
"""Pydantic schemas for resume analysis and saved history."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ResumeAnalysisRequest(BaseModel):
    job_role: str = Field(
        min_length=2,
        max_length=150,
        description="Target job role, e.g. Machine Learning Engineer",
    )
    job_description: str | None = Field(
        default=None,
        max_length=15000,
        description="Optional job description for more precise matching",
    )


class ResumeAnalysisResult(BaseModel):
    job_role: str
    resume_skills: list[str]
    matched_skills: list[str]
    missing_skills: list[str]
    match_score: float = Field(ge=0, le=100)
    strengths: list[str]
    improvement_suggestions: list[str]
    likely_interview_questions: list[str]


class AnalyzeResumeResponse(ResumeAnalysisResult):
    """Extended response returned by POST /resume/analyze with deduplication metadata."""

    analysis_id: int | None = None
    reused: bool = False
    version: int = 1
    status: str = "completed"
    skill_evidence: dict[str, str] = Field(default_factory=dict)


class ResumeAnalysisHistoryItem(BaseModel):
    """Compact entry for a user's resume analysis history."""

    id: int
    filename: str
    job_role: str
    created_at: datetime
    match_score: float = Field(ge=0, le=100)
    version: int = 1
    interview_count: int = 0


class SavedResumeAnalysis(BaseModel):
    """Complete saved analysis with its resume metadata."""

    id: int
    filename: str
    created_at: datetime
    version: int = 1
    interview_count: int = 0
    skill_evidence: dict[str, str] = Field(default_factory=dict)
    result: ResumeAnalysisResult


class DeleteAnalysisResponse(BaseModel):
    """Outcome of deleting or archiving a saved resume analysis."""

    deleted: bool
    analysis_id: int
    mode: Literal["archived", "permanent"]
    dependent_interviews: int = 0
