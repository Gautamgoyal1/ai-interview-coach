
"""Run the LLM judge against the human-labeled feedback benchmark."""

import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from app.integrations.llm.base import LLMError
from app.modules.resume.feedback_quality_judge import FeedbackQualityJudge
from scripts.evaluate_resume_feedback_quality import (
    calculate_binary_metrics,
    validate_dataset,
)


BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_PATH = BASE_DIR / "eval_data" / "resume_feedback_quality_cases.json"
OUTPUT_DIR = BASE_DIR / "eval_results"

DIMENSIONS = ("grounded", "relevant", "actionable")
logger = logging.getLogger(__name__)


async def run_evaluation():
    with DATASET_PATH.open(encoding="utf-8") as file:
        dataset = json.load(file)

    validate_dataset(dataset)

    judge = FeedbackQualityJudge()
    results = []

    for index, case in enumerate(dataset["cases"], start=1):
        print(f"[{index}/{len(dataset['cases'])}] {case['case_id']}")

        try:
            prediction = await judge.evaluate(case)
        except (LLMError, ValueError) as exc:
            logger.exception("Evaluation failed for %s", case["case_id"])
            raise RuntimeError(
                f"Could not evaluate case '{case['case_id']}': {exc}"
            ) from exc

        results.append({
            "case_id": case["case_id"],
            "expected": case["expected"],
            "predicted": {
                dimension: prediction[dimension]
                for dimension in DIMENSIONS
            },
            "reasoning": prediction["reasoning"],
        })

    metrics = {
        dimension: calculate_binary_metrics(
            [row["expected"][dimension] for row in results],
            [row["predicted"][dimension] for row in results],
        )
        for dimension in DIMENSIONS
    }

    report = {
        "evaluation_id": dataset.get("evaluation_id", "unspecified"),
        "evaluation_type": "llm_judge_agreement_with_human_labels",
        "judge_provider": "configured GeminiProvider",
        "case_count": len(results),
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "warning": (
            "Metrics measure agreement with the supplied reference labels. "
            "They do not establish objective model quality. Results may vary "
            "between runs because LLM judgments can vary."
        ),
        "metrics": metrics,
        "results": results,
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "resume_feedback_quality_judge.json"
    output_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("\nJudge agreement metrics:")
    print(json.dumps(metrics, indent=2))
    print(f"\nReport saved to: {output_path}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_evaluation())
