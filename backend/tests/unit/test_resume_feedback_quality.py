
import pytest

from scripts.evaluate_resume_feedback_quality import (
    calculate_binary_metrics,
    summarize_labels,
    validate_dataset,
)


def make_case(
    case_id="case_1",
    grounded=True,
    relevant=True,
    actionable=False,
):
    return {
        "case_id": case_id,
        "section": "strengths",
        "resume_text": "Skills: Python and SQL.",
        "job_role": "Junior Machine Learning Engineer",
        "feedback_item": "The candidate lists Python.",
        "expected": {
            "grounded": grounded,
            "relevant": relevant,
            "actionable": actionable,
        },
        "notes": "Unit-test case.",
    }


def test_valid_dataset_is_accepted():
    dataset = {
        "evaluation_id": "test",
        "cases": [make_case()],
    }

    assert validate_dataset(dataset) is None


def test_empty_cases_are_rejected():
    with pytest.raises(ValueError, match="non-empty cases list"):
        validate_dataset({"cases": []})


def test_duplicate_case_ids_are_rejected():
    dataset = {
        "cases": [
            make_case(case_id="duplicate"),
            make_case(case_id="duplicate"),
        ]
    }

    with pytest.raises(ValueError, match="Duplicate case_id"):
        validate_dataset(dataset)


def test_non_boolean_labels_are_rejected():
    case = make_case()
    case["expected"]["grounded"] = "yes"

    with pytest.raises(ValueError, match="booleans"):
        validate_dataset({"cases": [case]})


def test_perfect_binary_predictions():
    result = calculate_binary_metrics(
        [True, False, True, False],
        [True, False, True, False],
    )

    assert result["accuracy"] == 1.0
    assert result["precision"] == 1.0
    assert result["recall"] == 1.0
    assert result["f1"] == 1.0
    assert result["confusion_matrix"] == {
        "true_positive": 2,
        "true_negative": 2,
        "false_positive": 0,
        "false_negative": 0,
    }


def test_unsupported_feedback_misclassified_as_grounded():
    result = calculate_binary_metrics(
        [False, True],
        [True, True],
    )

    assert result["accuracy"] == 0.5
    assert result["confusion_matrix"]["false_positive"] == 1
    assert result["precision"] == 0.5
    assert result["recall"] == 1.0


def test_empty_metric_inputs_do_not_get_perfect_score():
    result = calculate_binary_metrics([], [])

    assert result["total"] == 0
    assert result["accuracy"] is None
    assert result["precision"] is None
    assert result["recall"] is None
    assert result["f1"] is None


def test_mismatched_prediction_lengths_are_rejected():
    with pytest.raises(ValueError, match="equal length"):
        calculate_binary_metrics([True, False], [True])


def test_label_distribution_counts_reference_labels():
    cases = [
        make_case(grounded=True, relevant=True, actionable=False),
        make_case(
            case_id="case_2",
            grounded=False,
            relevant=True,
            actionable=True,
        ),
    ]

    result = summarize_labels(cases)

    assert result["grounded"] == {
        "true_count": 1,
        "false_count": 1,
    }
    assert result["relevant"] == {
        "true_count": 2,
        "false_count": 0,
    }
    assert result["actionable"] == {
        "true_count": 1,
        "false_count": 1,
    }
