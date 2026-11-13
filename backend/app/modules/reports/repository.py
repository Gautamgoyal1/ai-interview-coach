"""Database repository for interview report persistence and user isolation."""

from sqlalchemy.orm import Session

from app.db.models.report import InterviewReport


def get_report_by_session(
    db: Session,
    session_id: str,
    user_id: int,
) -> InterviewReport | None:
    """Return an InterviewReport only if owned by user_id."""
    return (
        db.query(InterviewReport)
        .filter(
            InterviewReport.session_id == session_id,
            InterviewReport.user_id == user_id,
        )
        .first()
    )


def list_user_reports(
    db: Session,
    user_id: int,
    limit: int = 20,
) -> list[InterviewReport]:
    """List interview reports belonging to user_id, newest first."""
    return (
        db.query(InterviewReport)
        .filter(InterviewReport.user_id == user_id)
        .order_by(InterviewReport.created_at.desc())
        .limit(limit)
        .all()
    )
