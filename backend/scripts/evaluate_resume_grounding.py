"""Evaluate the resume grounding dataset and validate its labels."""

import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_PATH = BASE_DIR / "eval_data" / "resume_grounding_cases.json"


def main():
    with DATASET_PATH.open(encoding="utf-8") as file:
        cases = json.load(file)

    if not isinstance(cases, list) or not cases:
        raise ValueError("Evaluation dataset must be a non-empty JSON list.")

    case_ids = set()

    for case in cases:
        required = {
            "case_id",
            "category",
            "resume_text",
            "claim_to_evaluate",
            "expected_supported",
        }

        if not isinstance(case, dict) or not required.issubset(case):
            raise ValueError(f"Invalid evaluation case: {case}")

        if case["case_id"] in case_ids:
            raise ValueError(f"Duplicate case ID: {case['case_id']}")

        if not isinstance(case["expected_supported"], bool):
            raise ValueError(
                f"Expected a boolean label for {case['case_id']}"
            )

        case_ids.add(case["case_id"])

    supported = sum(
        case["expected_supported"] for case in cases
    )
    unsupported = len(cases) - supported

    print("Resume grounding evaluation dataset")
    print("-----------------------------------")
    print(f"Cases validated: {len(cases)}")
    print(f"Supported claims: {supported}")
    print(f"Unsupported claims: {unsupported}")
    print("\nCases by category:")

    categories = sorted({case["category"] for case in cases})
    for category in categories:
        count = sum(case["category"] == category for case in cases)
        print(f"  {category}: {count}")

    print("\nDataset validation passed.")
    print(
        "Note: this validates dataset structure and labels, "
        "not Gemini's grounding accuracy."
    )


if __name__ == "__main__":
    main()
