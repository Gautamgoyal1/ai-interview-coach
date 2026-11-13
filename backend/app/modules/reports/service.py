"""Service layer for idempotent interview report generation and retrieval."""

import logging
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models.report import InterviewReport
from app.integrations.llm.base import LLMProvider
from app.modules.interview.repository import (
    get_owned_session,
    list_session_turns,
)
from app.modules.interview.rubric import (
    HR_RUBRIC_VERSION,
    HR_RUBRIC_WEIGHTS,
    RUBRIC_VERSION,
    RUBRIC_WEIGHTS,
)
from app.modules.knowledge.retriever import retrieve_chunks_async
from app.modules.reports.analyzer import analyze_interview_performance
from app.modules.reports.generator import generate_recommendations
from app.modules.reports.repository import (
    get_report_by_session,
    list_user_reports,
)
from app.modules.reports.schemas import (
    CompletionStats,
    DimensionSummary,
    EvaluationCoverage,
    InterviewReportResponse,
    InterviewReportSummary,
    QuestionFeedbackItem,
    RecommendationItem,
    TopicPerformance,
)
from app.modules.reports.scoring import aggregate_interview_scores

logger = logging.getLogger(__name__)


def _to_response(
    report: InterviewReport,
    interview_date: datetime,
) -> InterviewReportResponse:
    iv_type = getattr(report, "interview_type", None) or "technical"
    return InterviewReportResponse(
        id=report.id,
        session_id=report.session_id,
        target_role=report.target_role,
        interview_type=iv_type,
        interview_date=interview_date,
        status=report.status,  # type: ignore[arg-type]
        overall_score=report.overall_score,
        dimension_scores={
            k: DimensionSummary.model_validate(v)
            for k, v in (report.dimension_scores or {}).items()
        },
        topic_scores=[
            TopicPerformance.model_validate(item)
            for item in (report.topic_scores or [])
        ],
        strengths=list(report.strengths or []),
        weaknesses=list(report.weaknesses or []),
        missing_concepts=list(report.missing_concepts or []),
        recommendations=[
            RecommendationItem.model_validate(item)
            for item in (report.recommendations or [])
        ],
        question_feedback=[
            QuestionFeedbackItem.model_validate(item)
            for item in (report.question_feedback or [])
        ],
        completion_stats=CompletionStats.model_validate(
            report.completion_stats
            or {
                "questions_answered": 0,
                "primary_questions_completed": 0,
                "follow_ups_answered": 0,
                "total_primary_questions": 0,
            }
        ),
        evaluation_coverage=EvaluationCoverage.model_validate(
            report.evaluation_coverage
            or {
                "evaluated_count": 0,
                "unavailable_count": 0,
                "total_answered": 0,
                "coverage_ratio": 0.0,
                "is_partial": True,
            }
        ),
        rubric_version=report.rubric_version,
        rubric_weights=dict(report.rubric_weights or {}),
        error_message=report.error_message,
        created_at=report.created_at,
        updated_at=report.updated_at,
    )


class ReportService:
    """Orchestrates deterministic scoring, analysis, and report persistence."""

    def __init__(self, llm_provider: LLMProvider | None = None) -> None:
        self.llm_provider = llm_provider

    async def generate_report(
        self,
        db: Session,
        user_id: int,
        session_id: str,
    ) -> InterviewReportResponse:
        session = get_owned_session(db, session_id, user_id)
        if session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found.",
            )

        if session.status != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot generate a report while the interview is still in progress.",
            )

        existing = get_report_by_session(db, session_id, user_id)
        if existing is not None and existing.status in {"completed", "partial"}:
            return _to_response(existing, session.started_at)

        turns = list_session_turns(db, session_id)
        session_iv_type = getattr(session, "interview_type", None) or (
            session.configuration or {}
        ).get("interview_type", "technical")
        is_hr = str(session_iv_type).strip().lower() == "hr"
        target_rubric_version = HR_RUBRIC_VERSION if is_hr else RUBRIC_VERSION
        target_rubric_weights = (
            dict(HR_RUBRIC_WEIGHTS) if is_hr else dict(RUBRIC_WEIGHTS)
        )

        bundle = aggregate_interview_scores(
            turns=turns,
            total_primary_questions=session.max_questions,
            interview_type=session_iv_type,
            rubric_version=target_rubric_version,
        )
        insights = analyze_interview_performance(
            question_feedback=bundle.question_feedback,
            topic_scores=bundle.topic_scores,
        )

        retrieved_context = ""
        if not is_hr and (insights.missing_concepts or insights.weaknesses):
            query = f"{session.target_role} {' '.join(insights.missing_concepts[:3])}".strip()
            try:
                chunks = await retrieve_chunks_async(db=db, query=query, top_k=2)
                retrieved_context = "\n".join(c.content.strip() for c in chunks)
            except Exception:
                retrieved_context = ""

        recommendations = await generate_recommendations(
            provider=self.llm_provider,
            target_role=session.target_role,
            weaknesses=insights.weaknesses,
            missing_concepts=insights.missing_concepts,
            topic_scores=bundle.topic_scores,
            retrieved_context=retrieved_context,
        )

        final_status = (
            "partial" if bundle.evaluation_coverage.is_partial else "completed"
        )

        report = existing or InterviewReport(
            session_id=session.id,
            user_id=user_id,
            target_role=session.target_role,
            interview_type=session_iv_type,
            rubric_version=target_rubric_version,
            rubric_weights=target_rubric_weights,
        )
        report.target_role = session.target_role
        report.interview_type = session_iv_type
        report.overall_score = bundle.overall_score
        report.dimension_scores = {
            k: v.model_dump() for k, v in bundle.dimension_scores.items()
        }
        report.topic_scores = [t.model_dump() for t in bundle.topic_scores]
        report.strengths = insights.strengths
        report.weaknesses = insights.weaknesses
        report.missing_concepts = insights.missing_concepts
        report.recommendations = [r.model_dump() for r in recommendations]
        report.question_feedback = [
            q.model_dump() for q in bundle.question_feedback
        ]
        report.completion_stats = bundle.completion_stats.model_dump()
        report.evaluation_coverage = bundle.evaluation_coverage.model_dump()
        report.rubric_version = target_rubric_version
        report.rubric_weights = target_rubric_weights
        report.status = final_status
        report.error_message = None

        if existing is None:
            db.add(report)

        try:
            db.commit()
            db.refresh(report)
        except IntegrityError:
            db.rollback()
            concurrent = get_report_by_session(db, session_id, user_id)
            if concurrent is not None:
                return _to_response(concurrent, session.started_at)
            raise

        return _to_response(report, session.started_at)

    def get_report(
        self,
        db: Session,
        user_id: int,
        session_id: str,
    ) -> InterviewReportResponse:
        session = get_owned_session(db, session_id, user_id)
        if session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found.",
            )

        report = get_report_by_session(db, session_id, user_id)
        if report is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview report has not been generated yet.",
            )

        return _to_response(report, session.started_at)

    def list_reports(
        self,
        db: Session,
        user_id: int,
        limit: int = 20,
    ) -> list[InterviewReportSummary]:
        reports = list_user_reports(db, user_id=user_id, limit=limit)
        summaries: list[InterviewReportSummary] = []
        for rep in reports:
            sess = get_owned_session(db, rep.session_id, user_id)
            interview_date = sess.started_at if sess is not None else rep.created_at
            summaries.append(
                InterviewReportSummary(
                    id=rep.id,
                    session_id=rep.session_id,
                    target_role=rep.target_role,
                    interview_type=getattr(rep, "interview_type", "technical"),
                    interview_date=interview_date,
                    status=rep.status,
                    overall_score=rep.overall_score,
                    rubric_version=rep.rubric_version,
                    created_at=rep.created_at,
                )
            )
        return summaries

    def delete_report(
        self,
        db: Session,
        user_id: int,
        session_id: str,
    ) -> dict:
        """Delete only the interview report, preserving the underlying interview session."""
        session = get_owned_session(db, session_id, user_id)
        if session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found.",
            )

        report = get_report_by_session(db, session_id, user_id)
        if report is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview report not found.",
            )

        db.delete(report)
        db.commit()
        return {"deleted": True, "session_id": session_id}
