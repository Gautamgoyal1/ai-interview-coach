"""Database models for personalized practice sessions, questions, and attempts."""

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


class PracticeSession(Base):
    __tablename__ = "practice_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    interview_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="technical",
    )

    target_role: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        default="Software Engineer",
    )

    topic: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    source_report_id: Mapped[int | None] = mapped_column(
        ForeignKey("interview_reports.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    experience_level: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="fresher",
    )

    weakness_context: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="active",
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    questions: Mapped[list["PracticeQuestion"]] = relationship(
        "PracticeQuestion",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="PracticeQuestion.created_at",
    )


class PracticeQuestion(Base):
    __tablename__ = "practice_questions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    session_id: Mapped[str] = mapped_column(
        ForeignKey("practice_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    question_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    topic: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    difficulty: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="medium",
    )

    hints: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    reference_answer: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    reference_explanation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    hints_revealed: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    reference_revealed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    reference_revealed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    session: Mapped["PracticeSession"] = relationship(
        "PracticeSession",
        back_populates="questions",
    )

    attempts: Mapped[list["PracticeAttempt"]] = relationship(
        "PracticeAttempt",
        back_populates="question",
        cascade="all, delete-orphan",
        order_by="PracticeAttempt.attempt_number",
    )


class PracticeAttempt(Base):
    __tablename__ = "practice_attempts"
    __table_args__ = (
        UniqueConstraint(
            "question_id",
            "attempt_number",
            name="uq_practice_attempts_question_attempt",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    question_id: Mapped[str] = mapped_column(
        ForeignKey("practice_questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    attempt_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    answer_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    assistance_level: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="independent",
    )

    hints_used: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    reference_revealed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    feedback: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    question: Mapped["PracticeQuestion"] = relationship(
        "PracticeQuestion",
        back_populates="attempts",
    )
