
import pytest

from app.modules.resume.grounding_metrics import (
    calculate_grounding_metrics,
)


def test_perfect_predictions():
    result = calculate_grounding_metrics(
        [
            {
                "expected_supported": True,
                "predicted_supported": True,
            },
            {
                "expected_supported": False,
                "predicted_supported": False,
            },
        ]
    )

    assert result["accuracy"] == 1.0
    assert result["supported_claims"]["f1"] == 1.0
    assert result["unsupported_claims"]["recall"] == 1.0


def test_unsupported_claims_predicted_as_supported_are_counted():
    result = calculate_grounding_metrics(
        [
            {
                "expected_supported": False,
                "predicted_supported": True,
            },
            {
                "expected_supported": True,
                "predicted_supported": True,
            },
        ]
    )

    assert result["accuracy"] == 0.5
    assert result["confusion_matrix"]["false_supported"] == 1
    assert result["unsupported_claims"]["recall"] == 0.0


def test_empty_evaluations_do_not_receive_perfect_score():
    result = calculate_grounding_metrics([])

    assert result["total"] == 0
    assert result["accuracy"] is None
    assert result["supported_claims"]["precision"] is None


def test_labels_must_be_booleans():
    with pytest.raises(ValueError, match="must be booleans"):
        calculate_grounding_metrics(
            [
                {
                    "expected_supported": "yes",
                    "predicted_supported": True,
                }
            ]
        )


def test_metrics_handle_missing_class():
    result = calculate_grounding_metrics(
        [
            {
                "expected_supported": True,
                "predicted_supported": True,
            }
        ]
    )

    assert result["supported_claims"]["recall"] == 1.0
    assert result["unsupported_claims"]["recall"] is None
