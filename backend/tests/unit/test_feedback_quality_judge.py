
import json

import anyio
import pytest

from app.modules.resume.feedback_quality_judge import (
    FeedbackQualityJudge,
    JUDGE_SYSTEM_PROMPT,
)


class FakeLLM:
    def __init__(self, response):
        self.response = response
        self.last_call = None

    async def generate(self, prompt, system=None, json_mode=False):
        self.last_call = {
            "prompt": prompt,
            "system": system,
            "json_mode": json_mode,
        }
        return self.response


def valid_response():
    return json.dumps({
        "grounded": True,
        "relevant": True,
        "actionable": False,
        "reasoning": {
            "grounded": "The claim is supported by the resume.",
            "relevant": "It relates to the target role.",
            "actionable": "It does not give a next step.",
        },
    })


def test_judge_returns_validated_labels():
    async def run_test():
        llm = FakeLLM(valid_response())
        judge = FeedbackQualityJudge(llm=llm)

        result = await judge.evaluate({
            "resume_text": "Skills: Python.",
            "job_role": "Junior ML Engineer",
            "section": "strengths",
            "feedback_item": "The candidate lists Python.",
        })

        assert result["grounded"] is True
        assert result["relevant"] is True
        assert result["actionable"] is False
        assert llm.last_call["json_mode"] is True

    anyio.run(run_test)


def test_judge_rejects_non_boolean_labels():
    async def run_test():
        response = json.loads(valid_response())
        response["grounded"] = "yes"
        llm = FakeLLM(json.dumps(response))
        judge = FeedbackQualityJudge(llm=llm)

        with pytest.raises(ValueError, match="must be Boolean"):
            await judge.evaluate({
                "resume_text": "Skills: Python.",
                "job_role": "Junior ML Engineer",
                "section": "strengths",
                "feedback_item": "The candidate lists Python.",
            })

    anyio.run(run_test)


def test_judge_rejects_invalid_json():
    async def run_test():
        judge = FeedbackQualityJudge(llm=FakeLLM("not JSON"))

        with pytest.raises(ValueError, match="invalid JSON"):
            await judge.evaluate({
                "resume_text": "Skills: Python.",
                "job_role": "Junior ML Engineer",
                "section": "strengths",
                "feedback_item": "The candidate lists Python.",
            })

    anyio.run(run_test)


def test_judge_prompt_distinguishes_recommendations_from_claims():
    prompt = JUDGE_SYSTEM_PROMPT.lower()

    assert "recommendation to add missing information is grounded" in prompt
    assert "do not confuse recommending a future action" in prompt
    assert "rmse of 12.5" in prompt
    assert "not grounded" in prompt


def test_judge_prompt_covers_unsupported_question_assumptions():
    prompt = JUDGE_SYSTEM_PROMPT.lower()

    assert "questions that presuppose an undocumented action" in prompt
    assert "a question mark does not make" in prompt
    assert "general knowledge question" in prompt
