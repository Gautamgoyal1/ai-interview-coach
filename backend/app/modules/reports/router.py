"""FastAPI endpoints for generating and retrieving interview reports."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.models.user import User
from app.db.session import get_db
from app.modules.reports.schemas import (
    InterviewReportResponse,
    InterviewReportSummary,
)
from app.modules.reports.service import ReportService

router = APIRouter(prefix="/reports", tags=["Reports"])
service = ReportService()


@router.post(
    "/interviews/{session_id}/generate",
    response_model=InterviewReportResponse,
)
async def generate_interview_report(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InterviewReportResponse:
    """Generate or retrieve an idempotent report for a completed interview."""
    return await service.generate_report(
        db=db,
        user_id=current_user.id,
        session_id=session_id,
    )


@router.get(
    "/interviews/{session_id}",
    response_model=InterviewReportResponse,
)
def get_interview_report(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InterviewReportResponse:
    """Retrieve an existing interview report belonging to the current user."""
    return service.get_report(
        db=db,
        user_id=current_user.id,
        session_id=session_id,
    )


@router.get(
    "",
    response_model=list[InterviewReportSummary],
)
def list_interview_reports(
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[InterviewReportSummary]:
    """List interview reports belonging to the authenticated user."""
    return service.list_reports(
        db=db,
        user_id=current_user.id,
        limit=limit,
    )


@router.delete("/interviews/{session_id}")
def delete_interview_report(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Delete an owned interview report while preserving the underlying interview."""
    return service.delete_report(
        db=db,
        user_id=current_user.id,
        session_id=session_id,
    )
