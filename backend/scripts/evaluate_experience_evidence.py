"""Evaluate experience-evidence classification against manual labels.

Rule-based baseline v6.

Important:
- Classifies evidence for one target skill.
- Separates practical evidence, learning evidence, negation,
  and third-party attribution.
- This is a heuristic baseline, not a production NLP classifier.
"""

import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.modules.resume.evidence import (  # noqa: E402
    LABELS,
    baseline_predict,
)

DATASET_PATH = (
    BACKEND_DIR / "eval_data" / "experience_evidence_cases.json"
)
OUTPUT_PATH = (
    BACKEND_DIR / "eval_results" / "experience_evidence_benchmark.json"
)


def safe_divide(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def main():
    with DATASET_PATH.open("r", encoding="utf-8-sig") as file:
        dataset = json.load(file)

    confusion = {
        actual: {predicted: 0 for predicted in LABELS}
        for actual in LABELS
    }
    results = []

    for case in dataset["cases"]:
        actual = case["expected_evidence"]

        if actual not in LABELS:
            raise ValueError(
                f"Unknown label {actual!r} in {case['case_id']}"
            )

        predicted = baseline_predict(case["resume_text"], case["skill"])

        if predicted not in LABELS:
            raise ValueError(
                f"Invalid prediction {predicted!r} for {case['case_id']}"
            )

        confusion[actual][predicted] += 1

        results.append({
            "case_id": case["case_id"],
            "skill": case["skill"],
            "expected": actual,
            "predicted": predicted,
            "correct": actual == predicted,
            "rationale": case.get("rationale", ""),
            "resume_text": case["resume_text"],
        })

    total = len(results)
    correct = sum(row["correct"] for row in results)
    per_label = {}

    for label in LABELS:
        true_positive = confusion[label][label]
        predicted_count = sum(
            confusion[actual][label] for actual in LABELS
        )
        actual_count = sum(confusion[label].values())

        precision = safe_divide(true_positive, predicted_count)
        recall = safe_divide(true_positive, actual_count)
        f1 = safe_divide(
            2 * precision * recall,
            precision + recall,
        )

        per_label[label] = {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "support": actual_count,
        }

    report = {
        "dataset": DATASET_PATH.name,
        "classifier": "rule_based_baseline_v6",
        "cases_evaluated": total,
        "accuracy": round(safe_divide(correct, total), 4),
        "per_label": per_label,
        "confusion_matrix": confusion,
        "results": results,
        "limitations": [
            "This is a rule-based baseline, not a validated NLP classifier.",
            "The dataset is small and manually labeled.",
            "Rules may still misclassify complex negation and attribution.",
            "One label cannot fully represent both learning status and experience evidence.",
            "Passing these cases does not establish production accuracy.",
        ],
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)

    print(f"Cases evaluated: {total}")
    print(f"Baseline accuracy: {report['accuracy'] * 100:.2f}%")

    print("\nPer-label metrics:")
    for label, metrics in per_label.items():
        print(
            f"{label}: precision={metrics['precision']:.2f}, "
            f"recall={metrics['recall']:.2f}, "
            f"F1={metrics['f1']:.2f}, "
            f"support={metrics['support']}"
        )

    print("\nConfusion matrix (rows=actual, columns=predicted):")
    print("actual\\predicted | " + " | ".join(LABELS))

    for actual in LABELS:
        counts = " | ".join(
            str(confusion[actual][predicted])
            for predicted in LABELS
        )
        print(f"{actual} | {counts}")

    print("\nPer-case results:")
    for row in results:
        status = "PASS" if row["correct"] else "FAIL"
        print(
            f"{status} {row['case_id']}: "
            f"expected={row['expected']}, "
            f"predicted={row['predicted']}"
        )

    print(f"\nDetailed report: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
