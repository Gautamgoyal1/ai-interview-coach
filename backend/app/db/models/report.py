"""Database model for persisted interview evaluation reports."""

from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class InterviewReport(Base):
    __tablename__ = "interview_reports"

    id: Mapped[int] = mapped_column(primary_key=True)

    session_id: Mapped[str] = mapped_column(
        ForeignKey("interview_sessions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
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

    overall_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    dimension_scores: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    topic_scores: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    strengths: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    weaknesses: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    missing_concepts: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    recommendations: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    question_feedback: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    completion_stats: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    evaluation_coverage: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    rubric_version: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    rubric_weights: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="pending",
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
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
