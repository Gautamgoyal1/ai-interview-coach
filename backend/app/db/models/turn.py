"""Database model for individual interview questions, answers, and evaluations."""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class InterviewTurn(Base):
    __tablename__ = "interview_turns"
    __table_args__ = (
        UniqueConstraint(
            "session_id",
            "question_id",
            name="uq_interview_turns_session_question",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    session_id: Mapped[str] = mapped_column(
        ForeignKey("interview_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    question_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    question_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    is_follow_up: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    parent_question_id: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    topic: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    difficulty: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    question_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    question_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    rag_sources: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    answer_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    evaluation: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    answered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    session: Mapped["InterviewSession"] = relationship(
        back_populates="turns",
    )
