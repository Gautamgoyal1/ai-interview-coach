
from app.modules.resume.feedback_evaluator import evaluate_feedback


def make_feedback():
    return {
        "strengths": [
            "Demonstrates Python and scikit-learn skills through the House Price Prediction project.",
            "Used Pandas for data preprocessing."
        ],
        "improvement_suggestions": [
            "Add specific performance metrics to quantify model success.",
            "Describe the data preprocessing steps in more detail."
        ],
        "likely_interview_questions": [
            "How did you evaluate your model using a train-test split?",
            "How did you use SQL to analyze sales records?"
        ]
    }


def make_expectations():
    return {
        "evaluation_id": "test_feedback",
        "resume_facts": [
            "The candidate used Python and scikit-learn in a House Price Prediction project.",
            "The candidate used Pandas for data preprocessing.",
            "The candidate evaluated the model using a train-test split.",
            "The candidate used SQL to query sales records."
        ],
        "not_established_by_resume": [
            "Model accuracy or other numerical performance results",
            "Model deployment or production experience",
            "Docker experience",
            "Cloud platform experience",
            "Specific feature engineering techniques",
            "Specific missing-value or outlier handling techniques"
        ],
        "section_expectations": {
            "strengths": {"must_be_nonempty": True},
            "improvement_suggestions": {"must_be_nonempty": True},
            "likely_interview_questions": {"must_be_nonempty": True}
        }
    }


def test_valid_feedback_passes_structure_checks():
    result = evaluate_feedback(make_feedback(), make_expectations())

    assert result["structure_checks_passed"] is True
    assert result["issue_count"] == 0


def test_empty_feedback_section_fails_structure_check():
    feedback = make_feedback()
    feedback["strengths"] = []

    result = evaluate_feedback(feedback, make_expectations())

    assert result["structure_checks_passed"] is False
    assert result["issue_count"] > 0

def test_conditional_feature_engineering_recommendation_is_not_flagged():
    feedback = make_feedback()
    feedback["improvement_suggestions"] = [
        "If you performed feature engineering, "
        "describe the techniques you used."
    ]

    result = evaluate_feedback(feedback, make_expectations())

    unsupported_issues = [
        issue
        for issue in result["issues"]
        if issue["issue"] == "unsupported_topic_needs_review"
    ]
    assert unsupported_issues == []
def test_unestablished_topic_is_flagged_for_review():
    feedback = make_feedback()
    feedback["strengths"] = [
        "Achieved 95% model accuracy using Docker."
    ]

    result = evaluate_feedback(feedback, make_expectations())

    flagged_topics = {
        issue["detail"]
        for issue in result["issues"]
        if issue["issue"] == "unsupported_topic_needs_review"
    }

    assert any("model accuracy" in detail.lower() for detail in flagged_topics)
    assert any("Docker experience" in detail for detail in flagged_topics)


def test_recommendation_about_missing_evidence_is_not_auto_rejected():
    feedback = make_feedback()
    feedback["improvement_suggestions"] = [
        "Add model accuracy metrics if you have measured them.",
        "Include Docker experience if applicable."
    ]

    result = evaluate_feedback(feedback, make_expectations())

    unsupported_issues = [
        issue
        for issue in result["issues"]
        if issue["issue"] == "unsupported_topic_needs_review"
    ]

    assert unsupported_issues == []
