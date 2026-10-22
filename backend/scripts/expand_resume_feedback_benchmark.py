
import json
from collections import Counter
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "eval_data"
SOURCE = DATA_DIR / "resume_feedback_quality_cases.json"

LABEL_DEFINITIONS = {
    "grounded": (
        "The item does not present unsupported candidate-specific "
        "facts as true."
    ),
    "relevant": (
        "The item meaningfully relates to the target role, supplied "
        "resume, or goal of improving the resume for that role."
    ),
    "actionable": (
        "The item provides a concrete question or practical next step, "
        "where applicable."
    ),
}


def make_case(case_id, section, resume_text, job_role, feedback_item,
              grounded, relevant, actionable, notes):
    return {
        "case_id": case_id,
        "section": section,
        "resume_text": resume_text,
        "job_role": job_role,
        "feedback_item": feedback_item,
        "expected": {
            "grounded": grounded,
            "relevant": relevant,
            "actionable": actionable,
        },
        "notes": notes,
    }


# These are proposed labels. Review the rationales before treating
# the cases as an independently human-validated benchmark.
NEW_CASES = [
    make_case(
        "conditional_cloud_recommendation", "improvement_suggestions",
        "Skills: Python, SQL. No cloud deployment is documented.",
        "Junior Machine Learning Engineer",
        "If you have deployed a model, describe the cloud service and "
        "your contribution; otherwise, consider a small deployment project.",
        True, True, True,
        "Conditional advice does not claim deployment experience."
    ),
    make_case(
        "fabricated_cloud_deployment", "strengths",
        "Skills: Python, SQL. No deployment experience is documented.",
        "Junior Machine Learning Engineer",
        "Your Azure deployment experience demonstrates production readiness.",
        False, True, False,
        "The feedback asserts undocumented Azure deployment experience."
    ),
    make_case(
        "unsupported_team_leadership", "strengths",
        "Built a classification model independently using Python.",
        "Junior Machine Learning Engineer",
        "You successfully led a team of five engineers.",
        False, True, False,
        "Team leadership and team size are unsupported."
    ),
    make_case(
        "safe_teamwork_question", "likely_interview_questions",
        "Built a classification model independently using Python.",
        "Junior Machine Learning Engineer",
        "How would you collaborate with a team when developing a model?",
        True, True, True,
        "This is a general knowledge question, not a claim about past teamwork."
    ),
    make_case(
        "fabricated_dataset_size", "strengths",
        "Trained a model on a customer dataset; dataset size is not stated.",
        "Data Scientist",
        "You processed over one million customer records.",
        False, True, False,
        "The record count is invented."
    ),
    make_case(
        "recommend_document_dataset_size", "improvement_suggestions",
        "Trained a model on a customer dataset; dataset size is not stated.",
        "Data Scientist",
        "If available, document the dataset size and how you validated it.",
        True, True, True,
        "This requests verifiable information without inventing a number."
    ),
    make_case(
        "unsupported_accuracy_improvement", "strengths",
        "Built a model. No baseline or comparison is documented.",
        "Machine Learning Engineer",
        "You improved prediction accuracy by 25 percent over the baseline.",
        False, True, False,
        "Both the percentage and comparison are unsupported."
    ),
    make_case(
        "safe_comparison_recommendation", "improvement_suggestions",
        "Built a model. No baseline or comparison is documented.",
        "Machine Learning Engineer",
        "If you compared against a baseline, report the measured improvement "
        "and explain how the comparison was performed.",
        True, True, True,
        "Conditional request for evidence is grounded and actionable."
    ),
    make_case(
        "irrelevant_cooking_advice", "improvement_suggestions",
        "Python, SQL, Pandas; built a churn prediction project.",
        "Junior Data Analyst",
        "Add a section describing your favorite cooking recipes.",
        True, False, True,
        "The instruction is concrete but unrelated to the resume goal."
    ),
    make_case(
        "irrelevant_travel_advice", "improvement_suggestions",
        "Python, SQL, Pandas; built a churn prediction project.",
        "Junior Data Analyst",
        "Describe your ideal international holiday destination.",
        True, False, True,
        "Travel preferences have no stated connection to this role."
    ),
    make_case(
        "irrelevant_graphic_design_claim", "strengths",
        "Python, SQL, Pandas; built a churn prediction project.",
        "Junior Data Analyst",
        "Your advanced graphic design portfolio is a major strength.",
        False, False, False,
        "The portfolio is invented and unrelated to the target role."
    ),
    make_case(
        "irrelevant_music_recommendation", "improvement_suggestions",
        "Python, SQL, Pandas; built a churn prediction project.",
        "Junior Data Analyst",
        "Add a list of your favorite musicians to make the resume stronger.",
        True, False, True,
        "The suggestion is actionable but irrelevant."
    ),
    make_case(
        "vague_interview_preparation", "improvement_suggestions",
        "Python, SQL, and a basic regression project.",
        "Junior Data Scientist",
        "Prepare better for interviews.",
        True, True, False,
        "Relevant to the job search but gives no concrete step."
    ),
    make_case(
        "specific_sql_next_step", "improvement_suggestions",
        "SQL is listed; no SQL project is described.",
        "Junior Data Analyst",
        "Add one SQL project showing joins, aggregation, and the question "
        "your analysis answered.",
        True, True, True,
        "Provides a concrete and role-relevant next step."
    ),
    make_case(
        "unsupported_sql_expertise", "strengths",
        "SQL is listed; no query examples are provided.",
        "Junior Data Analyst",
        "Your expert-level SQL optimization skills set you apart.",
        False, True, False,
        "Expertise and optimization experience are not established."
    ),
    make_case(
        "safe_sql_skill_question", "likely_interview_questions",
        "SQL is listed; no query examples are provided.",
        "Junior Data Analyst",
        "How would you investigate a slow SQL query?",
        True, True, True,
        "A general technical question does not assert prior experience."
    ),
    make_case(
        "unsupported_deep_learning_project", "strengths",
        "Built a house price model using scikit-learn.",
        "Junior Machine Learning Engineer",
        "Your deep learning project demonstrates CNN expertise.",
        False, True, False,
        "Neither a deep learning project nor CNN expertise is documented."
    ),
    make_case(
        "safe_deep_learning_learning_plan", "improvement_suggestions",
        "Built a house price model using scikit-learn.",
        "Junior Machine Learning Engineer",
        "If deep learning is relevant to your target roles, build a small "
        "CNN project and document your evaluation results.",
        True, True, True,
        "A future learning recommendation does not claim existing experience."
    ),
    make_case(
        "unsupported_certification", "strengths",
        "Python and SQL skills are listed. No certifications are mentioned.",
        "Junior Data Analyst",
        "Your Azure Data Scientist certification validates your cloud skills.",
        False, True, False,
        "The certification is not supported by the supplied resume."
    ),
    make_case(
        "safe_certification_suggestion", "improvement_suggestions",
        "Python and SQL skills are listed. No certifications are mentioned.",
        "Junior Data Analyst",
        "If you hold relevant certifications, list their exact names; "
        "otherwise, leave this section out.",
        True, True, True,
        "Conditional advice does not assert certification ownership."
    ),
    make_case(
        "irrelevant_medical_advice", "improvement_suggestions",
        "Python, SQL, and a sales dashboard project.",
        "Business Data Analyst",
        "Add a detailed account of your personal medical history.",
        True, False, True,
        "The advice is actionable but unrelated and unnecessarily personal."
    ),
    make_case(
        "unsupported_revenue_impact", "strengths",
        "Created a sales dashboard. No business impact is quantified.",
        "Business Data Analyst",
        "Your dashboard increased company revenue by 18 percent.",
        False, True, False,
        "The business outcome and percentage are unsupported."
    ),
    make_case(
        "safe_impact_measurement", "improvement_suggestions",
        "Created a sales dashboard. No business impact is quantified.",
        "Business Data Analyst",
        "If you measured business impact, report the verified result and "
        "how it was calculated; otherwise, describe the dashboard's purpose.",
        True, True, True,
        "Requests evidence without inventing an impact figure."
    ),
    make_case(
        "unsupported_model_ownership", "strengths",
        "Contributed data cleaning to a group classification project.",
        "Junior Machine Learning Engineer",
        "You designed and owned the complete model architecture.",
        False, True, False,
        "The resume only establishes a data-cleaning contribution."
    ),
    make_case(
        "safe_contribution_clarification", "improvement_suggestions",
        "Contributed data cleaning to a group classification project.",
        "Junior Machine Learning Engineer",
        "Clarify which components you personally implemented and which "
        "were completed by other team members.",
        True, True, True,
        "Requests an accurate description of personal contribution."
    ),
    make_case(
        "irrelevant_finance_advice", "improvement_suggestions",
        "Python, Pandas, and a data visualization project.",
        "Junior Data Analyst",
        "Include your personal stock portfolio and investment returns.",
        True, False, True,
        "Personal investment returns are not relevant to the stated application."
    ),
    make_case(
        "vague_project_description", "improvement_suggestions",
        "Built a Python project; purpose and results are not described.",
        "Junior Data Analyst",
        "Make your project description stronger.",
        True, True, False,
        "The feedback is relevant but lacks a specific next step."
    ),
    make_case(
        "concrete_project_documentation", "improvement_suggestions",
        "Built a Python project; purpose and results are not described.",
        "Junior Data Analyst",
        "Add the project's objective, data source, your contribution, and "
        "one verified result.",
        True, True, True,
        "Specifies the information to document without inventing results."
    ),
    make_case(
        "unsupported_production_scale", "strengths",
        "Built a REST API for a class project. No traffic data is stated.",
        "Backend Engineer",
        "Your API reliably handles 100,000 requests per second.",
        False, True, False,
        "The throughput and reliability claim are unsupported."
    ),
    make_case(
        "safe_load_testing_recommendation", "improvement_suggestions",
        "Built a REST API for a class project. No traffic data is stated.",
        "Backend Engineer",
        "Run a load test, record the setup and observed throughput, and "
        "report the measured result without extrapolating beyond the test.",
        True, True, True,
        "Concrete recommendation that does not assert a measured result."
    ),
]


def validate_case(case):
    assert set(case) == {
        "case_id", "section", "resume_text", "job_role",
        "feedback_item", "expected", "notes",
    }, case.get("case_id")

    assert set(case["expected"]) == {
        "grounded", "relevant", "actionable",
    }, case["case_id"]

    assert all(
        type(value) is bool for value in case["expected"].values()
    ), case["case_id"]


def main():
    original = json.loads(SOURCE.read_text(encoding="utf-8"))
    existing = original["cases"]

    all_cases = existing + NEW_CASES
    ids = [case["case_id"] for case in all_cases]

    if len(ids) != len(set(ids)):
        duplicates = [
            key for key, count in Counter(ids).items() if count > 1
        ]
        raise ValueError(f"Duplicate case IDs: {duplicates}")

    for case in all_cases:
        validate_case(case)

    # Keep the original 20 in development because they informed prompt tuning.
    # The newly authored 30 cases are held out from prompt tuning for now.
    # Before reporting test metrics, independently review their labels and
    # freeze the prompt and evaluation procedure.
    development = existing + NEW_CASES[:10]
    test = NEW_CASES[10:]

    assert len(all_cases) == 50
    assert len(development) == 30
    assert len(test) == 20
    assert not ({c["case_id"] for c in development} &
                {c["case_id"] for c in test})

    expanded = {
        **original,
        "evaluation_id": "resume_feedback_quality_v2",
        "label_definitions": LABEL_DEFINITIONS,
        "cases": all_cases,
    }

    dev_data = {
        **expanded,
        "evaluation_id": "resume_feedback_quality_dev_v1",
        "cases": development,
    }

    test_data = {
        **expanded,
        "evaluation_id": "resume_feedback_quality_test_v1",
        "cases": test,
    }

    outputs = {
        DATA_DIR / "resume_feedback_quality_cases_v2.json": expanded,
        DATA_DIR / "resume_feedback_quality_dev.json": dev_data,
        DATA_DIR / "resume_feedback_quality_test.json": test_data,
    }

    for path, payload in outputs.items():
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"Created {path}: {len(payload['cases'])} cases")

    print("\nLABEL DISTRIBUTION: FULL DATASET")
    for label in ("grounded", "relevant", "actionable"):
        counts = Counter(c["expected"][label] for c in all_cases)
        print(f"{label}: True={counts[True]}, False={counts[False]}")

    print("\nIMPORTANT: These proposed labels require human review.")
    print("Do not treat test scores as validated until labels are reviewed.")


if __name__ == "__main__":
    main()
