
import json

import pytest

from scripts import run_resume_feedback_quality_judge as runner


@pytest.fixture
def dataset():
    return {
        "evaluation_id": "checkpoint-test-v1",
        "cases": [
            {
                "case_id": "case-1",
                "feedback_item": "Add a concrete SQL project example.",
                "expected": {
                    "grounded": True,
                    "relevant": True,
                    "actionable": True,
                },
            }
        ],
    }


@pytest.fixture
def checkpoint_path(tmp_path, monkeypatch):
    path = tmp_path / "checkpoint.json"
    monkeypatch.setattr(runner, "CHECKPOINT_PATH", path)
    return path


def make_result(case):
    return {
        "case_id": case["case_id"],
        "expected": case["expected"].copy(),
        "predicted": {
            "grounded": True,
            "relevant": True,
            "actionable": True,
        },
        "reasoning": {
            "grounded": "The feedback does not invent candidate experience.",
            "relevant": "The feedback relates to the target role.",
            "actionable": "It gives a specific next step.",
        },
        "judge_provider": "azure_openai",
    }


def test_same_dataset_and_provider_resume_successfully(
    dataset, checkpoint_path
):
    result = make_result(dataset["cases"][0])
    runner.save_checkpoint(
        dataset, {"case-1": result}, "azure_openai"
    )

    loaded = runner.load_checkpoint(dataset, "azure_openai")

    assert list(loaded) == ["case-1"]
    assert loaded["case-1"] == result


def test_changed_feedback_text_rejects_checkpoint(
    dataset, checkpoint_path
):
    runner.save_checkpoint(dataset, {}, "azure_openai")
    dataset["cases"][0]["feedback_item"] = (
        "Claim expert-level SQL experience."
    )

    with pytest.raises(ValueError, match="fingerprint mismatch"):
        runner.load_checkpoint(dataset, "azure_openai")


def test_changed_expected_labels_reject_checkpoint(
    dataset, checkpoint_path
):
    runner.save_checkpoint(dataset, {}, "azure_openai")
    dataset["cases"][0]["expected"]["grounded"] = False

    with pytest.raises(ValueError, match="fingerprint mismatch"):
        runner.load_checkpoint(dataset, "azure_openai")


def test_different_provider_rejects_checkpoint(
    dataset, checkpoint_path
):
    runner.save_checkpoint(dataset, {}, "azure_openai")

    with pytest.raises(ValueError, match="provider"):
        runner.load_checkpoint(dataset, "gemini")


def test_legacy_checkpoint_without_metadata_is_rejected(
    dataset, checkpoint_path
):
    checkpoint_path.write_text(
        json.dumps(
            {
                "evaluation_id": dataset["evaluation_id"],
                "dataset_case_ids": ["case-1"],
                "completed_count": 0,
                "results": [],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="fingerprint mismatch"):
        runner.load_checkpoint(dataset, "azure_openai")
