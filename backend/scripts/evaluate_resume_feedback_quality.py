
"""Evaluate human-labeled resume feedback quality cases offline."""

import json
from collections import defaultdict
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_PATH = BASE_DIR / "eval_data" / "resume_feedback_quality_cases.json"
OUTPUT_DIR = BASE_DIR / "eval_results"

DIMENSIONS = ("grounded", "relevant", "actionable")
VALID_SECTIONS = {
    "strengths",
    "improvement_suggestions",
    "likely_interview_questions",
}


def validate_dataset(dataset):
    """Validate benchmark structure and human-defined labels."""
    if not isinstance(dataset, dict):
        raise ValueError("Dataset must be a JSON object.")

    cases = dataset.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("Dataset must contain a non-empty cases list.")

    seen_ids = set()

    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("Every case must be a JSON object.")

        required = {
            "case_id",
            "section",
            "resume_text",
            "job_role",
            "feedback_item",
            "expected",
            "notes",
        }
        if not required.issubset(case):
            raise ValueError(
                f"Case is missing fields: {case.get('case_id', '<unknown>')}"
            )

        case_id = case["case_id"]
        if not isinstance(case_id, str) or not case_id.strip():
            raise ValueError("Every case must have a non-empty case_id.")

        if case_id in seen_ids:
            raise ValueError(f"Duplicate case_id: {case_id}")
        seen_ids.add(case_id)

        for field in ("resume_text", "job_role", "feedback_item", "section"):
            if not isinstance(case[field], str) or not case[field].strip():
                raise ValueError(f"{field} must be non-empty in {case_id}")

        if case["section"] not in VALID_SECTIONS:
            raise ValueError(f"Invalid section in {case_id}: {case['section']}")

        expected = case["expected"]
        if not isinstance(expected, dict) or set(expected) != set(DIMENSIONS):
            raise ValueError(
                f"Expected labels must contain exactly {DIMENSIONS} in {case_id}"
            )

        if any(type(expected[key]) is not bool for key in DIMENSIONS):
            raise ValueError(f"Labels must be booleans in {case_id}")

        if not isinstance(case["notes"], str):
            raise ValueError(f"notes must be a string in {case_id}")


def calculate_binary_metrics(expected, predicted):
    """Calculate binary-classification metrics with explicit undefined values."""
    if len(expected) != len(predicted):
        raise ValueError("Expected and predicted labels must have equal length.")

    if any(type(value) is not bool for value in expected + predicted):
        raise ValueError("All labels must be booleans.")

    tp = sum(e and p for e, p in zip(expected, predicted))
    tn = sum(not e and not p for e, p in zip(expected, predicted))
    fp = sum(not e and p for e, p in zip(expected, predicted))
    fn = sum(e and not p for e, p in zip(expected, predicted))

    def ratio(numerator, denominator):
        return round(numerator / denominator, 4) if denominator else None

    precision = ratio(tp, tp + fp)
    recall = ratio(tp, tp + fn)

    if precision is None or recall is None:
        f1 = 0.0 if precision == 0 or recall == 0 else None
    elif precision + recall == 0:
        f1 = 0.0
    else:
        f1 = round(2 * precision * recall / (precision + recall), 4)

    return {
        "total": len(expected),
        "correct": tp + tn,
        "accuracy": ratio(tp + tn, len(expected)),
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "confusion_matrix": {
            "true_positive": tp,
            "true_negative": tn,
            "false_positive": fp,
            "false_negative": fn,
        },
    }


def summarize_labels(cases):
    """Summarize the distribution of reference labels, not model performance."""
    summary = {}

    for dimension in DIMENSIONS:
        positives = sum(case["expected"][dimension] for case in cases)
        total = len(cases)
        summary[dimension] = {
            "true_count": positives,
            "false_count": total - positives,
        }

    return summary


def main():
    with DATASET_PATH.open(encoding="utf-8") as file:
        dataset = json.load(file)

    validate_dataset(dataset)
    cases = dataset["cases"]

    report = {
        "evaluation_id": dataset.get("evaluation_id", "unspecified"),
        "evaluation_type": "human_labeled_feedback_quality_benchmark",
        "case_count": len(cases),
        "method": "reference_label_audit_only",
        "warning": (
            "This script validates human-defined labels and summarizes their "
            "distribution. It does not evaluate generated model feedback, "
            "so its results are not model-quality metrics."
        ),
        "label_distribution": summarize_labels(cases),
        "cases": cases,
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "resume_feedback_quality_benchmark.json"
    output_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Evaluation dataset validated: {len(cases)} cases")
    print("Reference label distribution:")
    print(json.dumps(report["label_distribution"], indent=2))
    print(f"Benchmark report saved to: {output_path}")


if __name__ == "__main__":
    main()
