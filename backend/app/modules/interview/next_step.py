"""Pure transition logic for deciding follow-up vs next question vs completion."""

from typing import Any, Literal

from app.modules.interview.adaptive import FollowUpType, plan_follow_up

NextAction = Literal["follow_up", "next_question", "complete"]


def decide_next_action(
    evaluation: dict[str, Any] | None,
    follow_up_count: int,
    max_follow_ups: int,
    question_index: int,
    max_questions: int,
) -> NextAction:
    """Decide whether to ask a follow-up, advance, or complete the interview."""
    follow_up_needed = bool((evaluation or {}).get("follow_up_needed", False))

    if follow_up_needed and follow_up_count < max_follow_ups:
        return "follow_up"

    if question_index >= max_questions:
        return "complete"

    return "next_question"


def decide_adaptive_next_step(
    *,
    evaluation: dict[str, Any] | None,
    follow_up_count: int,
    max_follow_ups: int,
    question_index: int,
    max_questions: int,
    question_type: str,
    current_difficulty: str,
) -> tuple[NextAction, FollowUpType | None, str | None]:
    """Use evaluation context and limits to choose next_action and follow-up intent."""
    should_fu, fu_type, fu_reason = plan_follow_up(
        evaluation=evaluation,
        follow_up_count=follow_up_count,
        max_follow_ups=max_follow_ups,
        question_type=question_type,
        current_difficulty=current_difficulty,
    )
    if should_fu:
        return "follow_up", fu_type, fu_reason

    if question_index >= max_questions:
        return "complete", None, None

    return "next_question", None, None
