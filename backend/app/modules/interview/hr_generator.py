"""HR and Behavioral question and follow-up generation with deduplication and curated fallbacks."""

import json
import logging
import re
from typing import Any

from pydantic import BaseModel, ConfigDict, ValidationError

from app.integrations.llm.base import LLMError, LLMProvider
from app.modules.interview.calibration import (
    DEFAULT_EXPERIENCE_LEVEL,
    Difficulty,
    EXPERIENCE_LEVEL_LABELS,
    normalize_experience_level,
)
from app.modules.interview.deduplication import (
    compute_question_fingerprint,
    is_duplicate_or_paraphrase,
)
from app.modules.interview.hr_prompts import (
    HR_FOLLOW_UP_SYSTEM_PROMPT,
    HR_FOLLOW_UP_USER_PROMPT,
    HR_QUESTION_SYSTEM_PROMPT,
    HR_QUESTION_USER_PROMPT,
)
from app.modules.interview.hr_question_bank import (
    HR_CATEGORIES,
    HRCategory,
    pick_curated_hr_question,
)
from app.modules.interview.schemas import InterviewQuestion

logger = logging.getLogger(__name__)

MAX_GENERATION_ATTEMPTS = 2


class _GeneratedHRQuestionPayload(BaseModel):
    model_config = ConfigDict(extra="ignore")

    category: str
    difficulty: str = "medium"
    question_text: str
    scenario_type: str = "past_experience"


class _GeneratedHRFollowUpPayload(BaseModel):
    model_config = ConfigDict(extra="ignore")

    question_text: str
    follow_up_type: str = "clarification"


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


def _clean_question_text(raw_text: str) -> str:
    cleaned = raw_text.strip().strip('"').strip("'")
    cleaned = re.sub(r"^(Question:\s*|\d+[\.\)]\s*)", "", cleaned, flags=re.IGNORECASE)
    return cleaned.strip()


async def generate_hr_question(
    *,
    provider: LLMProvider | None,
    question_id: str,
    target_role: str,
    category: str,
    difficulty: str,
    question_index: int,
    max_questions: int,
    candidate_context: dict[str, Any],
    previous_questions: list[str],
    experience_level: str = DEFAULT_EXPERIENCE_LEVEL,
    asked_fingerprints: list[str] | None = None,
) -> InterviewQuestion:
    """Generate an HR/behavioral question grounded in resume context with fallback."""
    norm_level = normalize_experience_level(experience_level)
    level_label = EXPERIENCE_LEVEL_LABELS[norm_level]
    calibrated_diff = _normalize_difficulty(difficulty)

    cat_name = category if category in HR_CATEGORIES else "Behavioral Experience"
    fingerprints = set(asked_fingerprints or [])

    resume_skills = candidate_context.get("resume_skills") or candidate_context.get("matched_skills") or []
    strengths = candidate_context.get("strengths") or []
    projects = candidate_context.get("projects") or []

    # Format previous questions
    prev_bulleted = "\n".join(f"- {q}" for q in previous_questions[-8:]) or "None."

    prompt = HR_QUESTION_USER_PROMPT.format(
        target_role=target_role,
        experience_level_label=level_label,
        category=cat_name,
        difficulty=calibrated_diff,
        question_index=question_index,
        max_questions=max_questions,
        resume_skills=", ".join(resume_skills[:8]) or "General technical background",
        strengths=", ".join(strengths[:4]) or "Standard background",
        projects=", ".join(projects[:3]) or "Coursework & personal projects",
        previous_questions=prev_bulleted,
    )

    if provider is not None:
        for attempt in range(MAX_GENERATION_ATTEMPTS):
            try:
                raw_json = await provider.generate(
                    prompt=prompt,
                    system=HR_QUESTION_SYSTEM_PROMPT,
                    json_mode=True,
                )
                cleaned_json = _strip_json_fences(raw_json)
                data = json.loads(cleaned_json)
                parsed = _GeneratedHRQuestionPayload.model_validate(data)
                cleaned_text = _clean_question_text(parsed.question_text)

                if len(cleaned_text.split()) < 6:
                    continue

                fp = compute_question_fingerprint(cat_name, cleaned_text)
                if fp in fingerprints:
                    continue

                if previous_questions:
                    is_dup, _ = is_duplicate_or_paraphrase(
                        candidate_text=cleaned_text,
                        candidate_topic=cat_name,
                        previous_questions=previous_questions,
                        asked_fingerprints=fingerprints,
                    )
                    if is_dup:
                        continue

                return InterviewQuestion(
                    question_id=question_id,
                    topic=cat_name,
                    difficulty=calibrated_diff,
                    question_text=cleaned_text,
                    question_type="conceptual",
                    is_follow_up=False,
                )
            except (LLMError, json.JSONDecodeError, ValidationError) as exc:
                logger.warning(
                    "HR question generation attempt %d failed: %s",
                    attempt + 1,
                    exc,
                )

    # Curated fallback
    curated = pick_curated_hr_question(
        category=cat_name,  # type: ignore[arg-type]
        difficulty=calibrated_diff,
        experience_level=norm_level,
        previous_questions=previous_questions,
    )
    return InterviewQuestion(
        question_id=question_id,
        topic=curated.category,
        difficulty=curated.difficulty,
        question_text=curated.question_text,
        question_type="conceptual",
        is_follow_up=False,
    )


async def generate_hr_follow_up(
    *,
    provider: LLMProvider | None,
    question_id: str,
    target_role: str,
    category: str,
    difficulty: str,
    previous_question: str,
    candidate_answer: str,
    evaluation: dict[str, Any],
    experience_level: str = DEFAULT_EXPERIENCE_LEVEL,
    follow_up_type: str | None = None,
) -> InterviewQuestion:
    """Generate a targeted, contextual HR follow-up question."""
    norm_level = normalize_experience_level(experience_level)
    level_label = EXPERIENCE_LEVEL_LABELS[norm_level]
    calibrated_diff = _normalize_difficulty(difficulty)
    fu_type = follow_up_type or "clarification"

    eval_summary = (
        f"Reasoning score: {evaluation.get('overall_score')}, "
        f"Reason for follow up: {evaluation.get('follow_up_reason', 'Probe deeper')}"
    )

    prompt = HR_FOLLOW_UP_USER_PROMPT.format(
        target_role=target_role,
        experience_level_label=level_label,
        category=category,
        previous_question=previous_question,
        candidate_answer=candidate_answer,
        evaluation_summary=eval_summary,
        follow_up_type=fu_type,
    )

    if provider is not None:
        try:
            raw_json = await provider.generate(
                prompt=prompt,
                system=HR_FOLLOW_UP_SYSTEM_PROMPT,
                json_mode=True,
            )
            cleaned_json = _strip_json_fences(raw_json)
            data = json.loads(cleaned_json)
            parsed = _GeneratedHRFollowUpPayload.model_validate(data)
            cleaned_text = _clean_question_text(parsed.question_text)

            if len(cleaned_text.split()) >= 5:
                return InterviewQuestion(
                    question_id=question_id,
                    topic=category,
                    difficulty=calibrated_diff,
                    question_text=cleaned_text,
                    question_type="follow_up",
                    is_follow_up=True,
                )
        except Exception as exc:
            logger.warning("HR follow-up generation failed: %s", exc)

    # Curated contextual fallback based on intent
    fallbacks = {
        "trade_off_exploration": (
            "What alternative approaches or trade-offs did you consider before settling on that course of action?"
        ),
        "alternative_perspective": (
            "If a key teammate or stakeholder strongly pushed back on your chosen direction, how would you address their concerns?"
        ),
        "outcome_analysis": (
            "How did you evaluate or measure whether your decision ultimately produced the desired outcome?"
        ),
        "reflection": (
            "Looking back with hindsight, is there anything you would approach differently if faced with the same situation today?"
        ),
        "clarification": (
            "Could you elaborate on your specific personal contribution and the immediate impact of your decision?"
        ),
    }

    fallback_text = fallbacks.get(fu_type, fallbacks["clarification"])
    return InterviewQuestion(
        question_id=question_id,
        topic=category,
        difficulty=calibrated_diff,
        question_text=fallback_text,
        question_type="follow_up",
        is_follow_up=True,
    )
