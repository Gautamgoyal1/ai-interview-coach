
import asyncio
import hashlib
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from app.integrations.llm.base import LLMError
from app.integrations.llm.factory import get_llm_provider
from app.modules.resume.feedback_quality_judge import FeedbackQualityJudge
from scripts.evaluate_resume_feedback_quality import (
    calculate_binary_metrics,
    validate_dataset,
)

BASE_DIR = Path(__file__).resolve().parent.parent

DATASET_PATH = Path(
    os.getenv(
        "RESUME_FEEDBACK_JUDGE_DATASET",
        str(BASE_DIR / "eval_data" / "resume_feedback_quality_cases.json"),
    )
)

OUTPUT_DIR = BASE_DIR / "eval_results"

OUTPUT_PATH = Path(
    os.getenv(
        "RESUME_FEEDBACK_JUDGE_OUTPUT",
        str(OUTPUT_DIR / "resume_feedback_quality_judge.json"),
    )
)

CHECKPOINT_PATH = Path(
    os.getenv(
        "RESUME_FEEDBACK_JUDGE_CHECKPOINT",
        str(OUTPUT_DIR / "resume_feedback_quality_judge.checkpoint.json"),
    )
)

DIMENSIONS = ("grounded", "relevant", "actionable")
logger = logging.getLogger(__name__)


def dataset_fingerprint(dataset: dict) -> str:
    """Return a stable SHA-256 fingerprint of the complete dataset."""
    canonical_json = json.dumps(
        dataset,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


def save_json_atomically(path: Path, data: dict) -> None:
    """Write JSON to a temporary file before replacing the destination."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(path.suffix + ".tmp")

    temporary_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    os.replace(temporary_path, path)


def load_checkpoint(
    dataset: dict,
    provider_name: str,
) -> dict[str, dict]:
    """Load predictions only when dataset and provider metadata match."""
    if not CHECKPOINT_PATH.exists():
        return {}

    checkpoint = json.loads(
        CHECKPOINT_PATH.read_text(encoding="utf-8")
    )

    expected_ids = [case["case_id"] for case in dataset["cases"]]
    fingerprint = dataset_fingerprint(dataset)

    if checkpoint.get("evaluation_id") != dataset.get("evaluation_id"):
        raise ValueError(
            "Checkpoint belongs to another evaluation. "
            "Preserve it and use a separate checkpoint path if needed."
        )

    if checkpoint.get("dataset_case_ids") != expected_ids:
        raise ValueError(
            "Benchmark case IDs or order changed. "
            "Preserve the checkpoint and resolve the dataset mismatch."
        )

    if checkpoint.get("dataset_sha256") != fingerprint:
        raise ValueError(
            "Checkpoint dataset fingerprint mismatch. The dataset content "
            "or metadata changed. Preserve the checkpoint and use a separate "
            "checkpoint path for the changed dataset."
        )

    if checkpoint.get("provider_name") != provider_name:
        raise ValueError(
            f"Checkpoint provider is {checkpoint.get('provider_name')!r}, "
            f"but the active provider is {provider_name!r}. "
            "Use the original provider or a separate checkpoint path."
        )

    results = checkpoint.get("results")

    if not isinstance(results, list):
        raise ValueError("Checkpoint results must be a list.")

    valid_ids = set(expected_ids)
    completed = {}

    for row in results:
        if (
            not isinstance(row, dict)
            or row.get("case_id") not in valid_ids
        ):
            raise ValueError(
                "Checkpoint contains an unknown or invalid case."
            )

        case_id = row["case_id"]

        if case_id in completed:
            raise ValueError(
                f"Duplicate checkpoint result: {case_id}"
            )

        if row.get("judge_provider") != provider_name:
            raise ValueError(
                f"Checkpoint provider mismatch for case {case_id}."
            )

        predicted = row.get("predicted")
        reasoning = row.get("reasoning")

        if (
            not isinstance(predicted, dict)
            or set(predicted) != set(DIMENSIONS)
        ):
            raise ValueError(
                f"Invalid predicted labels in checkpoint: {case_id}"
            )

        if any(
            type(predicted[key]) is not bool
            for key in DIMENSIONS
        ):
            raise ValueError(
                f"Non-Boolean predicted label in checkpoint: {case_id}"
            )

        if (
            not isinstance(reasoning, dict)
            or set(reasoning) != set(DIMENSIONS)
        ):
            raise ValueError(
                f"Invalid reasoning in checkpoint: {case_id}"
            )

        if any(
            not isinstance(reasoning[key], str)
            or not reasoning[key].strip()
            for key in DIMENSIONS
        ):
            raise ValueError(
                f"Invalid reasoning text in checkpoint: {case_id}"
            )

        expected = row.get("expected")
        current_case = next(
            case for case in dataset["cases"]
            if case["case_id"] == case_id
        )

        if expected != current_case["expected"]:
            raise ValueError(
                f"Reference labels differ for checkpoint case {case_id}."
            )

        completed[case_id] = row

    if checkpoint.get("completed_count") != len(completed):
        raise ValueError(
            "Checkpoint completed_count does not match its results."
        )

    return completed


def save_checkpoint(
    dataset: dict,
    results: dict[str, dict],
    provider_name: str,
) -> None:
    """Persist completed predictions after each successful API call."""
    ordered_results = [
        results[case["case_id"]]
        for case in dataset["cases"]
        if case["case_id"] in results
    ]

    save_json_atomically(
        CHECKPOINT_PATH,
        {
            "evaluation_id": dataset.get(
                "evaluation_id", "unspecified"
            ),
            "dataset_case_ids": [
                case["case_id"] for case in dataset["cases"]
            ],
            "dataset_sha256": dataset_fingerprint(dataset),
            "provider_name": provider_name,
            "updated_at_utc": datetime.now(timezone.utc).isoformat(),
            "completed_count": len(ordered_results),
            "results": ordered_results,
        },
    )


def build_report(
    dataset: dict,
    results: list[dict],
    provider_names: list[str],
) -> dict:
    """Calculate agreement metrics and identify the providers used."""
    metrics = {
        dimension: calculate_binary_metrics(
            [
                row["expected"][dimension]
                for row in results
            ],
            [
                row["predicted"][dimension]
                for row in results
            ],
        )
        for dimension in DIMENSIONS
    }

    return {
        "evaluation_id": dataset.get(
            "evaluation_id", "unspecified"
        ),
        "dataset_sha256": dataset_fingerprint(dataset),
        "evaluation_type": "llm_judge_agreement_with_human_labels",
        "judge_providers": provider_names,
        "case_count": len(results),
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "warning": (
            "Metrics measure agreement with the supplied reference labels, "
            "not objective model quality. LLM judgments can vary between "
            "runs. Human review of reference labels is required."
        ),
        "metrics": metrics,
        "results": results,
    }


async def run_evaluation() -> bool:
    with DATASET_PATH.open(encoding="utf-8") as file:
        dataset = json.load(file)

    validate_dataset(dataset)

    # Resolve the provider before loading provider-specific checkpoints.
    provider = get_llm_provider()

    # Validate the checkpoint before making any evaluation API calls.
    completed = load_checkpoint(dataset, provider.name)

    judge = FeedbackQualityJudge(llm=provider)
    total = len(dataset["cases"])

    print(f"Benchmark cases: {total}")
    print(f"Already completed: {len(completed)}")
    print(f"Active provider: {provider.name}")
    print(f"Dataset SHA-256: {dataset_fingerprint(dataset)}")
    print(f"Checkpoint: {CHECKPOINT_PATH}")

    for index, case in enumerate(dataset["cases"], start=1):
        case_id = case["case_id"]

        if case_id in completed:
            print(
                f"[{index}/{total}] {case_id} "
                "— already completed; skipping"
            )
            continue

        print(f"[{index}/{total}] {case_id}")

        try:
            prediction = await judge.evaluate(case)

        except LLMError as exc:
            logger.error(
                "Evaluation paused for %s: %s",
                case_id,
                exc,
            )
            print(
                f"\nEvaluation INCOMPLETE: "
                f"{len(completed)}/{total} cases saved."
            )
            print(f"Checkpoint preserved at: {CHECKPOINT_PATH}")
            print(
                "Resolve the provider issue, then rerun the same command."
            )
            return False

        except ValueError as exc:
            logger.error(
                "Invalid judge response for %s: %s",
                case_id,
                exc,
            )
            print(
                f"\nEvaluation paused: invalid judge response "
                f"for {case_id}."
            )
            print(
                f"Completed predictions preserved at: {CHECKPOINT_PATH}"
            )
            return False

        completed[case_id] = {
            "case_id": case_id,
            "expected": case["expected"],
            "predicted": {
                dimension: prediction[dimension]
                for dimension in DIMENSIONS
            },
            "reasoning": prediction["reasoning"],
            "judge_provider": provider.name,
        }

        # Save immediately to protect completed predictions from later errors.
        save_checkpoint(dataset, completed, provider.name)
        print(f"Saved checkpoint: {len(completed)}/{total}")

    ordered_results = [
        completed[case["case_id"]]
        for case in dataset["cases"]
    ]

    provider_names = sorted({
        row["judge_provider"]
        for row in ordered_results
    })

    if provider_names != [provider.name]:
        raise ValueError(
            "The completed results do not all belong to the active provider."
        )

    report = build_report(
        dataset,
        ordered_results,
        provider_names,
    )

    save_json_atomically(OUTPUT_PATH, report)

    print("\nJudge agreement metrics:")
    print(json.dumps(report["metrics"], indent=2))
    print(f"\nProviders represented: {', '.join(provider_names)}")
    print(f"Complete report saved to: {OUTPUT_PATH}")
    print(f"Checkpoint retained at: {CHECKPOINT_PATH}")

    return True


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    try:
        success = asyncio.run(run_evaluation())
    except (ValueError, json.JSONDecodeError) as exc:
        logger.error("Evaluation could not start: %s", exc)
        sys.exit(2)

    sys.exit(0 if success else 2)
