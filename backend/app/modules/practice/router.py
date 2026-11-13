"""FastAPI router for personalized practice sessions and AI answer coaching."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.models.user import User
from app.db.session import get_db
from app.modules.practice.schemas import (
    CreatePracticeSessionRequest,
    GeneratePracticeQuestionRequest,
    PracticeAttemptResponse,
    PracticeQuestionResponse,
    PracticeRecommendationItem,
    PracticeSessionDetailResponse,
    PracticeSessionSummaryResponse,
    RevealHintResponse,
    RevealReferenceResponse,
    SubmitPracticeAttemptRequest,
)
from app.modules.practice.service import PracticeService

router = APIRouter(prefix="/practice", tags=["Practice & Answer Coaching"])
service = PracticeService()


@router.post(
    "/sessions",
    response_model=PracticeSessionDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_practice_session(
    request: CreatePracticeSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PracticeSessionDetailResponse:
    """Create a new targeted practice session and generate its first question."""
    return await service.create_session(
        db,
        user_id=current_user.id,
        request=request,
    )


@router.get(
    "/sessions",
    response_model=list[PracticeSessionSummaryResponse],
)
def list_practice_sessions(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[PracticeSessionSummaryResponse]:
    """List the user's active practice sessions."""
    return service.list_sessions(
        db,
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/sessions/{session_id}",
    response_model=PracticeSessionDetailResponse,
)
def get_practice_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PracticeSessionDetailResponse:
    """Retrieve full details of a practice session including questions and attempts."""
    return service.get_session(
        db,
        session_id=session_id,
        user_id=current_user.id,
    )


@router.delete(
    "/sessions/{session_id}",
    status_code=status.HTTP_200_OK,
)
def delete_practice_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Safely soft-delete a practice session belonging to the user."""
    return service.delete_session(
        db,
        session_id=session_id,
        user_id=current_user.id,
    )


@router.post(
    "/sessions/{session_id}/questions",
    response_model=PracticeQuestionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_next_question(
    session_id: str,
    request: GeneratePracticeQuestionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PracticeQuestionResponse:
    """Generate another practice question (e.g. similar question or variation) in this session."""
    return await service.generate_next_question(
        db,
        session_id=session_id,
        user_id=current_user.id,
        request=request,
    )


@router.post(
    "/questions/{question_id}/hints/{level}/reveal",
    response_model=RevealHintResponse,
)
def reveal_hint(
    question_id: str,
    level: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RevealHintResponse:
    """Reveal a progressive hint (level 1 or 2) and record the assistance event."""
    return service.reveal_hint(
        db,
        question_id=question_id,
        user_id=current_user.id,
        level=level,
    )


@router.post(
    "/questions/{question_id}/reference/reveal",
    response_model=RevealReferenceResponse,
)
def reveal_reference_answer(
    question_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RevealReferenceResponse:
    """Reveal the complete reference answer and record the reference assistance event."""
    return service.reveal_reference(
        db,
        question_id=question_id,
        user_id=current_user.id,
    )


@router.post(
    "/questions/{question_id}/attempts",
    response_model=PracticeAttemptResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_practice_attempt(
    question_id: str,
    request: SubmitPracticeAttemptRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PracticeAttemptResponse:
    """Submit candidate answer for coaching, evaluate against reference, and persist attempt."""
    return await service.submit_attempt(
        db,
        question_id=question_id,
        user_id=current_user.id,
        request=request,
    )


@router.get(
    "/questions/{question_id}/attempts",
    response_model=list[PracticeAttemptResponse],
)
def list_question_attempts(
    question_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[PracticeAttemptResponse]:
    """Retrieve all submitted attempts and coaching feedback for this question."""
    return service.list_attempts(
        db,
        question_id=question_id,
        user_id=current_user.id,
    )


@router.get(
    "/recommendations",
    response_model=list[PracticeRecommendationItem],
)
def get_practice_recommendations(
    limit: int = Query(default=5, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[PracticeRecommendationItem]:
    """Retrieve prioritized practice recommendations extracted from user's completed interview reports."""
    return service.get_recommendations(
        db,
        user_id=current_user.id,
        limit=limit,
    )
