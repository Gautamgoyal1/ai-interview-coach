"""Structured question and follow-up generation with quality validation and curated fallback."""

import json
import logging
import re
from typing import Any

from pydantic import BaseModel, ConfigDict, ValidationError

from app.integrations.llm.base import LLMError, LLMProvider
from app.modules.interview.calibration import (
    DEFAULT_EXPERIENCE_LEVEL,
    Difficulty,
    EXPERIENCE_GUIDANCE,
    EXPERIENCE_LEVEL_LABELS,
    ExperienceLevel,
    normalize_experience_level,
)
from app.modules.interview.deduplication import (
    compute_question_fingerprint,
    is_duplicate_or_paraphrase,
)
from app.modules.interview.prompts import (
    FOLLOW_UP_SYSTEM_PROMPT,
    FOLLOW_UP_USER_PROMPT,
    INTERVIEW_QUESTION_SYSTEM_PROMPT,
    INTERVIEW_QUESTION_USER_PROMPT,
)
from app.modules.interview.question_bank import pick_curated_fallback_question
from app.modules.interview.schemas import InterviewQuestion

logger = logging.getLogger(__name__)

MAX_GENERATION_ATTEMPTS = 2

_OVERLY_ACADEMIC_PATTERNS = (
    r"\bmathematical derivation\b",
    r"\bformal proof\b",
    r"\bmulti-head projection\b",
    r"\bbyzantine\b",
    r"\bpaxos\b",
    r"\braft consensus\b",
    r"\bstrict latency guarantees\b",
    r"\bhorizontally scalable,\s*distributed event-driven\b",
    r"\bjepsen\b",
)


class _GeneratedQuestionPayload(BaseModel):
    model_config = ConfigDict(extra="ignore")

    topic: str
    difficulty: str = "medium"
    question_type: str = "conceptual"
    question_text: str


class _GeneratedFollowUpPayload(BaseModel):
    model_config = ConfigDict(extra="ignore")

    question_text: str
    difficulty: str = "medium"


def _strip_json_fences(raw: str) -> str:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


def _normalize_difficulty(value: str) -> Difficulty:
    lowered = value.strip().lower()
    if lowered in {"easy", "medium", "hard"}:
        return lowered  # type: ignore[return-value]
    return "medium"


def _normalize_question_type(value: str, fallback: str) -> str:
    lowered = value.strip().lower()
    if lowered in {"conceptual", "applied", "gap_probe"}:
        return lowered
    return fallback if fallback in {"conceptual", "applied", "gap_probe"} else "conceptual"


def validate_generated_question(
    question_text: str,
    experience_level: ExperienceLevel,
    difficulty: Difficulty,
    previous_questions: list[str],
    candidate_context: dict[str, Any] | None = None,
    topic: str = "",
    asked_fingerprints: list[str] | None = None,
) -> tuple[bool, str | None]:
    """Validate clarity, single-question focus, calibration, novelty, and grounding."""
    cleaned = question_text.strip()
    if len(cleaned) < 12:
        return False, "Question is too short."
    if len(cleaned) > 420:
        return False, "Question is overly long or broad; keep it concise and focused."

    if cleaned.count("?") >= 3 or re.search(r"\b1\)\s+.*\b2\)\s+.*\b3\)\s+", cleaned):
        return False, "Ask one main question at a time instead of bundling multiple questions."

    is_dup, dup_reason = is_duplicate_or_paraphrase(
        candidate_text=cleaned,
        candidate_topic=topic,
        previous_questions=previous_questions,
        asked_fingerprints=asked_fingerprints,
    )
    if is_dup:
        return False, dup_reason or "Question repeats or closely paraphrases a previous question."

    lowered = cleaned.lower()
    if experience_level in {"internship", "fresher"} or difficulty in {"easy", "medium"}:
        for pattern in _OVERLY_ACADEMIC_PATTERNS:
            if re.search(pattern, lowered):
                return (
                    False,
                    "Question is overly academic or advanced for the selected experience level and difficulty.",
                )

    ctx = candidate_context or {}
    has_evidence = bool(
        (ctx.get("projects") or [])
        or (ctx.get("resume_skills") or [])
        or (ctx.get("matched_skills") or [])
    )
    if not has_evidence and re.search(r"\b(your project|you built|your resume)\b", lowered):
        return False, "Do not reference candidate projects when no resume evidence is available."

    return True, None


def _step_down_difficulty(difficulty: Difficulty) -> Difficulty:
    if difficulty == "hard":
        return "medium"
    return "easy"


def _calibrate_follow_up_difficulty(
    primary_difficulty: Difficulty,
    experience_level: ExperienceLevel,
    evaluation: dict[str, Any],
    follow_up_type: str | None = None,
) -> tuple[Difficulty, str]:
    """Calibrate follow-up difficulty and conversational guidance by intent & performance."""
    score = evaluation.get("overall_score")
    tech_corr = (evaluation.get("technical_correctness") or {}).get("score")

    struggled = (
        follow_up_type == "understanding_check"
        or (isinstance(score, (int, float)) and score < 50)
        or (isinstance(tech_corr, (int, float)) and tech_corr <= 2.0)
    )

    if struggled:
        target = _step_down_difficulty(primary_difficulty)
        guidance = (
            "The candidate struggled or showed a misconception; ask a gentler, "
            "concrete example or understanding check without escalating difficulty."
        )
        return target, guidance

    if follow_up_type == "deeper_exploration":
        guidance = (
            "The candidate gave a strong answer; ask a practical follow-up "
            "exploring real-world behavior, edge cases, or how to verify it."
        )
        return primary_difficulty, guidance

    if follow_up_type == "practical_application":
        guidance = (
            "Ask a concise practical application question connecting their "
            "explanation to real implementation."
        )
        return primary_difficulty, guidance

    if experience_level in {"internship", "fresher"} and primary_difficulty == "hard":
        return "medium", "Keep the follow-up practical and concise."

    return primary_difficulty, "Ask one concise follow-up to clarify the missing detail."


def _format_topic_performance_summary(
    topic_performance: dict[str, Any] | None,
) -> str:
    if not topic_performance:
        return "No topics evaluated yet."
    parts = []
    for entry in list(topic_performance.values())[-5:]:
        name = entry.get("topic") or "Topic"
        avg = entry.get("avg_score")
        if isinstance(avg, (int, float)):
            parts.append(f"{name}: {avg:.0f}/100")
    return "; ".join(parts) or "No topics evaluated yet."


def _fallback_primary_question(
    question_id: str,
    target_role: str,
    topic: str,
    difficulty: str,
    question_type: str,
    previous_questions: list[str] | None = None,
    experience_level: ExperienceLevel = DEFAULT_EXPERIENCE_LEVEL,
    candidate_context: dict[str, Any] | None = None,
    asked_fingerprints: list[str] | None = None,
) -> InterviewQuestion:
    norm_diff = _normalize_difficulty(difficulty)
    ctx = candidate_context or {}
    has_evidence = bool(
        (ctx.get("projects") or [])
        or (ctx.get("resume_skills") or [])
        or (ctx.get("matched_skills") or [])
    )
    curated = pick_curated_fallback_question(
        target_role=target_role,
        topic=topic,
        difficulty=norm_diff,
        question_type=question_type,
        previous_questions=previous_questions or [],
        experience_level=experience_level,
        has_resume_evidence=has_evidence,
        asked_fingerprints=asked_fingerprints,
    )
    return InterviewQuestion(
        question_id=question_id,
        topic=curated.topic,
        difficulty=norm_diff,
        question_text=curated.question_text,
        question_type=_normalize_question_type(curated.question_type, question_type),  # type: ignore[arg-type]
        is_follow_up=False,
    )


async def generate_interview_question(
    provider: LLMProvider | None,
    question_id: str,
    target_role: str,
    topic: str,
    question_type: str,
    difficulty: str,
    question_index: int,
    max_questions: int,
    candidate_context: dict[str, Any],
    retrieved_context: str,
    previous_questions: list[str],
    experience_level: str = DEFAULT_EXPERIENCE_LEVEL,
    question_focus: str = "fundamental",
    asked_fingerprints: list[str] | None = None,
    topic_performance: dict[str, Any] | None = None,
) -> InterviewQuestion:
    """Generate a validated primary interview question grounded in profile & RAG."""
    norm_level = normalize_experience_level(experience_level)
    norm_diff = _normalize_difficulty(difficulty)

    if provider is None:
        return _fallback_primary_question(
            question_id=question_id,
            target_role=target_role,
            topic=topic,
            difficulty=norm_diff,
            question_type=question_type,
            previous_questions=previous_questions,
            experience_level=norm_level,
            candidate_context=candidate_context,
            asked_fingerprints=asked_fingerprints,
        )

    validation_feedback = ""
    topic_perf_summary = _format_topic_performance_summary(topic_performance)

    for attempt in range(MAX_GENERATION_ATTEMPTS):
        prompt = INTERVIEW_QUESTION_USER_PROMPT.format(
            target_role=target_role,
            experience_level_label=EXPERIENCE_LEVEL_LABELS[norm_level],
            experience_guidance=EXPERIENCE_GUIDANCE[norm_level],
            topic=topic,
            question_focus=question_focus,
            question_type=question_type,
            difficulty=norm_diff,
            question_index=question_index,
            max_questions=max_questions,
            topic_performance_summary=topic_perf_summary,
            matched_skills=", ".join(candidate_context.get("matched_skills") or []) or "None listed",
            resume_skills=", ".join(candidate_context.get("resume_skills") or []) or "None listed",
            missing_skills=", ".join(candidate_context.get("missing_skills") or []) or "None listed",
            strengths="; ".join(candidate_context.get("strengths") or []) or "None listed",
            improvement_suggestions="; ".join(candidate_context.get("improvement_suggestions") or []) or "None listed",
            retrieved_context=retrieved_context or "No external knowledge chunks retrieved; rely on standard technical interview fundamentals.",
            previous_questions="\n".join(f"- {q}" for q in previous_questions[-20:]) or "None yet.",
            validation_feedback=validation_feedback,
        )

        try:
            raw = await provider.generate(
                prompt=prompt,
                system=INTERVIEW_QUESTION_SYSTEM_PROMPT,
                json_mode=True,
            )
            data = json.loads(_strip_json_fences(raw))
            parsed = _GeneratedQuestionPayload.model_validate(data)
            question_text = parsed.question_text.strip()
            resolved_topic = parsed.topic.strip() or topic
            is_valid, reason = validate_generated_question(
                question_text=question_text,
                experience_level=norm_level,
                difficulty=norm_diff,
                previous_questions=previous_questions,
                candidate_context=candidate_context,
                topic=resolved_topic,
                asked_fingerprints=asked_fingerprints,
            )
            if is_valid:
                return InterviewQuestion(
                    question_id=question_id,
                    topic=resolved_topic,
                    difficulty=norm_diff,
                    question_text=question_text,
                    question_type=_normalize_question_type(parsed.question_type, question_type),  # type: ignore[arg-type]
                    is_follow_up=False,
                )

            logger.info(
                "Question attempt %d rejected by quality validator: %s",
                attempt + 1,
                reason,
            )
            validation_feedback = (
                f"\nPrevious attempt was rejected ({reason}). Generate a fresh, non-repeating question.\n"
            )
        except (LLMError, json.JSONDecodeError, ValidationError, ValueError) as exc:
            logger.warning(
                "Question generation attempt %d failed (%s); falling back.",
                attempt + 1,
                type(exc).__name__,
            )
            break

    return _fallback_primary_question(
        question_id=question_id,
        target_role=target_role,
        topic=topic,
        difficulty=norm_diff,
        question_type=question_type,
        previous_questions=previous_questions,
        experience_level=norm_level,
        candidate_context=candidate_context,
        asked_fingerprints=asked_fingerprints,
    )


async def generate_follow_up_question(
    provider: LLMProvider | None,
    question_id: str,
    target_role: str,
    topic: str,
    difficulty: str,
    previous_question: str,
    candidate_answer: str,
    evaluation: dict[str, Any],
    retrieved_context: str,
    experience_level: str = DEFAULT_EXPERIENCE_LEVEL,
    follow_up_type: str | None = None,
) -> InterviewQuestion:
    """Generate a natural, level-calibrated follow-up question or safe fallback."""
    norm_level = normalize_experience_level(experience_level)
    primary_diff = _normalize_difficulty(difficulty)
    fu_diff, fu_guidance = _calibrate_follow_up_difficulty(
        primary_difficulty=primary_diff,
        experience_level=norm_level,
        evaluation=evaluation,
        follow_up_type=follow_up_type,
    )

    missing = list(evaluation.get("missing_concepts") or [])
    reason = str(evaluation.get("follow_up_reason") or "").strip()

    def _fallback() -> InterviewQuestion:
        if follow_up_type == "deeper_exploration":
            text = (
                f"Good explanation. In practice, what edge case or common pitfall "
                f"should you watch out for with {topic}?"
            )
        elif follow_up_type == "practical_application":
            text = (
                f"How would you apply {topic} in a small feature or API endpoint?"
            )
        elif missing:
            text = (
                f"You touched on parts of {topic}. Could you briefly explain "
                f"{missing[0]} in your own words?"
            )
        else:
            text = (
                f"Could you give a quick, concrete example of how {topic} "
                f"is used in practice?"
            )
        return InterviewQuestion(
            question_id=question_id,
            topic=topic,
            difficulty=fu_diff,
            question_text=text,
            question_type="follow_up",
            is_follow_up=True,
        )

    if provider is None:
        return _fallback()

    prompt = FOLLOW_UP_USER_PROMPT.format(
        target_role=target_role,
        experience_level_label=EXPERIENCE_LEVEL_LABELS[norm_level],
        topic=topic,
        previous_question=previous_question,
        candidate_answer=candidate_answer,
        follow_up_type=follow_up_type or "clarification",
        follow_up_reason=reason or "Clarify understanding gently.",
        follow_up_guidance=fu_guidance,
        missing_concepts=", ".join(missing) or "None specified",
        retrieved_context=retrieved_context or "No external knowledge chunks retrieved.",
        difficulty=fu_diff,
    )

    try:
        raw = await provider.generate(
            prompt=prompt,
            system=FOLLOW_UP_SYSTEM_PROMPT,
            json_mode=True,
        )
        data = json.loads(_strip_json_fences(raw))
        parsed = _GeneratedFollowUpPayload.model_validate(data)
        question_text = parsed.question_text.strip()
        is_valid, _reason = validate_generated_question(
            question_text=question_text,
            experience_level=norm_level,
            difficulty=fu_diff,
            previous_questions=[previous_question],
            topic=topic,
        )
        if not is_valid:
            return _fallback()

        return InterviewQuestion(
            question_id=question_id,
            topic=topic,
            difficulty=fu_diff,
            question_text=question_text,
            question_type="follow_up",
            is_follow_up=True,
        )
    except (LLMError, json.JSONDecodeError, ValidationError, ValueError) as exc:
        logger.warning(
            "Follow-up generation fell back to deterministic prompt: %s",
            type(exc).__name__,
        )
        return _fallback()
