"""Evaluate experience-evidence classification against holdout benchmark."""

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.modules.resume.evidence import (  # noqa: E402
    LABELS,
    baseline_predict,
)
from evaluate_experience_evidence import safe_divide  # noqa: E402

DATASET_PATH = ROOT / "eval_data" / "experience_evidence_holdout.json"
REPORT_PATH = ROOT / "eval_results" / "experience_evidence_holdout_report.json"


def main():
    with DATASET_PATH.open("r", encoding="utf-8-sig") as file:
        dataset = json.load(file)

    cases = dataset["cases"]
    confusion = {actual: Counter() for actual in LABELS}
    per_label = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})
    results = []
    correct = 0

    for case in cases:
        expected = case["expected_evidence"]
        predicted = baseline_predict(case["resume_text"], case["skill"])

        if expected not in LABELS:
            raise ValueError(
                f"Unknown expected label {expected!r} in {case['case_id']}"
            )

        if predicted not in LABELS:
            raise ValueError(
                f"Unknown predicted label {predicted!r} in {case['case_id']}"
            )

        confusion[expected][predicted] += 1
        passed = expected == predicted
        correct += int(passed)

        for label in LABELS:
            if predicted == label and expected == label:
                per_label[label]["tp"] += 1
            elif predicted == label and expected != label:
                per_label[label]["fp"] += 1
            elif expected == label and predicted != label:
                per_label[label]["fn"] += 1

        results.append({
            "case_id": case["case_id"],
            "skill": case["skill"],
            "expected": expected,
            "predicted": predicted,
            "passed": passed,
            "resume_text": case["resume_text"],
            "rationale": case.get("rationale", ""),
        })

    metrics = {}
    for label in LABELS:
        values = per_label[label]
        precision = safe_divide(values["tp"], values["tp"] + values["fp"])
        recall = safe_divide(values["tp"], values["tp"] + values["fn"])
        f1 = safe_divide(
            int(round(2 * precision * recall * 10000)),
            int(round((precision + recall) * 10000)),
        ) if precision + recall else 0.0

        metrics[label] = {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "support": sum(
                1 for case in cases if case["expected_evidence"] == label
            ),
        }

    accuracy = correct / len(cases) if cases else 0.0

    report = {
        "evaluation_id": dataset.get("evaluation_id"),
        "classifier": "rule_based_baseline_v2",
        "dataset_path": str(DATASET_PATH),
        "total_cases": len(cases),
        "correct": correct,
        "accuracy": round(accuracy, 4),
        "per_label_metrics": metrics,
        "confusion_matrix": {
            "labels": LABELS,
            "rows": {
                actual: {
                    predicted: confusion[actual][predicted]
                    for predicted in LABELS
                }
                for actual in LABELS
            },
        },
        "results": results,
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Evaluation: {dataset.get('evaluation_id', 'holdout')}")
    print(f"Cases evaluated: {len(cases)}")
    print(f"Correct: {correct}/{len(cases)}")
    print(f"Holdout accuracy: {accuracy:.2%}")

    print("\nPer-label metrics:")
    for label, values in metrics.items():
        print(
            f"{label}: precision={values['precision']:.2f}, "
            f"recall={values['recall']:.2f}, "
            f"F1={values['f1']:.2f}, "
            f"support={values['support']}"
        )

    print("\nConfusion matrix (rows=actual, columns=predicted):")
    print("actual\\predicted | " + " | ".join(LABELS))
    for actual in LABELS:
        values = [str(confusion[actual][predicted]) for predicted in LABELS]
        print(actual + " | " + " | ".join(values))

    print("\nPer-case results:")
    for result in results:
        status = "PASS" if result["passed"] else "FAIL"
        print(
            f"{status} {result['case_id']}: "
            f"expected={result['expected']}, "
            f"predicted={result['predicted']}"
        )

    print(f"\nDetailed report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
