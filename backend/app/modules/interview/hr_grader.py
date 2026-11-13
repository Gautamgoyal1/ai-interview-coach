"""Objective, 5-dimension rubric evaluation for HR and Behavioral interview answers."""

import json
import logging
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.integrations.llm.base import LLMError, LLMProvider
from app.modules.interview.calibration import (
    DEFAULT_EXPERIENCE_LEVEL,
    EXPERIENCE_LEVEL_LABELS,
    normalize_experience_level,
)
from app.modules.interview.grader import DimensionScore
from app.modules.interview.hr_prompts import (
    HR_EVALUATION_SYSTEM_PROMPT,
    HR_EVALUATION_USER_PROMPT,
)
from app.modules.interview.rubric import (
    HR_RUBRIC_DIMENSIONS,
    HR_RUBRIC_VERSION,
    HR_RUBRIC_WEIGHTS,
    calculate_hr_answer_score,
)

logger = logging.getLogger(__name__)


class _RawHRRubricLLMOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    reasoning_critical_thinking: DimensionScore
    decision_making_tradeoffs: DimensionScore
    communication_clarity: DimensionScore
    relevance_completeness: DimensionScore
    reflection_adaptability: DimensionScore

    strengths: list[str] = Field(default_factory=list)
    missing_concepts: list[str] = Field(default_factory=list)
    improvement_suggestions: list[str] = Field(default_factory=list)

    confidence: Literal["high", "medium", "low"] = "medium"
    follow_up_needed: bool = False
    follow_up_reason: str | None = None
    follow_up_type: str | None = None


class HRRubricAnswerEvaluation(BaseModel):
    """Structured HR rubric-based evaluation with deterministic weighted score."""

    model_config = ConfigDict(extra="ignore")

    reasoning_critical_thinking: DimensionScore | None = None
    decision_making_tradeoffs: DimensionScore | None = None
    communication_clarity: DimensionScore | None = None
    relevance_completeness: DimensionScore | None = None
    reflection_adaptability: DimensionScore | None = None

    overall_score: float | None = Field(default=None, ge=0.0, le=100.0)

    strengths: list[str] = Field(default_factory=list)
    missing_concepts: list[str] = Field(default_factory=list)
    improvement_suggestions: list[str] = Field(default_factory=list)

    confidence: Literal["high", "medium", "low", "unavailable"] = "medium"
    grading_status: Literal["completed", "unavailable"] = "completed"
    rubric_version: str = HR_RUBRIC_VERSION
    rubric_weights: dict[str, float] = Field(
        default_factory=lambda: dict(HR_RUBRIC_WEIGHTS)
    )

    follow_up_needed: bool = False
    follow_up_reason: str | None = None
    follow_up_type: str | None = None


def _strip_fences(raw: str) -> str:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


def unavailable_hr_evaluation(
    *,
    follow_up_needed: bool = False,
    follow_up_reason: str | None = None,
    follow_up_type: str | None = None,
) -> HRRubricAnswerEvaluation:
    """Return explicit unavailable evaluation without fabricating scores."""
    return HRRubricAnswerEvaluation(
        overall_score=None,
        confidence="unavailable",
        grading_status="unavailable",
        follow_up_needed=follow_up_needed,
        follow_up_reason=follow_up_reason,
        follow_up_type=follow_up_type,
    )


async def grade_hr_interview_answer(
    *,
    provider: LLMProvider | None,
    target_role: str,
    category: str,
    difficulty: str,
    question_text: str,
    answer_text: str,
    experience_level: str = DEFAULT_EXPERIENCE_LEVEL,
) -> HRRubricAnswerEvaluation:
    """Evaluate an HR interview answer against the 5-dimension behavioral rubric."""
    cleaned_answer = answer_text.strip()

    if not cleaned_answer:
        zero_dim = DimensionScore(
            score=0.0,
            explanation="No answer was provided by the candidate.",
        )
        return HRRubricAnswerEvaluation(
            reasoning_critical_thinking=zero_dim,
            decision_making_tradeoffs=zero_dim,
            communication_clarity=zero_dim,
            relevance_completeness=zero_dim,
            reflection_adaptability=zero_dim,
            overall_score=0.0,
            strengths=[],
            missing_concepts=["Response to scenario"],
            improvement_suggestions=["Provide an answer describing your approach or experience."],
            confidence="high",
            grading_status="completed",
            follow_up_needed=True,
            follow_up_reason="No answer provided.",
            follow_up_type="clarification",
        )

    is_brief = len(cleaned_answer.split()) < 15

    if provider is None:
        return unavailable_hr_evaluation(
            follow_up_needed=is_brief,
            follow_up_reason="Answer was brief; probe for concrete context." if is_brief else None,
            follow_up_type="clarification" if is_brief else None,
        )

    norm_level = normalize_experience_level(experience_level)
    level_label = EXPERIENCE_LEVEL_LABELS[norm_level]

    prompt = HR_EVALUATION_USER_PROMPT.format(
        target_role=target_role,
        experience_level_label=level_label,
        category=category,
        difficulty=difficulty,
        question_text=question_text,
        answer_text=cleaned_answer,
    )

    try:
        raw = await provider.generate(
            prompt=prompt,
            system=HR_EVALUATION_SYSTEM_PROMPT,
            json_mode=True,
        )
        data = json.loads(_strip_fences(raw))
        parsed = _RawHRRubricLLMOutput.model_validate(data)
    except (LLMError, json.JSONDecodeError, ValidationError, ValueError) as exc:
        logger.warning("HR grading failed or returned invalid JSON: %s", exc)
        return unavailable_hr_evaluation(
            follow_up_needed=is_brief,
            follow_up_reason="Answer was brief; probe for concrete context." if is_brief else None,
            follow_up_type="clarification" if is_brief else None,
        )

    dim_scores = {
        "reasoning_critical_thinking": parsed.reasoning_critical_thinking.score,
        "decision_making_tradeoffs": parsed.decision_making_tradeoffs.score,
        "communication_clarity": parsed.communication_clarity.score,
        "relevance_completeness": parsed.relevance_completeness.score,
        "reflection_adaptability": parsed.reflection_adaptability.score,
    }
    overall = calculate_hr_answer_score(dim_scores, HR_RUBRIC_WEIGHTS)

    return HRRubricAnswerEvaluation(
        reasoning_critical_thinking=parsed.reasoning_critical_thinking,
        decision_making_tradeoffs=parsed.decision_making_tradeoffs,
        communication_clarity=parsed.communication_clarity,
        relevance_completeness=parsed.relevance_completeness,
        reflection_adaptability=parsed.reflection_adaptability,
        overall_score=overall,
        strengths=parsed.strengths,
        missing_concepts=parsed.missing_concepts,
        improvement_suggestions=parsed.improvement_suggestions,
        confidence=parsed.confidence,
        grading_status="completed",
        rubric_version=HR_RUBRIC_VERSION,
        rubric_weights=dict(HR_RUBRIC_WEIGHTS),
        follow_up_needed=parsed.follow_up_needed,
        follow_up_reason=parsed.follow_up_reason,
        follow_up_type=parsed.follow_up_type,
    )
