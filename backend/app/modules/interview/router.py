"""FastAPI endpoints for the LangGraph-based AI Interview Engine."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.models.user import User
from app.db.session import get_db
from app.modules.interview.schemas import (
    InterviewSessionResponse,
    StartInterviewRequest,
    SubmitAnswerRequest,
)
from app.modules.interview.service import InterviewService

router = APIRouter(prefix="/interview", tags=["Interview"])
service = InterviewService()


@router.post(
    "/start",
    response_model=InterviewSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def start_interview(
    request: StartInterviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InterviewSessionResponse:
    """Start a personalized AI interview session from a saved resume analysis."""
    return await service.start_interview(
        db=db,
        user_id=current_user.id,
        request=request,
    )


@router.get(
    "/{session_id}",
    response_model=InterviewSessionResponse,
)
def get_interview_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InterviewSessionResponse:
    """Retrieve the current state and conversation history of an interview."""
    return service.get_session(
        db=db,
        user_id=current_user.id,
        session_id=session_id,
    )


@router.post(
    "/{session_id}/answer",
    response_model=InterviewSessionResponse,
)
async def submit_interview_answer(
    session_id: str,
    request: SubmitAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InterviewSessionResponse:
    """Submit an answer to the active question and advance the LangGraph flow."""
    return await service.submit_answer(
        db=db,
        user_id=current_user.id,
        session_id=session_id,
        request=request,
    )


@router.post(
    "/{session_id}/end",
    response_model=InterviewSessionResponse,
)
async def end_interview_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InterviewSessionResponse:
    """Safely end an active interview session."""
    return await service.end_interview(
        db=db,
        user_id=current_user.id,
        session_id=session_id,
    )


@router.delete("/{session_id}")
async def delete_interview_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Permanently delete an owned interview session, its turns, and its report."""
    return await service.delete_interview(
        db=db,
        user_id=current_user.id,
        session_id=session_id,
    )
