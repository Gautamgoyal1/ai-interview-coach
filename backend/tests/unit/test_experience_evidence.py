"""Unit tests for the experience-evidence rule-based classifier (baseline_predict)."""

import pytest

from app.modules.resume.evidence import LABELS, baseline_predict
from scripts.evaluate_experience_evidence import (
    LABELS as EVAL_LABELS,
    baseline_predict as eval_baseline_predict,
)


def test_evaluator_script_shares_same_classifier_implementation():
    """Verify that the evaluator script imports and uses the reusable module."""
    assert eval_baseline_predict is baseline_predict
    assert EVAL_LABELS is LABELS


def test_labels_list_contains_expected_classes():
    assert set(LABELS) == {
        "demonstrated",
        "mentioned_only",
        "negated",
        "planned_or_learning",
    }


# ---------------------------------------------------------------------------
# Contract & Empty / Missing Input Tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "text,skill",
    [
        ("", "python"),
        ("   ", "python"),
        ("Proficient in Python.", ""),
        ("Proficient in Python.", "   "),
        ("", ""),
        ("   ", "   "),
    ],
)
def test_empty_or_whitespace_input_returns_mentioned_only(text, skill):
    """Missing or empty inputs should return 'mentioned_only' without raising."""
    assert baseline_predict(text, skill) == "mentioned_only"


def test_target_skill_not_present_returns_mentioned_only():
    text = "Developed web applications using Go and PostgreSQL."
    assert baseline_predict(text, "docker") == "mentioned_only"


def test_case_insensitive_skill_and_text_matching():
    text = "BUILT DISTRIBUTED MICROSERVICES USING DOCKER."
    assert baseline_predict(text, "docker") == "demonstrated"
    assert baseline_predict(text, "DOCKER") == "demonstrated"


def test_curly_apostrophe_normalization():
    text = "I haven’t worked with Docker in production."
    assert baseline_predict(text, "docker") == "negated"


# ---------------------------------------------------------------------------
# Coverage of all Four Direct Evidence Labels
# ---------------------------------------------------------------------------


def test_label_demonstrated():
    text = "Built and deployed machine learning pipelines using scikit-learn."
    assert baseline_predict(text, "scikit-learn") == "demonstrated"


def test_label_mentioned_only():
    text = "Core technical competencies: Python, SQL, Docker, and Kubernetes."
    assert baseline_predict(text, "docker") == "mentioned_only"


def test_label_negated():
    text = "Have not worked with GraphQL in any commercial or personal project."
    assert baseline_predict(text, "graphql") == "negated"


def test_label_planned_or_learning():
    text = "Currently taking an introductory course on PyTorch architecture."
    assert baseline_predict(text, "pytorch") == "planned_or_learning"


# ---------------------------------------------------------------------------
# Negation and Contrast (Personal Project vs Professional Experience)
# ---------------------------------------------------------------------------


def test_personal_project_demonstrated_despite_no_professional_experience():
    text = (
        "I have never used Python professionally, "
        "but built several tools for personal automation projects."
    )
    assert baseline_predict(text, "python") == "demonstrated"


def test_at_work_denial_does_not_override_personal_applied_work():
    text = (
        "Have not used Docker at work, "
        "but configured containerized environments for home lab projects."
    )
    assert baseline_predict(text, "docker") == "demonstrated"


def test_unqualified_negation_classifies_as_negated():
    text = "I have never used Kubernetes in any capacity."
    assert baseline_predict(text, "kubernetes") == "negated"


# ---------------------------------------------------------------------------
# Coursework Alongside Denial of Practical Experience
# ---------------------------------------------------------------------------


def test_coursework_precedes_practical_denial_in_skill_context():
    text = (
        "No practical experience with scikit-learn; "
        "completed a course introducing its API."
    )
    assert baseline_predict(text, "scikit-learn") == "planned_or_learning"


def test_completed_coursework_with_lack_of_hands_on_experience():
    text = (
        "Lack hands-on experience with pandas; "
        "completed coursework covering its dataframes."
    )
    assert baseline_predict(text, "pandas") == "planned_or_learning"


# ---------------------------------------------------------------------------
# Third-Party Attribution
# ---------------------------------------------------------------------------


def test_teammate_action_is_not_credited_to_candidate():
    text = "My teammate built the Docker container deployment pipeline."
    assert baseline_predict(text, "docker") == "mentioned_only"


def test_employer_tech_stack_is_not_credited_to_candidate():
    text = (
        "My employer used Kubernetes for microservice hosting and orchestration."
    )
    assert baseline_predict(text, "kubernetes") == "mentioned_only"


def test_third_party_mention_with_explicit_self_denial_classifies_as_negated():
    text = "My team used Docker, but I did not use it myself."
    assert baseline_predict(text, "docker") == "negated"


def test_employer_stack_with_candidate_self_denial_classifies_as_negated():
    text = "My team's technology stack included Terraform, but I didn't use it."
    assert baseline_predict(text, "terraform") == "negated"


# ---------------------------------------------------------------------------
# Beginner-Level Descriptions Without Current Learning Evidence
# ---------------------------------------------------------------------------


def test_beginner_level_without_applied_evidence_is_mentioned_only():
    text = "Docker: beginner level; no deployments completed."
    assert baseline_predict(text, "docker") == "mentioned_only"


def test_beginner_status_without_learning_signals_is_mentioned_only():
    text = "Beginner with Redis; have reviewed documentation."
    assert baseline_predict(text, "redis") == "mentioned_only"


# ---------------------------------------------------------------------------
# Negative Control (Unrelated Positive Action in Another Clause)
# ---------------------------------------------------------------------------


def test_unrelated_positive_action_does_not_count_as_evidence_for_target_skill():
    text = (
        "Built data processing pipelines in Python; "
        "Docker is also listed in my technical summary."
    )
    # Python is demonstrated in the first clause
    assert baseline_predict(text, "python") == "demonstrated"
    # Docker is only mentioned in the second clause without applied action
    assert baseline_predict(text, "docker") == "mentioned_only"


def test_unrelated_action_in_separate_sentence_does_not_leak_evidence():
    text = (
        "Trained neural network models with PyTorch. "
        "Also familiar with SQL requirements."
    )
    assert baseline_predict(text, "pytorch") == "demonstrated"
    assert baseline_predict(text, "sql") == "mentioned_only"
