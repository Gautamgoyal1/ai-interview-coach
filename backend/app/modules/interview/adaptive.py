"""Performance-based adaptive difficulty and intelligent follow-up planning."""

from typing import Any, Literal

from app.modules.interview.calibration import (
    Difficulty,
    ExperienceLevel,
    normalize_experience_level,
)

DIFFICULTY_TO_LEVEL: dict[Difficulty, int] = {
    "easy": 1,
    "medium": 2,
    "hard": 3,
}

LEVEL_TO_DIFFICULTY: dict[int, Difficulty] = {
    1: "easy",
    2: "medium",
    3: "hard",
}

STARTING_DIFFICULTY_BY_LEVEL: dict[ExperienceLevel, Difficulty] = {
    "internship": "easy",
    "fresher": "medium",
    "intermediate": "medium",
    "experienced": "medium",
}

DIFFICULTY_CEILING_BY_LEVEL: dict[ExperienceLevel, int] = {
    "internship": 2,  # medium
    "fresher": 3,     # hard
    "intermediate": 3,
    "experienced": 3,
}

FollowUpType = Literal[
    "clarification",
    "understanding_check",
    "deeper_exploration",
    "practical_application",
]


def starting_difficulty_for_level(experience_level: str | None) -> Difficulty:
    """Return the calibrated initial difficulty for an experience level."""
    level = normalize_experience_level(experience_level)
    return STARTING_DIFFICULTY_BY_LEVEL[level]


def difficulty_to_int(difficulty: str | None) -> int:
    cleaned = str(difficulty or "medium").strip().lower()
    return DIFFICULTY_TO_LEVEL.get(cleaned, 2)  # type: ignore[arg-type]


def int_to_difficulty(level_num: int) -> Difficulty:
    clamped = max(1, min(3, int(level_num)))
    return LEVEL_TO_DIFFICULTY[clamped]


def update_topic_performance(
    topic_performance: dict[str, Any],
    topic: str,
    score: float | None,
    difficulty: str,
) -> dict[str, Any]:
    """Update rolling per-topic mastery statistics without mutating input."""
    updated = {k: dict(v) for k, v in (topic_performance or {}).items()}
    key = topic.strip().lower() or "general"
    entry = dict(updated.get(key) or {})
    scores = list(entry.get("scores") or [])
    if score is not None:
        scores.append(round(float(score), 2))
    avg = round(sum(scores) / len(scores), 2) if scores else entry.get("avg_score")
    updated[key] = {
        "topic": topic,
        "scores": scores[-10:],
        "avg_score": avg,
        "attempts": int(entry.get("attempts", 0)) + 1,
        "last_difficulty": difficulty,
    }
    return updated


def compute_adaptive_update(
    *,
    current_difficulty: str,
    experience_level: str | None,
    evaluation: dict[str, Any] | None,
    recent_scores: list[float],
    consecutive_strong_answers: int,
    consecutive_weak_answers: int,
    topic_performance: dict[str, Any],
    topic: str,
    progression_mode: str = "adaptive",
    starting_difficulty: str | None = None,
) -> dict[str, Any]:
    """Deterministically compute next difficulty and adaptive tracking fields."""
    norm_exp = normalize_experience_level(experience_level)
    # Ensure ceiling accommodates candidate's explicit starting difficulty choice
    level_ceiling = DIFFICULTY_CEILING_BY_LEVEL[norm_exp]
    chosen_diff_int = difficulty_to_int(starting_difficulty) if starting_difficulty else 1
    ceiling = max(level_ceiling, chosen_diff_int)
    cur_level = min(ceiling, max(1, difficulty_to_int(current_difficulty)))

    updated_recent = list(recent_scores or [])
    strong_streak = int(consecutive_strong_answers or 0)
    weak_streak = int(consecutive_weak_answers or 0)

    # In mock assessment mode, difficulty stays stable at planned/starting difficulty
    if str(progression_mode).strip().lower() == "mock":
        score = evaluation.get("overall_score") if evaluation else None
        if isinstance(score, (int, float)):
            score_val = float(score)
            updated_recent.append(round(score_val, 2))
            updated_recent = updated_recent[-8:]
            updated_topics = update_topic_performance(
                topic_performance, topic, score_val, int_to_difficulty(cur_level)
            )
        else:
            updated_topics = update_topic_performance(
                topic_performance, topic, None, int_to_difficulty(cur_level)
            )
        stable_diff = starting_difficulty if starting_difficulty in {"easy", "medium", "hard"} else int_to_difficulty(cur_level)
        return {
            "next_difficulty": stable_diff,
            "recent_scores": updated_recent,
            "consecutive_strong_answers": strong_streak,
            "consecutive_weak_answers": weak_streak,
            "topic_performance": updated_topics,
        }

    if not evaluation or evaluation.get("grading_status") == "unavailable":
        updated_topics = update_topic_performance(
            topic_performance, topic, None, int_to_difficulty(cur_level)
        )
        return {
            "next_difficulty": int_to_difficulty(cur_level),
            "recent_scores": updated_recent,
            "consecutive_strong_answers": strong_streak,
            "consecutive_weak_answers": weak_streak,
            "topic_performance": updated_topics,
        }

    score = evaluation.get("overall_score")
    if not isinstance(score, (int, float)):
        updated_topics = update_topic_performance(
            topic_performance, topic, None, int_to_difficulty(cur_level)
        )
        return {
            "next_difficulty": int_to_difficulty(cur_level),
            "recent_scores": updated_recent,
            "consecutive_strong_answers": strong_streak,
            "consecutive_weak_answers": weak_streak,
            "topic_performance": updated_topics,
        }

    score_val = float(score)
    updated_recent.append(round(score_val, 2))
    updated_recent = updated_recent[-8:]
    updated_topics = update_topic_performance(
        topic_performance, topic, score_val, int_to_difficulty(cur_level)
    )

    tech_corr = (evaluation.get("technical_correctness") or {}).get("score")
    reasoning_corr = (evaluation.get("reasoning_critical_thinking") or {}).get("score")
    core_score = reasoning_corr if reasoning_corr is not None else tech_corr
    missing_concepts = list(evaluation.get("missing_concepts") or [])

    next_level = cur_level
    if score_val >= 85.0:
        strong_streak += 1
        weak_streak = 0
        # Require 2 consecutive strong answers before advancing difficulty.
        if strong_streak >= 2 and cur_level < ceiling:
            next_level = cur_level + 1
            strong_streak = 0  # Reset after stepping up to avoid rapid oscillation
    elif score_val >= 65.0:
        strong_streak = 0
        weak_streak = 0
    elif score_val >= 40.0:
        strong_streak = 0
        has_major_gap = (
            (isinstance(core_score, (int, float)) and core_score <= 2.0)
            or len(missing_concepts) >= 2
            or weak_streak >= 1
        )
        if has_major_gap:
            weak_streak += 1
            if cur_level > 1:
                next_level = cur_level - 1
        else:
            weak_streak = 0
    else:
        strong_streak = 0
        weak_streak += 1
        if cur_level > 1:
            next_level = cur_level - 1

    next_level = max(1, min(ceiling, next_level))

    return {
        "next_difficulty": int_to_difficulty(next_level),
        "recent_scores": updated_recent,
        "consecutive_strong_answers": strong_streak,
        "consecutive_weak_answers": weak_streak,
        "topic_performance": updated_topics,
    }


def difficulty_for_next_topic(
    *,
    global_difficulty: str,
    next_topic: str,
    last_topic: str,
    consecutive_weak_answers: int,
    recent_scores: list[float],
    topic_performance: dict[str, Any],
    experience_level: str | None,
) -> Difficulty:
    """Adjust difficulty for a new topic without letting one weak topic drag down strong areas."""
    norm_exp = normalize_experience_level(experience_level)
    ceiling = DIFFICULTY_CEILING_BY_LEVEL[norm_exp]
    base_level = min(ceiling, max(1, difficulty_to_int(global_difficulty)))

    topic_key = next_topic.strip().lower()
    topic_entry = (topic_performance or {}).get(topic_key)
    if topic_entry and isinstance(topic_entry.get("avg_score"), (int, float)):
        t_avg = float(topic_entry["avg_score"])
        if t_avg >= 85.0 and base_level < ceiling:
            return int_to_difficulty(base_level + 1)
        if t_avg < 45.0 and base_level > 1:
            return int_to_difficulty(base_level - 1)

    # If switching to a different topic after a single isolated weak answer,
    # keep medium when overall recent performance is otherwise solid (>= 65).
    if (
        topic_key != last_topic.strip().lower()
        and base_level == 1
        and consecutive_weak_answers <= 1
        and len(recent_scores) >= 2
    ):
        prior_scores = recent_scores[:-1]
        if prior_scores and (sum(prior_scores) / len(prior_scores)) >= 65.0:
            return "medium"

    return int_to_difficulty(base_level)


def plan_follow_up(
    *,
    evaluation: dict[str, Any] | None,
    follow_up_count: int,
    max_follow_ups: int,
    question_type: str,
    current_difficulty: str,
) -> tuple[bool, FollowUpType | None, str | None]:
    """Decide whether a follow-up adds conversational value and classify its intent."""
    if follow_up_count >= max_follow_ups:
        return False, None, None

    if not evaluation:
        return False, None, None

    if evaluation.get("grading_status") == "unavailable":
        if evaluation.get("follow_up_needed"):
            return (
                True,
                "clarification",
                str(evaluation.get("follow_up_reason") or "Clarify brief response."),
            )
        return False, None, None

    score = evaluation.get("overall_score")
    if not isinstance(score, (int, float)):
        return False, None, None

    score_val = float(score)
    tech_corr = (evaluation.get("technical_correctness") or {}).get("score")
    completeness = (evaluation.get("completeness") or {}).get("score")
    tech_depth = (evaluation.get("technical_depth") or {}).get("score")
    missing = list(evaluation.get("missing_concepts") or [])
    llm_flag = bool(evaluation.get("follow_up_needed", False))
    llm_reason = str(evaluation.get("follow_up_reason") or "").strip()
    llm_type = evaluation.get("follow_up_type")

    # If the evaluator explicitly specified a behavioral follow-up intent, honor it
    if llm_flag and llm_type:
        return (
            True,
            llm_type,
            llm_reason or f"Probe further with {llm_type}.",
        )

    # 1. Weak or confused answer -> gentle understanding check
    if score_val < 50.0 or (isinstance(tech_corr, (int, float)) and tech_corr <= 2.0):
        return (
            True,
            "understanding_check",
            llm_reason or "Check understanding with a concrete, approachable example.",
        )

    # 2. Partially correct answer with missing concepts -> targeted clarification
    if score_val < 75.0 and (missing or (isinstance(completeness, (int, float)) and completeness <= 3.0)):
        return (
            True,
            "clarification",
            llm_reason or f"Clarify missing concept: {missing[0]}" if missing else "Clarify missing detail.",
        )

    # 3. Strong answer -> deeper exploration when evaluator flags it or depth is below 4
    if score_val >= 82.0 and (
        llm_flag or (isinstance(tech_depth, (int, float)) and tech_depth < 4.0)
    ):
        return (
            True,
            "deeper_exploration",
            llm_reason or "Explore practical depth or real-world failure mode.",
        )

    # 4. Good conceptual answer -> practical application
    if 75.0 <= score_val < 82.0 and question_type == "conceptual" and llm_flag:
        return (
            True,
            "practical_application",
            llm_reason or "Connect the concept to a practical implementation scenario.",
        )

    # 5. Otherwise skip follow-up to maintain breadth and natural pacing
    return False, None, None
