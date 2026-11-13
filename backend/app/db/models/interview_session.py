"""Database model for LangGraph-backed AI interview sessions."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    resume_analysis_id: Mapped[int] = mapped_column(
        ForeignKey("resume_analyses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    target_role: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    interview_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="technical",
    )

    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="in_progress",
    )

    question_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    max_questions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=8,
    )

    follow_up_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    max_follow_ups: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    configuration: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    graph_state: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    turns: Mapped[list["InterviewTurn"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="InterviewTurn.id",
    )
