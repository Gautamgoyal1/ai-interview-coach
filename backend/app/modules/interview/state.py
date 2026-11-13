"""Typed LangGraph state definition for the AI interview workflow."""

from typing import Any, TypedDict


class InterviewState(TypedDict):
    """Explicit state tracked across LangGraph nodes and persisted per session."""

    session_id: str
    user_id: int
    analysis_id: int
    target_role: str
    interview_type: str
    experience_level: str
    starting_difficulty: str
    progression_mode: str

    candidate_context: dict[str, Any]

    selected_topic: str
    question_focus: str
    retrieved_context: str
    retrieved_sources: list[dict[str, Any]]

    current_question: dict[str, Any] | None
    current_answer: str | None
    current_evaluation: dict[str, Any] | None
    next_action: str

    question_index: int
    max_questions: int

    follow_up_count: int
    max_follow_ups: int

    asked_topics: list[str]
    conversation_history: list[dict[str, Any]]
    evaluation_history: list[dict[str, Any]]

    # Adaptive assessment & deduplication tracking
    current_difficulty: str
    difficulty_history: list[str]
    recent_scores: list[float]
    consecutive_strong_answers: int
    consecutive_weak_answers: int
    topic_performance: dict[str, Any]
    asked_question_fingerprints: list[str]
    recent_cross_session_questions: list[str]
    last_evaluation: dict[str, Any] | None
    follow_up_reason: str | None
    follow_up_type: str | None

    status: str
