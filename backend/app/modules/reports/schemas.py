"""Pydantic schemas for interview evaluation reports."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class DimensionSummary(BaseModel):
    """Aggregated rubric dimension score."""

    dimension: str
    label: str
    weight: float
    average_score: float | None = None
    percentage: float | None = None
    evaluated_count: int = 0


class TopicPerformance(BaseModel):
    """Aggregated performance for a technical topic covered in the interview."""

    topic: str
    score: float | None = None
    questions_asked: int
    evaluated_questions: int


class RecommendationItem(BaseModel):
    """Actionable preparation recommendation grounded in observed gaps."""

    model_config = ConfigDict(extra="ignore")

    area: str
    observed_gap: str
    action: str
    priority: Literal["high", "medium", "low"] = "medium"


class QuestionFeedbackItem(BaseModel):
    """Question-by-question feedback preserving follow-up parent linkage."""

    question_id: str
    question_index: int
    is_follow_up: bool
    parent_question_id: str | None = None
    topic: str
    difficulty: str
    question_text: str
    answer_text: str | None = None
    overall_score: float | None = None
    grading_status: str
    dimension_scores: dict[str, dict] = Field(default_factory=dict)
    strengths: list[str] = Field(default_factory=list)
    missing_concepts: list[str] = Field(default_factory=list)
    improvement_suggestions: list[str] = Field(default_factory=list)


class CompletionStats(BaseModel):
    questions_answered: int
    primary_questions_completed: int
    follow_ups_answered: int
    total_primary_questions: int


class EvaluationCoverage(BaseModel):
    evaluated_count: int
    unavailable_count: int
    total_answered: int
    coverage_ratio: float
    is_partial: bool


class InterviewReportResponse(BaseModel):
    """Full interview performance report returned to the authenticated user."""

    id: int
    session_id: str
    target_role: str
    interview_type: Literal["technical", "hr"] = "technical"
    interview_date: datetime
    status: Literal["pending", "processing", "completed", "partial", "failed"]
    overall_score: float | None = None
    dimension_scores: dict[str, DimensionSummary] = Field(default_factory=dict)
    topic_scores: list[TopicPerformance] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    missing_concepts: list[str] = Field(default_factory=list)
    recommendations: list[RecommendationItem] = Field(default_factory=list)
    question_feedback: list[QuestionFeedbackItem] = Field(default_factory=list)
    completion_stats: CompletionStats
    evaluation_coverage: EvaluationCoverage
    rubric_version: str
    rubric_weights: dict[str, float]
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime


class InterviewReportSummary(BaseModel):
    """Compact entry for a user's interview report history."""

    id: int
    session_id: str
    target_role: str
    interview_type: Literal["technical", "hr"] = "technical"
    interview_date: datetime
    status: str
    overall_score: float | None = None
    rubric_version: str
    created_at: datetime
