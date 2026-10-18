
"""Unit tests for resume skill extraction and matching."""

import pytest

from app.modules.resume.scoring import (
    calculate_match,
    calculate_match_against_skills,
    extract_skills,
    load_role_skills,
    load_skill_taxonomy,
)


@pytest.fixture
def taxonomy():
    return {
        "python": ["python", "python3"],
        "machine learning": [
            "machine learning",
            "ml",
            "machine-learning",
        ],
        "docker": ["docker", "containers", "containerization"],
    }


def test_extract_skills(taxonomy):
    text = "Experienced in Python3, ML, and Docker."

    assert extract_skills(text, taxonomy) == [
        "docker",
        "machine learning",
        "python",
    ]


def test_extract_skills_avoids_partial_word_matches(taxonomy):
    assert extract_skills("I enjoy pythonista tools.", taxonomy) == []


def test_calculate_match_all_skills_match(taxonomy):
    result = calculate_match(
        "Python, machine learning, Docker",
        "Python, ML, Docker",
        taxonomy,
    )

    assert result["match_score"] == 100.0
    assert result["missing_skills"] == []


def test_calculate_match_one_skill_missing(taxonomy):
    result = calculate_match(
        "Python and machine learning",
        "Python, machine learning, Docker",
        taxonomy,
    )

    assert result["match_score"] == 66.67
    assert result["missing_skills"] == ["docker"]


def test_calculate_match_no_matching_skills(taxonomy):
    result = calculate_match(
        "I have communication skills",
        "Python and Docker",
        taxonomy,
    )

    assert result["match_score"] == 0.0
    assert result["matched_skills"] == []


def test_empty_job_description_has_zero_score(taxonomy):
    result = calculate_match("Python experience", "", taxonomy)

    assert result["match_score"] == 0.0


def test_match_against_explicit_required_skills(taxonomy):
    result = calculate_match_against_skills(
        "Python and ML experience",
        ["python", "machine learning", "docker"],
        taxonomy,
    )

    assert result["match_score"] == 66.67
    assert result["matched_skills"] == ["machine learning", "python"]
    assert result["missing_skills"] == ["docker"]


def test_unknown_required_skill_is_rejected(taxonomy):
    with pytest.raises(ValueError, match="Unknown canonical skills"):
        calculate_match_against_skills(
            "Python experience",
            ["java"],
            taxonomy,
        )


def test_role_configuration_loads():
    roles = load_role_skills()

    assert "machine learning engineer" in roles
    assert "python developer" in roles


def test_real_taxonomy_recognizes_resume_technologies():
    taxonomy = load_skill_taxonomy()

    result = extract_skills(
        "Python, SQL, NumPy, Pandas, and Scikit-learn",
        taxonomy,
    )

    assert result == [
        "numpy",
        "pandas",
        "python",
        "scikit-learn",
        "sql",
    ]


def test_model_evaluation_alias_matches_resume_wording():
    taxonomy = load_skill_taxonomy()

    result = extract_skills(
        "Evaluated the model using a train-test split.",
        taxonomy,
    )

    assert result == ["model evaluation"]


def test_docker_is_missing_when_not_mentioned():
    taxonomy = load_skill_taxonomy()

    result = calculate_match(
        (
            "Python, SQL, NumPy, Pandas, Scikit-learn, "
            "and evaluated the model."
        ),
        (
            "Python, SQL, NumPy, Pandas, Scikit-learn, "
            "model evaluation, and Docker."
        ),
        taxonomy,
    )

    assert "docker" in result["missing_skills"]
    assert "model evaluation" in result["matched_skills"]

def test_extract_skills_currently_matches_negated_mentions(taxonomy):
    """Document that keyword matching does not understand negation."""
    result = extract_skills(
        "I have never used Docker.",
        taxonomy,
    )

    # Current limitation: Docker is detected despite the negation.
    assert result == ["docker"]


def test_extract_skills_currently_matches_learning_interests(taxonomy):
    """Document that keyword matching does not infer skill proficiency."""
    result = extract_skills(
        "I am interested in learning Docker.",
        taxonomy,
    )

    # Current limitation: interest is treated as a skill mention.
    assert result == ["docker"]


def test_empty_explicit_required_skills_has_zero_score(taxonomy):
    result = calculate_match_against_skills(
        "Python and Docker experience",
        [],
        taxonomy,
    )

    assert result["match_score"] == 0.0
    assert result["matched_skills"] == []
    assert result["missing_skills"] == []
