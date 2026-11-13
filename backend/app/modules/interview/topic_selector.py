"""Topic selection grounded in role fundamentals, resume skills, projects, and gaps."""

from typing import Any

from app.modules.interview.calibration import (
    QuestionFocus,
    category_for_question,
)
from app.modules.interview.question_bank import (
    ROLE_FUNDAMENTAL_TOPICS,
    get_role_fundamental_topics,
)

ROLE_FALLBACK_TOPICS: dict[str, list[str]] = ROLE_FUNDAMENTAL_TOPICS

GENERIC_FALLBACK_TOPICS = [
    "Core Programming",
    "Data Structures & Algorithms",
    "Database Design",
    "System Architecture",
    "Debugging & Testing",
    "Deployment & Reliability",
]


def _deduplicate_preserving_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for raw in items:
        cleaned = str(raw).strip()
        if not cleaned:
            continue
        key = cleaned.lower()
        if key not in seen:
            seen.add(key)
            ordered.append(cleaned)
    return ordered


def _first_unasked(candidates: list[str], asked_lower: set[str]) -> str | None:
    for topic in candidates:
        if topic.lower() not in asked_lower:
            return topic
    return None


def select_next_topic(
    candidate_context: dict[str, Any],
    asked_topics: list[str],
    question_index: int,
) -> tuple[str, str]:
    """Select the next interview topic and question focus from candidate profile.

    Returns (topic, question_type) where question_type is one of
    'applied', 'conceptual', or 'gap_probe'.
    """
    matched = list(candidate_context.get("matched_skills") or [])
    demonstrated = list(candidate_context.get("resume_skills") or [])
    missing = list(candidate_context.get("missing_skills") or [])
    role = str(candidate_context.get("target_role") or "").strip()
    role_defaults = get_role_fundamental_topics(role)

    # Alternate between demonstrated/matched skills and skill gaps for balanced coverage.
    prefer_gap = question_index % 3 == 0 and len(missing) > 0

    asked_lower = {t.strip().lower() for t in asked_topics if t}

    if prefer_gap:
        gap_candidates = _deduplicate_preserving_order(missing)
        for topic in gap_candidates:
            if topic.lower() not in asked_lower:
                return topic, "gap_probe"

    strength_candidates = _deduplicate_preserving_order(
        matched + demonstrated + missing + role_defaults
    )
    for topic in strength_candidates:
        if topic.lower() not in asked_lower:
            q_type = (
                "gap_probe"
                if topic.lower() in {m.lower() for m in missing}
                else ("applied" if question_index % 2 == 1 else "conceptual")
            )
            return topic, q_type

    # All candidate topics were covered; cycle cleanly.
    pool = strength_candidates or GENERIC_FALLBACK_TOPICS
    topic = pool[(max(question_index, 1) - 1) % len(pool)]
    return topic, "conceptual"


def select_topic_with_focus(
    candidate_context: dict[str, Any],
    asked_topics: list[str],
    question_index: int,
    max_questions: int = 8,
) -> tuple[str, str, QuestionFocus]:
    """Select (topic, question_type, question_focus) using a balanced 40/30/20/10 mix."""
    focus = category_for_question(
        question_index=question_index,
        max_questions=max_questions,
        candidate_context=candidate_context,
    )

    role = str(candidate_context.get("target_role") or "").strip()
    fundamentals = _deduplicate_preserving_order(get_role_fundamental_topics(role))
    matched = list(candidate_context.get("matched_skills") or [])
    demonstrated = list(candidate_context.get("resume_skills") or [])
    resume_skills = _deduplicate_preserving_order(matched + demonstrated)
    missing = _deduplicate_preserving_order(list(candidate_context.get("missing_skills") or []))
    projects = _deduplicate_preserving_order(list(candidate_context.get("projects") or []))

    asked_lower = {t.strip().lower() for t in asked_topics if t}

    if focus == "fundamental":
        topic = _first_unasked(fundamentals, asked_lower)
        if topic:
            return topic, "conceptual", "fundamental"

    if focus == "resume_skill":
        topic = _first_unasked(resume_skills, asked_lower)
        if topic:
            return topic, "applied", "resume_skill"

    if focus == "project":
        project_pool = projects if projects else resume_skills
        topic = _first_unasked(project_pool, asked_lower)
        if topic:
            return topic, "applied", "project"

    if focus == "gap_probe":
        topic = _first_unasked(missing, asked_lower)
        if topic:
            return topic, "gap_probe", "gap_probe"

    # Fallback across unasked role fundamentals, resume skills, and gaps
    combined = _deduplicate_preserving_order(fundamentals + resume_skills + missing)
    fallback_topic = _first_unasked(combined, asked_lower)
    if fallback_topic:
        if fallback_topic.lower() in {m.lower() for m in missing}:
            return fallback_topic, "gap_probe", "gap_probe"
        if fallback_topic.lower() in {s.lower() for s in resume_skills}:
            return fallback_topic, "applied", "resume_skill"
        return fallback_topic, "conceptual", "fundamental"

    pool = combined or GENERIC_FALLBACK_TOPICS
    topic = pool[(max(question_index, 1) - 1) % len(pool)]
    return topic, "conceptual", "fundamental"
