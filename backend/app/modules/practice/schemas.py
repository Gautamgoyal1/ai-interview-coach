"""Pydantic schemas for the personalized practice mode and AI answer coach."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class CreatePracticeSessionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    topic: str = Field(min_length=2, max_length=150)
    interview_type: Literal["technical", "hr"] = "technical"
    target_role: str = Field(default="Software Engineer", max_length=150)
    experience_level: str = Field(default="fresher", max_length=50)
    source_report_id: int | None = None
    weakness_context: str | None = Field(default=None, max_length=1000)
    difficulty: Literal["easy", "medium", "hard"] = "medium"


class GeneratePracticeQuestionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    difficulty: Literal["easy", "medium", "hard"] | None = None
    focus_concept: str | None = Field(default=None, max_length=200)


class SubmitPracticeAttemptRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answer_text: str = Field(min_length=1, max_length=8000)


class PracticeFeedback(BaseModel):
    model_config = ConfigDict(extra="ignore")

    correct_points: list[str] = Field(default_factory=list)
    missing_points: list[str] = Field(default_factory=list)
    improvement_suggestions: list[str] = Field(default_factory=list)
    suggested_structure: list[str] = Field(default_factory=list)
    improved_example_answer: str = ""
    next_action: str = ""
    evaluation_status: Literal["completed", "unavailable"] = "completed"
    evaluation_confidence: Literal["high", "medium", "low", "unavailable"] = "medium"
    improvements_from_previous: list[str] = Field(default_factory=list)


class PracticeAttemptResponse(BaseModel):
    id: str
    question_id: str
    attempt_number: int
    answer_text: str
    assistance_level: Literal["independent", "hint_assisted", "reference_assisted"]
    hints_used: list[int]
    reference_revealed: bool
    feedback: PracticeFeedback
    created_at: datetime


class PracticeQuestionResponse(BaseModel):
    id: str
    session_id: str
    question_text: str
    topic: str
    difficulty: str
    hints_revealed: list[int]
    revealed_hints: dict[str, str]
    reference_revealed: bool
    reference_answer: str | None
    reference_explanation: str | None
    attempts: list[PracticeAttemptResponse] = Field(default_factory=list)
    created_at: datetime


class PracticeSessionDetailResponse(BaseModel):
    id: str
    user_id: int
    interview_type: str
    target_role: str
    topic: str
    source_report_id: int | None
    experience_level: str
    weakness_context: str | None
    status: str
    questions: list[PracticeQuestionResponse]
    created_at: datetime
    updated_at: datetime


class PracticeSessionSummaryResponse(BaseModel):
    id: str
    interview_type: str
    target_role: str
    topic: str
    source_report_id: int | None
    status: str
    question_count: int
    attempt_count: int
    latest_attempt_at: datetime | None
    created_at: datetime


class RevealHintResponse(BaseModel):
    question_id: str
    level: int
    hint_text: str
    hints_revealed: list[int]
    assistance_level: Literal["independent", "hint_assisted", "reference_assisted"]


class RevealReferenceResponse(BaseModel):
    question_id: str
    reference_answer: str
    reference_explanation: str | None
    reference_revealed: bool
    assistance_level: Literal["independent", "hint_assisted", "reference_assisted"]


class PracticeRecommendationItem(BaseModel):
    topic: str
    interview_type: str
    target_role: str
    observed_gap: str
    suggested_action: str
    source_report_id: int
    priority: str
