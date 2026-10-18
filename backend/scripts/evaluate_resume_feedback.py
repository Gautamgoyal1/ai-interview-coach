
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.modules.resume.feedback_evaluator import evaluate_feedback


def main():
    base = Path(__file__).resolve().parent.parent

    baseline_path = (
        base / "eval_results" / "resume_grounding_baseline.json"
    )
    expectations_path = (
        base / "eval_data" / "resume_feedback_expectations.json"
    )
    output_path = (
        base / "eval_results" / "resume_feedback_evaluation.json"
    )

    if not baseline_path.exists():
        raise FileNotFoundError(
            f"Baseline report not found: {baseline_path}\n"
            "Run scripts/run_resume_grounding_eval.py first."
        )

    if not expectations_path.exists():
        raise FileNotFoundError(
            f"Expectations file not found: {expectations_path}"
        )

    baseline = json.loads(
        baseline_path.read_text(encoding="utf-8")
    )
    expectations = json.loads(
        expectations_path.read_text(encoding="utf-8")
    )

    feedback_sections = (
        "strengths",
        "improvement_suggestions",
        "likely_interview_questions",
    )

    missing_sections = [
        section
        for section in feedback_sections
        if section not in baseline
    ]

    if missing_sections:
        raise ValueError(
            "Baseline is missing feedback sections: "
            + ", ".join(missing_sections)
        )

    feedback = {
        section: baseline[section]
        for section in feedback_sections
    }

    evaluation = evaluate_feedback(feedback, expectations)

    report = {
        "evaluation_id": evaluation["evaluation_id"],
        "baseline_file": baseline_path.name,
        "expectations_file": expectations_path.name,
        "evaluation_method": "deterministic_heuristics",
        "limitations": [
            "Potential unsupported claims are review warnings, "
            "not proof of factual errors.",
            "This evaluation does not measure semantic correctness "
            "or overall feedback quality.",
        ],
        "structure_checks_passed": evaluation[
            "structure_checks_passed"
        ],
        "issue_count": evaluation["issue_count"],
        "issues": evaluation["issues"],
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\nEvaluation report saved to: {output_path}")


if __name__ == "__main__":
    main()
