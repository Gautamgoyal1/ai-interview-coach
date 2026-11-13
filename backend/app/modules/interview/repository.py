"""Database repository for interview sessions, turns, and ownership checks."""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.db.models.interview_session import InterviewSession
from app.db.models.resume import Resume, ResumeAnalysis
from app.db.models.turn import InterviewTurn


def get_owned_resume_analysis(
    db: Session,
    analysis_id: int,
    user_id: int,
) -> tuple[ResumeAnalysis, Resume] | None:
    """Return (ResumeAnalysis, Resume) only if owned by user_id."""
    return (
        db.query(ResumeAnalysis, Resume)
        .join(Resume, Resume.id == ResumeAnalysis.resume_id)
        .filter(
            ResumeAnalysis.id == analysis_id,
            Resume.user_id == user_id,
            ResumeAnalysis.deleted_at.is_(None),
            ResumeAnalysis.status == "completed",
        )
        .first()
    )


def create_interview_session(
    db: Session,
    session_id: str,
    user_id: int,
    analysis_id: int,
    target_role: str,
    max_questions: int,
    max_follow_ups: int,
    configuration: dict[str, Any],
    graph_state: dict[str, Any],
    interview_type: str = "technical",
) -> InterviewSession:
    """Persist a new interview session."""
    session = InterviewSession(
        id=session_id,
        user_id=user_id,
        resume_analysis_id=analysis_id,
        target_role=target_role,
        interview_type=interview_type,
        status="in_progress",
        question_index=1,
        max_questions=max_questions,
        follow_up_count=0,
        max_follow_ups=max_follow_ups,
        configuration=configuration,
        graph_state=graph_state,
    )
    db.add(session)
    db.flush()
    return session


def get_owned_session(
    db: Session,
    session_id: str,
    user_id: int,
) -> InterviewSession | None:
    """Return an InterviewSession only if it belongs to user_id."""
    return (
        db.query(InterviewSession)
        .filter(
            InterviewSession.id == session_id,
            InterviewSession.user_id == user_id,
        )
        .first()
    )


def list_session_turns(
    db: Session,
    session_id: str,
) -> list[InterviewTurn]:
    """Return all turns for a session in chronological order."""
    return (
        db.query(InterviewTurn)
        .filter(InterviewTurn.session_id == session_id)
        .order_by(InterviewTurn.id.asc())
        .all()
    )


def create_question_turn(
    db: Session,
    session_id: str,
    question: dict[str, Any],
    question_index: int,
    rag_sources: list[dict[str, Any]],
    parent_question_id: str | None = None,
) -> InterviewTurn:
    """Persist a newly generated interview question turn if not already present."""
    existing = (
        db.query(InterviewTurn)
        .filter(
            InterviewTurn.session_id == session_id,
            InterviewTurn.question_id == question["question_id"],
        )
        .first()
    )
    if existing is not None:
        return existing

    turn = InterviewTurn(
        session_id=session_id,
        question_id=question["question_id"],
        question_index=question_index,
        is_follow_up=bool(question.get("is_follow_up", False)),
        parent_question_id=parent_question_id,
        topic=question["topic"],
        difficulty=question["difficulty"],
        question_type=question["question_type"],
        question_text=question["question_text"],
        rag_sources=rag_sources,
    )
    db.add(turn)
    db.flush()
    return turn


def get_turn_by_question_id(
    db: Session,
    session_id: str,
    question_id: str,
) -> InterviewTurn | None:
    """Fetch a specific turn within a session."""
    return (
        db.query(InterviewTurn)
        .filter(
            InterviewTurn.session_id == session_id,
            InterviewTurn.question_id == question_id,
        )
        .first()
    )


def record_turn_answer(
    db: Session,
    turn: InterviewTurn,
    answer_text: str,
    evaluation: dict[str, Any] | None,
) -> InterviewTurn:
    """Persist the candidate's answer and internal evaluation on a turn."""
    turn.answer_text = answer_text
    turn.evaluation = evaluation
    turn.answered_at = datetime.now(timezone.utc)
    db.flush()
    return turn


def list_recent_user_questions(
    db: Session,
    user_id: int,
    target_role: str | None = None,
    limit: int = 40,
) -> list[dict[str, str]]:
    """Return recent primary questions asked to this user (never cross-user)."""
    query = (
        db.query(InterviewTurn.topic, InterviewTurn.question_text)
        .join(InterviewSession, InterviewSession.id == InterviewTurn.session_id)
        .filter(
            InterviewSession.user_id == user_id,
            InterviewTurn.is_follow_up.is_(False),
        )
    )
    if target_role and target_role.strip():
        query = query.filter(InterviewSession.target_role == target_role.strip())

    rows = query.order_by(InterviewTurn.id.desc()).limit(limit).all()
    return [
        {"topic": str(topic), "question_text": str(question_text)}
        for topic, question_text in rows
        if question_text
    ]
