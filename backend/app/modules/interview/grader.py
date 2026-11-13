
import json
import math
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.integrations.llm.base import LLMError, LLMProvider
from app.modules.interview.calibration import (
    DEFAULT_EXPERIENCE_LEVEL,
    EXPERIENCE_LEVEL_LABELS,
    normalize_experience_level,
)
from app.modules.interview.prompts import (
    ANSWER_EVALUATION_SYSTEM_PROMPT,
    ANSWER_EVALUATION_USER_PROMPT,
    GRADER_SYSTEM_PROMPT,
    GRADER_USER_PROMPT,
)
from app.modules.interview.rubric import (
    RUBRIC_VERSION,
    RUBRIC_WEIGHTS,
    calculate_answer_score,
)


class GradingResult(BaseModel):
    """Validated result returned by the AI answer grader."""

    model_config = ConfigDict(extra="forbid")

    score: float = Field(ge=0)
    label: Literal["correct", "partially_correct", "incorrect"]
    strengths: list[str]
    missing_concepts: list[str]
    feedback: str


async def grade_answer(
    provider: LLMProvider,
    question: str,
    answer: str,
    reference_answer: str,
    max_score: float = 5,
) -> GradingResult:
    """Grade an interview answer using an LLM and validate its output."""

    if not question.strip():
        raise ValueError("Question cannot be empty.")

    if not answer.strip():
        answer = "[No answer provided]"

    if not math.isfinite(max_score) or max_score <= 0:
        raise ValueError("max_score must be a positive, finite number.")

    prompt = GRADER_USER_PROMPT.format(
        question=question,
        answer=answer,
        reference_answer=reference_answer or "No reference answer provided.",
        max_score=max_score,
    )

    raw_response = await provider.generate(
        prompt=prompt,
        system=GRADER_SYSTEM_PROMPT,
        json_mode=True,
    )

    try:
        data = json.loads(raw_response)
        result = GradingResult.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as exc:
        raise ValueError(
            f"The LLM returned an invalid grading response: {exc}"
        ) from exc

    if not math.isfinite(result.score) or result.score > max_score:
        raise ValueError(
            f"Grader score must be between 0 and {max_score}."
        )

    # Round only after validating the original score.
    result.score = round(result.score, 2)

    return result


class DimensionScore(BaseModel):
    """Score and evidence-based explanation for a single rubric dimension."""

    model_config = ConfigDict(extra="ignore")

    score: float = Field(ge=0.0, le=5.0)
    explanation: str


class _RawRubricLLMOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    technical_correctness: DimensionScore
    relevance: DimensionScore
    completeness: DimensionScore
    technical_depth: DimensionScore
    strengths: list[str] = Field(default_factory=list)
    missing_concepts: list[str] = Field(default_factory=list)
    improvement_suggestions: list[str] = Field(default_factory=list)
    confidence: Literal["high", "medium", "low"] = "medium"
    follow_up_needed: bool = False
    follow_up_reason: str | None = None


class RubricAnswerEvaluation(BaseModel):
    """Structured rubric-based evaluation with deterministic weighted score."""

    technical_correctness: DimensionScore | None = None
    relevance: DimensionScore | None = None
    completeness: DimensionScore | None = None
    technical_depth: DimensionScore | None = None

    overall_score: float | None = Field(default=None, ge=0.0, le=100.0)

    strengths: list[str] = Field(default_factory=list)
    missing_concepts: list[str] = Field(default_factory=list)
    improvement_suggestions: list[str] = Field(default_factory=list)

    confidence: Literal["high", "medium", "low", "unavailable"] = "medium"
    grading_status: Literal["completed", "unavailable"] = "completed"
    reference_available: bool = False
    rubric_version: str = RUBRIC_VERSION
    rubric_weights: dict[str, float] = Field(
        default_factory=lambda: dict(RUBRIC_WEIGHTS)
    )

    follow_up_needed: bool = False
    follow_up_reason: str | None = None


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


def unavailable_evaluation(
    *,
    reference_available: bool,
    follow_up_needed: bool = False,
    follow_up_reason: str | None = None,
) -> RubricAnswerEvaluation:
    """Return an explicit unavailable evaluation without fabricating scores."""
    return RubricAnswerEvaluation(
        overall_score=None,
        confidence="unavailable",
        grading_status="unavailable",
        reference_available=reference_available,
        follow_up_needed=follow_up_needed,
        follow_up_reason=follow_up_reason,
    )


async def grade_interview_answer(
    provider: LLMProvider | None,
    target_role: str,
    topic: str,
    difficulty: str,
    question_text: str,
    answer_text: str,
    retrieved_context: str = "",
    experience_level: str = DEFAULT_EXPERIENCE_LEVEL,
) -> RubricAnswerEvaluation:
    """Evaluate an interview answer against the 4-dimension rubric."""
    cleaned_answer = answer_text.strip()
    reference_available = bool(retrieved_context.strip())

    if not cleaned_answer:
        zero_dim = DimensionScore(
            score=0.0,
            explanation="No answer was provided by the candidate.",
        )
        return RubricAnswerEvaluation(
            technical_correctness=zero_dim,
            relevance=zero_dim,
            completeness=zero_dim,
            technical_depth=zero_dim,
            overall_score=0.0,
            strengths=[],
            missing_concepts=["Complete technical explanation"],
            improvement_suggestions=[
                "Provide a clear answer addressing the core question."
            ],
            confidence="high",
            grading_status="completed",
            reference_available=reference_available,
            follow_up_needed=True,
            follow_up_reason="No answer provided.",
        )

    is_brief = len(cleaned_answer.split()) < 12

    if provider is None:
        return unavailable_evaluation(
            reference_available=reference_available,
            follow_up_needed=is_brief,
            follow_up_reason=(
                "Answer was brief; probe for concrete details."
                if is_brief
                else None
            ),
        )

    norm_level = normalize_experience_level(experience_level)
    prompt = ANSWER_EVALUATION_USER_PROMPT.format(
        target_role=target_role,
        experience_level_label=EXPERIENCE_LEVEL_LABELS[norm_level],
        topic=topic,
        difficulty=difficulty,
        question_text=question_text,
        answer_text=cleaned_answer,
        retrieved_context=(
            retrieved_context.strip()
            or "No external reference material retrieved; evaluate using standard technical fundamentals and note this limitation."
        ),
    )

    try:
        raw = await provider.generate(
            prompt=prompt,
            system=ANSWER_EVALUATION_SYSTEM_PROMPT,
            json_mode=True,
        )
        data = json.loads(_strip_fences(raw))
        parsed = _RawRubricLLMOutput.model_validate(data)
    except (LLMError, json.JSONDecodeError, ValidationError, ValueError):
        return unavailable_evaluation(
            reference_available=reference_available,
            follow_up_needed=is_brief,
            follow_up_reason=(
                "Answer was brief; probe for concrete details."
                if is_brief
                else None
            ),
        )

    dim_scores = {
        "technical_correctness": parsed.technical_correctness.score,
        "relevance": parsed.relevance.score,
        "completeness": parsed.completeness.score,
        "technical_depth": parsed.technical_depth.score,
    }
    overall = calculate_answer_score(dim_scores, RUBRIC_WEIGHTS)

    return RubricAnswerEvaluation(
        technical_correctness=parsed.technical_correctness,
        relevance=parsed.relevance,
        completeness=parsed.completeness,
        technical_depth=parsed.technical_depth,
        overall_score=overall,
        strengths=parsed.strengths,
        missing_concepts=parsed.missing_concepts,
        improvement_suggestions=parsed.improvement_suggestions,
        confidence=parsed.confidence if reference_available else "low",
        grading_status="completed",
        reference_available=reference_available,
        rubric_version=RUBRIC_VERSION,
        rubric_weights=dict(RUBRIC_WEIGHTS),
        follow_up_needed=parsed.follow_up_needed,
        follow_up_reason=parsed.follow_up_reason,
    )
