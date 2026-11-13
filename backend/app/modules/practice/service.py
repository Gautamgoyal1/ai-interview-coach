"""PracticeService orchestrating practice sessions, question generation, assistance tracking, and AI coaching."""

from datetime import datetime, timezone
import logging
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.integrations.llm.base import LLMProvider
from app.integrations.llm.factory import get_llm_provider
from app.modules.practice.coach import coach_practice_answer
from app.modules.practice.generator import generate_practice_question
from app.modules.practice.repository import PracticeRepository
from app.modules.practice.schemas import (
    CreatePracticeSessionRequest,
    GeneratePracticeQuestionRequest,
    PracticeAttemptResponse,
    PracticeFeedback,
    PracticeQuestionResponse,
    PracticeRecommendationItem,
    PracticeSessionDetailResponse,
    PracticeSessionSummaryResponse,
    RevealHintResponse,
    RevealReferenceResponse,
    SubmitPracticeAttemptRequest,
)

logger = logging.getLogger(__name__)


class PracticeService:
    def __init__(
        self,
        repository: PracticeRepository | None = None,
        llm_provider: LLMProvider | None = None,
    ):
        self.repository = repository or PracticeRepository()
        self._llm_provider = llm_provider

    def _get_provider(self) -> LLMProvider | None:
        if self._llm_provider is not None:
            return self._llm_provider
        try:
            return get_llm_provider()
        except Exception as exc:
            logger.warning("Could not initialize default LLM provider: %s", exc)
            return None

    def _determine_assistance_level(
        self,
        hints_revealed: list[int],
        reference_revealed: bool,
    ) -> str:
        if reference_revealed:
            return "reference_assisted"
        if hints_revealed:
            return "hint_assisted"
        return "independent"

    def _to_question_response(self, q: Any) -> PracticeQuestionResponse:
        hints_dict = q.hints or {}
        hints_rev = list(q.hints_revealed or [])

        # Only expose revealed hints
        revealed_hints = {
            str(lvl): hints_dict.get(f"hint_{lvl}", "")
            for lvl in hints_rev
            if f"hint_{lvl}" in hints_dict
        }

        # Format attempts
        attempts_list = []
        for att in getattr(q, "attempts", []):
            fb_dict = att.feedback or {}
            attempts_list.append(
                PracticeAttemptResponse(
                    id=att.id,
                    question_id=att.question_id,
                    attempt_number=att.attempt_number,
                    answer_text=att.answer_text,
                    assistance_level=att.assistance_level,
                    hints_used=list(att.hints_used or []),
                    reference_revealed=att.reference_revealed,
                    feedback=PracticeFeedback(**fb_dict),
                    created_at=att.created_at,
                )
            )

        return PracticeQuestionResponse(
            id=q.id,
            session_id=q.session_id,
            question_text=q.question_text,
            topic=q.topic,
            difficulty=q.difficulty,
            hints_revealed=hints_rev,
            revealed_hints=revealed_hints,
            reference_revealed=q.reference_revealed,
            reference_answer=q.reference_answer if q.reference_revealed else None,
            reference_explanation=q.reference_explanation if q.reference_revealed else None,
            attempts=attempts_list,
            created_at=q.created_at,
        )

    def _to_session_detail(self, session: Any) -> PracticeSessionDetailResponse:
        questions = [self._to_question_response(q) for q in (session.questions or [])]
        return PracticeSessionDetailResponse(
            id=session.id,
            user_id=session.user_id,
            interview_type=session.interview_type,
            target_role=session.target_role,
            topic=session.topic,
            source_report_id=session.source_report_id,
            experience_level=session.experience_level,
            weakness_context=session.weakness_context,
            status=session.status,
            questions=questions,
            created_at=session.created_at,
            updated_at=session.updated_at,
        )

    async def create_session(
        self,
        db: Session,
        *,
        user_id: int,
        request: CreatePracticeSessionRequest,
    ) -> PracticeSessionDetailResponse:
        provider = self._get_provider()

        # 1. Create session entity
        session = self.repository.create_session(
            db,
            user_id=user_id,
            interview_type=request.interview_type,
            target_role=request.target_role,
            topic=request.topic,
            experience_level=request.experience_level,
            source_report_id=request.source_report_id,
            weakness_context=request.weakness_context,
        )

        # 2. Generate initial practice question with hints & reference answer
        q_data = await generate_practice_question(
            provider=provider,
            interview_type=session.interview_type,
            target_role=session.target_role,
            topic=session.topic,
            experience_level=session.experience_level,
            difficulty=request.difficulty,
            weakness_context=session.weakness_context,
            previous_questions=[],
            db=db,
        )

        self.repository.create_question(
            db,
            session_id=session.id,
            question_text=q_data.question_text,
            topic=q_data.topic,
            difficulty=q_data.difficulty,
            hints=q_data.hints,
            reference_answer=q_data.reference_answer,
            reference_explanation=q_data.reference_explanation,
        )

        # 3. Reload complete session
        full_session = self.repository.get_session(db, session.id, user_id)
        if not full_session:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve created practice session.",
            )

        return self._to_session_detail(full_session)

    def get_session(
        self,
        db: Session,
        *,
        session_id: str,
        user_id: int,
    ) -> PracticeSessionDetailResponse:
        session = self.repository.get_session(db, session_id, user_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Practice session not found or you do not have permission to view it.",
            )
        return self._to_session_detail(session)

    def list_sessions(
        self,
        db: Session,
        *,
        user_id: int,
        limit: int = 20,
        offset: int = 0,
    ) -> list[PracticeSessionSummaryResponse]:
        sessions = self.repository.list_sessions(db, user_id, limit, offset)
        summaries = []
        for s in sessions:
            questions = s.questions or []
            attempts_total = sum(len(q.attempts or []) for q in questions)
            latest_attempt_ts = None
            for q in questions:
                for a in q.attempts or []:
                    if latest_attempt_ts is None or a.created_at > latest_attempt_ts:
                        latest_attempt_ts = a.created_at

            summaries.append(
                PracticeSessionSummaryResponse(
                    id=s.id,
                    interview_type=s.interview_type,
                    target_role=s.target_role,
                    topic=s.topic,
                    source_report_id=s.source_report_id,
                    status=s.status,
                    question_count=len(questions),
                    attempt_count=attempts_total,
                    latest_attempt_at=latest_attempt_ts,
                    created_at=s.created_at,
                )
            )
        return summaries

    async def generate_next_question(
        self,
        db: Session,
        *,
        session_id: str,
        user_id: int,
        request: GeneratePracticeQuestionRequest,
    ) -> PracticeQuestionResponse:
        session = self.repository.get_session(db, session_id, user_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Practice session not found.",
            )

        provider = self._get_provider()
        prev_questions = [q.question_text for q in (session.questions or [])]
        diff = request.difficulty or (session.questions[-1].difficulty if session.questions else "medium")
        weakness = request.focus_concept or session.weakness_context

        q_data = await generate_practice_question(
            provider=provider,
            interview_type=session.interview_type,
            target_role=session.target_role,
            topic=session.topic,
            experience_level=session.experience_level,
            difficulty=diff,
            weakness_context=weakness,
            previous_questions=prev_questions,
            db=db,
        )

        question = self.repository.create_question(
            db,
            session_id=session.id,
            question_text=q_data.question_text,
            topic=q_data.topic,
            difficulty=q_data.difficulty,
            hints=q_data.hints,
            reference_answer=q_data.reference_answer,
            reference_explanation=q_data.reference_explanation,
        )

        return self._to_question_response(question)

    def reveal_hint(
        self,
        db: Session,
        *,
        question_id: str,
        user_id: int,
        level: int,
    ) -> RevealHintResponse:
        if level not in (1, 2):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hint level must be 1 or 2.",
            )

        question = self.repository.get_question(db, question_id, user_id)
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Practice question not found or unauthorized.",
            )

        hints_dict = question.hints or {}
        hint_key = f"hint_{level}"
        hint_text = hints_dict.get(
            hint_key,
            "Focus on the primary definition and trade-offs of the concept." if level == 1 else "Organize your response with definition, mechanism, and an example.",
        )

        updated_hints = self.repository.reveal_hint(db, question, level)
        assistance_level = self._determine_assistance_level(
            hints_revealed=updated_hints,
            reference_revealed=question.reference_revealed,
        )

        return RevealHintResponse(
            question_id=question.id,
            level=level,
            hint_text=hint_text,
            hints_revealed=updated_hints,
            assistance_level=assistance_level,  # type: ignore[arg-type]
        )

    def reveal_reference(
        self,
        db: Session,
        *,
        question_id: str,
        user_id: int,
    ) -> RevealReferenceResponse:
        question = self.repository.get_question(db, question_id, user_id)
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Practice question not found or unauthorized.",
            )

        self.repository.reveal_reference(db, question)
        assistance_level = self._determine_assistance_level(
            hints_revealed=list(question.hints_revealed or []),
            reference_revealed=True,
        )

        return RevealReferenceResponse(
            question_id=question.id,
            reference_answer=question.reference_answer,
            reference_explanation=question.reference_explanation,
            reference_revealed=True,
            assistance_level=assistance_level,  # type: ignore[arg-type]
        )

    async def submit_attempt(
        self,
        db: Session,
        *,
        question_id: str,
        user_id: int,
        request: SubmitPracticeAttemptRequest,
    ) -> PracticeAttemptResponse:
        cleaned_answer = request.answer_text.strip()
        if not cleaned_answer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Answer cannot be empty.",
            )

        question = self.repository.get_question(db, question_id, user_id)
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Practice question not found or unauthorized.",
            )

        session = question.session
        provider = self._get_provider()

        # Find previous attempt if retry
        existing_attempts = self.repository.list_attempts(db, question_id, user_id)
        prev_answer = existing_attempts[-1].answer_text if existing_attempts else None

        # Determine assistance level
        hints_used = list(question.hints_revealed or [])
        ref_revealed = bool(question.reference_revealed)
        assistance_level = self._determine_assistance_level(
            hints_revealed=hints_used,
            reference_revealed=ref_revealed,
        )

        # AI Answer Coach evaluation
        feedback = await coach_practice_answer(
            provider=provider,
            question_text=question.question_text,
            reference_answer=question.reference_answer,
            candidate_answer=cleaned_answer,
            interview_type=session.interview_type,
            topic=question.topic,
            difficulty=question.difficulty,
            experience_level=session.experience_level,
            previous_attempt_answer=prev_answer,
        )

        # Save attempt
        attempt = self.repository.create_attempt(
            db,
            question_id=question.id,
            user_id=user_id,
            answer_text=cleaned_answer,
            assistance_level=assistance_level,
            hints_used=hints_used,
            reference_revealed=ref_revealed,
            feedback=feedback.model_dump(),
        )

        # Touch session updated_at
        session.updated_at = datetime.now(timezone.utc)
        db.commit()

        return PracticeAttemptResponse(
            id=attempt.id,
            question_id=attempt.question_id,
            attempt_number=attempt.attempt_number,
            answer_text=attempt.answer_text,
            assistance_level=attempt.assistance_level,  # type: ignore[arg-type]
            hints_used=list(attempt.hints_used or []),
            reference_revealed=attempt.reference_revealed,
            feedback=feedback,
            created_at=attempt.created_at,
        )

    def list_attempts(
        self,
        db: Session,
        *,
        question_id: str,
        user_id: int,
    ) -> list[PracticeAttemptResponse]:
        question = self.repository.get_question(db, question_id, user_id)
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Practice question not found or unauthorized.",
            )

        attempts = self.repository.list_attempts(db, question_id, user_id)
        return [
            PracticeAttemptResponse(
                id=a.id,
                question_id=a.question_id,
                attempt_number=a.attempt_number,
                answer_text=a.answer_text,
                assistance_level=a.assistance_level,  # type: ignore[arg-type]
                hints_used=list(a.hints_used or []),
                reference_revealed=a.reference_revealed,
                feedback=PracticeFeedback(**(a.feedback or {})),
                created_at=a.created_at,
            )
            for a in attempts
        ]

    def delete_session(
        self,
        db: Session,
        *,
        session_id: str,
        user_id: int,
    ) -> dict[str, str]:
        deleted = self.repository.soft_delete_session(db, session_id, user_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Practice session not found or unauthorized.",
            )
        return {"status": "deleted", "session_id": session_id}

    def get_recommendations(
        self,
        db: Session,
        *,
        user_id: int,
        limit: int = 5,
    ) -> list[PracticeRecommendationItem]:
        items = self.repository.get_recommendations_from_reports(db, user_id, limit)
        return [PracticeRecommendationItem(**it) for it in items]
