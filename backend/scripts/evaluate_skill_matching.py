
"""Offline benchmark for resume skill extraction and requirement matching."""

import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.modules.resume.scoring import (  # noqa: E402
    calculate_match_against_skills,
    extract_skills,
    load_skill_taxonomy,
)

DATASET_PATH = BACKEND_DIR / "eval_data" / "skill_matching_cases.json"
OUTPUT_PATH = BACKEND_DIR / "eval_results" / "skill_matching_benchmark.json"


def normalize(values):
    return sorted({value.strip().lower() for value in values})


def evaluate_case(case, taxonomy):
    resume_text = case["resume_text"]
    required_skills = normalize(case["expected_required_skills"])

    # Metric 1: all skills detected in the resume.
    predicted_resume_skills = extract_skills(resume_text, taxonomy)

    # This field must contain ALL expected skills detected in the resume.
    # Until the dataset includes it, use the union of expected matched
    # and expected missing skills only as a temporary comparison set.
    expected_resume_skills = normalize(
        case.get("expected_resume_skills", case["expected_matched_skills"])
    )

    resume_skill_exact = (
        set(predicted_resume_skills) == set(expected_resume_skills)
    )

    # Metric 2: match resume skills against explicitly labeled requirements.
    result = calculate_match_against_skills(
        resume_text,
        required_skills,
        taxonomy,
    )

    expected_matched = normalize(case["expected_matched_skills"])
    expected_missing = normalize(case["expected_missing_skills"])

    predicted_matched = result["matched_skills"]
    predicted_missing = result["missing_skills"]

    matched_correct = set(predicted_matched) == set(expected_matched)
    missing_correct = set(predicted_missing) == set(expected_missing)

    return {
        "case_id": case["case_id"],
        "resume_skill_exact": resume_skill_exact,
        "predicted_resume_skills": predicted_resume_skills,
        "expected_resume_skills": expected_resume_skills,
        "resume_skill_false_positives": sorted(
            set(predicted_resume_skills) - set(expected_resume_skills)
        ),
        "resume_skill_false_negatives": sorted(
            set(expected_resume_skills) - set(predicted_resume_skills)
        ),
        "matched_correct": matched_correct,
        "missing_correct": missing_correct,
        "predicted_matched_skills": predicted_matched,
        "expected_matched_skills": expected_matched,
        "predicted_missing_skills": predicted_missing,
        "expected_missing_skills": expected_missing,
        "match_score": result["match_score"],
        "notes": case.get("notes", ""),
    }


def percentage(numerator, denominator):
    return round(numerator / denominator * 100, 2) if denominator else 0.0


def main():
    with DATASET_PATH.open("r", encoding="utf-8-sig") as file:
        dataset = json.load(file)

    taxonomy = load_skill_taxonomy()
    results = [evaluate_case(case, taxonomy) for case in dataset["cases"]]

    total = len(results)
    summary = {
        "dataset": DATASET_PATH.name,
        "cases_evaluated": total,
        "resume_skill_extraction_exact_accuracy": percentage(
            sum(row["resume_skill_exact"] for row in results), total
        ),
        "matched_skills_exact_accuracy": percentage(
            sum(row["matched_correct"] for row in results), total
        ),
        "missing_skills_exact_accuracy": percentage(
            sum(row["missing_correct"] for row in results), total
        ),
        "fully_correct_requirement_case_accuracy": percentage(
            sum(
                row["matched_correct"] and row["missing_correct"]
                for row in results
            ),
            total,
        ),
        "results": results,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2, ensure_ascii=False)

    print(f"Cases evaluated: {total}")
    print(
        "Resume skill extraction exact accuracy: "
        f"{summary['resume_skill_extraction_exact_accuracy']}%"
    )
    print(
        "Matched-skills exact accuracy: "
        f"{summary['matched_skills_exact_accuracy']}%"
    )
    print(
        "Missing-skills exact accuracy: "
        f"{summary['missing_skills_exact_accuracy']}%"
    )
    print(
        "Fully correct requirement case accuracy: "
        f"{summary['fully_correct_requirement_case_accuracy']}%"
    )

    print("\nPer-case results:")
    for row in results:
        status = (
            "PASS"
            if row["matched_correct"] and row["missing_correct"]
            else "FAIL"
        )
        print(
            f"{status} {row['case_id']}: "
            f"resume_skills={row['predicted_resume_skills']}, "
            f"matched={row['predicted_matched_skills']}, "
            f"missing={row['predicted_missing_skills']}"
        )

    print(f"\nDetailed report: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
