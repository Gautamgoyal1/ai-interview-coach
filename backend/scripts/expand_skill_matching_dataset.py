
"""Expand the offline skill-matching benchmark to 30 cases."""

import json
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
DATASET_PATH = BACKEND_DIR / "eval_data" / "skill_matching_cases.json"

# Each case specifies expected canonical skills mentioned in the resume
# and the manually labeled mandatory skills for the job.
NEW_CASES = [
    {
        "case_id": "SM009",
        "resume_text": "I have never used Docker, but I write Python scripts.",
        "job_description": "Docker is required. Python is required.",
        "required_skills": ["docker", "python"],
        "expected_resume_skills": ["docker", "python"],
        "notes": "Negation: keyword extraction detects Docker despite lack of experience."
    },
    {
        "case_id": "SM010",
        "resume_text": "No Python experience. Familiar with SQL.",
        "job_description": "Python and SQL are required.",
        "required_skills": ["python", "sql"],
        "expected_resume_skills": ["python", "sql"],
        "notes": "Negated Python mention; tests lexical detection, not proficiency."
    },
    {
        "case_id": "SM011",
        "resume_text": "Used Python3 to automate a report.",
        "job_description": "Python is required.",
        "required_skills": ["python"],
        "expected_resume_skills": ["python"],
        "notes": "Python3 alias."
    },
    {
        "case_id": "SM012",
        "resume_text": "Created queries using structured query language.",
        "job_description": "SQL is required.",
        "required_skills": ["sql"],
        "expected_resume_skills": ["sql"],
        "notes": "SQL long-form alias."
    },
    {
        "case_id": "SM013",
        "resume_text": "Trained ML models for classification.",
        "job_description": "Machine learning is required.",
        "required_skills": ["machine learning"],
        "expected_resume_skills": ["machine learning"],
        "notes": "ML alias."
    },
    {
        "case_id": "SM014",
        "resume_text": "Built a model using sklearn.",
        "job_description": "Scikit-learn is required.",
        "required_skills": ["scikit-learn"],
        "expected_resume_skills": ["scikit-learn"],
        "notes": "scikit-learn alias."
    },
    {
        "case_id": "SM015",
        "resume_text": "Cleaned raw records during preprocessing.",
        "job_description": "Data preprocessing is required.",
        "required_skills": ["data preprocessing"],
        "expected_resume_skills": ["data preprocessing"],
        "notes": "Preprocessing alias."
    },
    {
        "case_id": "SM016",
        "resume_text": "Evaluated the model on a held-out dataset.",
        "job_description": "Model evaluation is required.",
        "required_skills": ["model evaluation"],
        "expected_resume_skills": ["model evaluation"],
        "notes": "Model-evaluation alias."
    },
    {
        "case_id": "SM017",
        "resume_text": "Used containers to package an application.",
        "job_description": "Docker is required.",
        "required_skills": ["docker"],
        "expected_resume_skills": ["docker"],
        "notes": "Container alias."
    },
    {
        "case_id": "SM018",
        "resume_text": "Worked with a cloud platform for deployment.",
        "job_description": "Cloud platforms are required.",
        "required_skills": ["cloud platforms"],
        "expected_resume_skills": ["cloud platforms"],
        "notes": "Cloud-platform alias."
    },
    {
        "case_id": "SM019",
        "resume_text": "Python, Python3 and Python were used in multiple projects.",
        "job_description": "Python is required.",
        "required_skills": ["python"],
        "expected_resume_skills": ["python"],
        "notes": "Repeated mentions should produce one canonical skill."
    },
    {
        "case_id": "SM020",
        "resume_text": "",
        "job_description": "Python and SQL are required.",
        "required_skills": ["python", "sql"],
        "expected_resume_skills": [],
        "notes": "Empty resume."
    },
    {
        "case_id": "SM021",
        "resume_text": "Built a Java application and learned Kubernetes.",
        "job_description": "Python and Docker are required.",
        "required_skills": ["python", "docker"],
        "expected_resume_skills": [],
        "notes": "Technologies absent from the current canonical taxonomy."
    },
    {
        "case_id": "SM022",
        "resume_text": "I want to learn Python and Docker next year.",
        "job_description": "Python and Docker are required.",
        "required_skills": ["python", "docker"],
        "expected_resume_skills": ["python", "docker"],
        "notes": "Learning goals are detected like experience by keyword matching."
    },
    {
        "case_id": "SM023",
        "resume_text": "Read about pandas but have not used it in a project.",
        "job_description": "Pandas is required.",
        "required_skills": ["pandas"],
        "expected_resume_skills": ["pandas"],
        "notes": "Mention does not establish hands-on proficiency."
    },
    {
        "case_id": "SM024",
        "resume_text": "Used NumPy arrays for numerical operations.",
        "job_description": "NumPy is required.",
        "required_skills": ["numpy"],
        "expected_resume_skills": ["numpy"],
        "notes": "NumPy extraction."
    },
    {
        "case_id": "SM025",
        "resume_text": "Worked with pandas and NumPy.",
        "job_description": "Pandas is required. NumPy is preferred.",
        "required_skills": ["pandas"],
        "expected_resume_skills": ["pandas", "numpy"],
        "notes": "Only pandas is mandatory; both skills appear in the resume."
    },
    {
        "case_id": "SM026",
        "resume_text": "Built a small Docker deployment.",
        "job_description": "Docker is preferred but Python is required.",
        "required_skills": ["python"],
        "expected_resume_skills": ["docker"],
        "notes": "Preferred Docker is present; required Python is missing."
    },
    {
        "case_id": "SM027",
        "resume_text": "Python is listed in a course I plan to take.",
        "job_description": "Python is required.",
        "required_skills": ["python"],
        "expected_resume_skills": ["python"],
        "notes": "Course mention does not prove practical experience."
    },
    {
        "case_id": "SM028",
        "resume_text": "My teammate used Docker; I worked on the documentation.",
        "job_description": "Docker is required.",
        "required_skills": ["docker"],
        "expected_resume_skills": ["docker"],
        "notes": "Third-party mention can cause a false proficiency inference."
    },
    {
        "case_id": "SM029",
        "resume_text": "Used scikit learn and machine-learning techniques.",
        "job_description": "Scikit-learn and machine learning are required.",
        "required_skills": ["scikit-learn", "machine learning"],
        "expected_resume_skills": ["scikit-learn", "machine learning"],
        "notes": "Alternate spellings and aliases."
    },
    {
        "case_id": "SM030",
        "resume_text": "Used Python and SQL.",
        "job_description": "No mandatory technical skills.",
        "required_skills": [],
        "expected_resume_skills": ["python", "sql"],
        "notes": "Empty required-skill set."
    }
]


def normalize(values):
    return sorted({value.strip().lower() for value in values})


def main():
    with DATASET_PATH.open("r", encoding="utf-8-sig") as file:
        dataset = json.load(file)

    existing = {case["case_id"]: case for case in dataset["cases"]}

    for item in NEW_CASES:
        case_id = item["case_id"]

        if case_id in existing:
            continue

        required = normalize(item["required_skills"])
        resume_skills = normalize(item["expected_resume_skills"])

        # Expected matching labels are derived consistently from the
        # manually labeled resume skills and required-skill list.
        item["required_skills"] = required
        item["expected_resume_skills"] = resume_skills
        item["expected_required_skills"] = required
        item["expected_matched_skills"] = sorted(
            set(required) & set(resume_skills)
        )
        item["expected_missing_skills"] = sorted(
            set(required) - set(resume_skills)
        )

        existing[case_id] = item

    dataset["evaluation_id"] = "skill_matching_v3"
    dataset["description"] = (
        "Offline benchmark for skill extraction and explicitly labeled "
        "required-skill matching. Keyword mentions do not prove proficiency."
    )
    dataset["cases"] = sorted(
        existing.values(), key=lambda case: case["case_id"]
    )

    with DATASET_PATH.open("w", encoding="utf-8") as file:
        json.dump(dataset, file, indent=2, ensure_ascii=False)
        file.write("\n")

    ids = [case["case_id"] for case in dataset["cases"]]
    print(f"Total cases: {len(ids)}")
    print(f"Unique IDs: {len(set(ids))}")
    print("New cases added: SM009-SM030 (if not already present).")


if __name__ == "__main__":
    main()
