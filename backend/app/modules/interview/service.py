"""Service layer orchestrating LangGraph interview execution and DB persistence."""

import asyncio
from datetime import datetime, timezone
import uuid
from typing import Any

from fastapi import HTTPException, status
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from sqlalchemy.orm import Session

from app.db.models.interview_session import InterviewSession
from app.integrations.llm.base import LLMProvider
from app.modules.interview.adaptive import starting_difficulty_for_level
from app.modules.interview.calibration import normalize_experience_level
from app.modules.interview.deduplication import compute_question_fingerprint
from app.modules.interview.graph import build_interview_graph, clear_session_checkpoints
from app.modules.interview.repository import (
    create_interview_session,
    create_question_turn,
    get_owned_resume_analysis,
    get_owned_session,
    get_turn_by_question_id,
    list_recent_user_questions,
    list_session_turns,
    record_turn_answer,
)
from app.modules.interview.schemas import (
    InterviewSessionResponse,
    PublicConversationTurn,
    PublicInterviewQuestion,
    StartInterviewRequest,
    SubmitAnswerRequest,
)
from app.modules.interview.state import InterviewState


def _extract_candidate_context(
    job_role: str,
    result_json: dict[str, Any],
) -> dict[str, Any]:
    return {
        "target_role": job_role,
        "resume_skills": list(result_json.get("resume_skills") or []),
        "matched_skills": list(result_json.get("matched_skills") or []),
        "missing_skills": list(result_json.get("missing_skills") or []),
        "strengths": list(result_json.get("strengths") or []),
        "improvement_suggestions": list(
            result_json.get("improvement_suggestions") or []
        ),
    }


def _to_public_question(
    question: dict[str, Any] | None,
) -> PublicInterviewQuestion | None:
    if not question or not question.get("question_id"):
        return None
    return PublicInterviewQuestion(
        question_id=str(question["question_id"]),
        topic=str(question.get("topic", "")),
        difficulty=str(question.get("difficulty", "medium")),
        question_text=str(question.get("question_text", "")),
        question_type=str(question.get("question_type", "conceptual")),
        is_follow_up=bool(question.get("is_follow_up", False)),
    )


def _to_session_response(
    db: Session,
    session: InterviewSession,
) -> InterviewSessionResponse:
    turns = list_session_turns(db, session.id)
    active_q = None
    if session.status == "in_progress":
        active_q = _to_public_question(
            (session.graph_state or {}).get("current_question")
        )

    history = [
        PublicConversationTurn(
            question_id=t.question_id,
            question_index=t.question_index,
            is_follow_up=t.is_follow_up,
            topic=t.topic,
            difficulty=t.difficulty,
            question_type=t.question_type,
            question_text=t.question_text,
            answer_text=t.answer_text,
            created_at=t.created_at,
            answered_at=t.answered_at,
        )
        for t in turns
    ]

    cfg = session.configuration or {}
    interview_type = (
        getattr(session, "interview_type", None)
        or cfg.get("interview_type", "technical")
    )
    starting_difficulty = cfg.get("starting_difficulty", "medium")
    progression_mode = cfg.get("progression_mode", "adaptive")

    return InterviewSessionResponse(
        session_id=session.id,
        analysis_id=session.resume_analysis_id,
        target_role=session.target_role,
        interview_type=interview_type,
        experience_level=normalize_experience_level(cfg.get("experience_level")),
        starting_difficulty=starting_difficulty,
        progression_mode=progression_mode,
        status=session.status,  # type: ignore[arg-type]
        question_index=session.question_index,
        max_questions=session.max_questions,
        follow_up_count=session.follow_up_count,
        max_follow_ups=session.max_follow_ups,
        current_question=active_q,
        conversation_history=history,
        started_at=session.started_at,
        completed_at=session.completed_at,
    )


def _clean_state_for_storage(state: dict[str, Any]) -> dict[str, Any]:
    """Return a JSON-serializable copy of InterviewState."""
    return {
        key: value
        for key, value in state.items()
        if not key.startswith("__")
    }


class InterviewService:
    """Coordinates LangGraph workflow execution with database persistence."""

    def __init__(
        self,
        llm_provider: LLMProvider | None = None,
        checkpointer: MemorySaver | None = None,
    ) -> None:
        self.llm_provider = llm_provider
        self.checkpointer = checkpointer
        self._session_locks: dict[str, asyncio.Lock] = {}

    def _get_session_lock(self, session_id: str) -> asyncio.Lock:
        lock = self._session_locks.get(session_id)
        if lock is None:
            if len(self._session_locks) > 1000:
                stale = [k for k, v in self._session_locks.items() if not v.locked()]
                for k in stale[:500]:
                    self._session_locks.pop(k, None)
            lock = asyncio.Lock()
            self._session_locks[session_id] = lock
        return lock

    async def start_interview(
        self,
        db: Session,
        user_id: int,
        request: StartInterviewRequest,
    ) -> InterviewSessionResponse:
        record = get_owned_resume_analysis(db, request.analysis_id, user_id)
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume analysis not found.",
            )

        analysis, _resume = record
        session_id = str(uuid.uuid4())
        level = normalize_experience_level(request.experience_level)
        interview_type = str(getattr(request, "interview_type", "technical") or "technical").strip().lower()
        progression_mode = str(getattr(request, "progression_mode", "adaptive") or "adaptive").strip().lower()
        requested_diff = getattr(request, "starting_difficulty", None)
        initial_difficulty = requested_diff or starting_difficulty_for_level(level)
        candidate_context = _extract_candidate_context(
            analysis.job_role,
            analysis.result_json or {},
        )
        recent_rows = list_recent_user_questions(
            db=db,
            user_id=user_id,
            target_role=analysis.job_role,
            limit=40,
        )
        recent_questions = [row["question_text"] for row in recent_rows]
        recent_fingerprints = [
            compute_question_fingerprint(row["topic"], row["question_text"])
            for row in recent_rows
        ]

        initial_state: InterviewState = {
            "session_id": session_id,
            "user_id": user_id,
            "analysis_id": analysis.id,
            "target_role": analysis.job_role,
            "interview_type": interview_type,
            "experience_level": level,
            "starting_difficulty": initial_difficulty,
            "progression_mode": progression_mode,
            "candidate_context": candidate_context,
            "selected_topic": "",
            "question_focus": "behavioral" if interview_type == "hr" else "fundamental",
            "retrieved_context": "",
            "retrieved_sources": [],
            "current_question": None,
            "current_answer": None,
            "current_evaluation": None,
            "next_action": "",
            "question_index": 1,
            "max_questions": request.max_questions,
            "follow_up_count": 0,
            "max_follow_ups": request.max_follow_ups,
            "asked_topics": [],
            "conversation_history": [],
            "evaluation_history": [],
            "current_difficulty": initial_difficulty,
            "difficulty_history": [],
            "recent_scores": [],
            "consecutive_strong_answers": 0,
            "consecutive_weak_answers": 0,
            "topic_performance": {},
            "asked_question_fingerprints": recent_fingerprints,
            "recent_cross_session_questions": recent_questions,
            "last_evaluation": None,
            "follow_up_reason": None,
            "follow_up_type": None,
            "status": "in_progress",
        }

        graph = build_interview_graph(
            db=db,
            llm_provider=self.llm_provider,
            checkpointer=self.checkpointer,
        )
        config = {"configurable": {"thread_id": session_id}}
        result_state = await graph.ainvoke(initial_state, config=config)

        stored_state = _clean_state_for_storage(dict(result_state))
        session = create_interview_session(
            db=db,
            session_id=session_id,
            user_id=user_id,
            analysis_id=analysis.id,
            target_role=analysis.job_role,
            interview_type=interview_type,
            max_questions=request.max_questions,
            max_follow_ups=request.max_follow_ups,
            configuration={
                "interview_type": interview_type,
                "experience_level": level,
                "starting_difficulty": initial_difficulty,
                "progression_mode": progression_mode,
                "max_questions": request.max_questions,
                "max_follow_ups": request.max_follow_ups,
            },
            graph_state=stored_state,
        )

        first_question = stored_state.get("current_question")
        if first_question:
            create_question_turn(
                db=db,
                session_id=session_id,
                question=first_question,
                question_index=stored_state["question_index"],
                rag_sources=list(stored_state.get("retrieved_sources") or []),
            )

        db.commit()
        db.refresh(session)
        return _to_session_response(db, session)

    def get_session(
        self,
        db: Session,
        user_id: int,
        session_id: str,
    ) -> InterviewSessionResponse:
        session = get_owned_session(db, session_id, user_id)
        if session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found.",
            )
        return _to_session_response(db, session)

    async def submit_answer(
        self,
        db: Session,
        user_id: int,
        session_id: str,
        request: SubmitAnswerRequest,
    ) -> InterviewSessionResponse:
        cleaned_answer = request.answer.strip()
        if not cleaned_answer:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Answer cannot be empty.",
            )

        async with self._get_session_lock(session_id):
            db.expire_all()
            return await self._submit_answer_locked(
                db=db,
                user_id=user_id,
                session_id=session_id,
                request=request,
                cleaned_answer=cleaned_answer,
            )

    async def _submit_answer_locked(
        self,
        db: Session,
        user_id: int,
        session_id: str,
        request: SubmitAnswerRequest,
        cleaned_answer: str,
    ) -> InterviewSessionResponse:
        session = get_owned_session(db, session_id, user_id)
        if session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found.",
            )

        if session.status != "in_progress":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This interview session has already ended.",
            )

        stored_state = dict(session.graph_state or {})
        active_question = stored_state.get("current_question") or {}
        if active_question.get("question_id") != request.question_id:
            existing_turn = get_turn_by_question_id(
                db, session_id, request.question_id
            )
            if existing_turn is not None and existing_turn.answer_text is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="This question has already been answered.",
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Submitted question_id is not currently active.",
            )

        turn = get_turn_by_question_id(db, session_id, request.question_id)
        if turn is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Active question record was not found.",
            )
        if turn.answer_text is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This question has already been answered.",
            )

        graph = build_interview_graph(
            db=db,
            llm_provider=self.llm_provider,
            checkpointer=self.checkpointer,
        )
        config = {"configurable": {"thread_id": session_id}}

        # Rehydrate LangGraph checkpoint if process restarted.
        snapshot = await graph.aget_state(config)
        if not snapshot.next:
            as_node = (
                "generate_follow_up"
                if active_question.get("is_follow_up")
                else "generate_question"
            )
            await graph.aupdate_state(config, stored_state, as_node=as_node)

        result_state = await graph.ainvoke(
            Command(resume=cleaned_answer),
            config=config,
        )

        updated_state = _clean_state_for_storage(dict(result_state))
        record_turn_answer(
            db=db,
            turn=turn,
            answer_text=cleaned_answer,
            evaluation=updated_state.get("current_evaluation"),
        )

        next_question = updated_state.get("current_question")
        if updated_state.get("status") == "in_progress" and next_question:
            parent_id = (
                active_question.get("question_id")
                if next_question.get("is_follow_up")
                else None
            )
            create_question_turn(
                db=db,
                session_id=session_id,
                question=next_question,
                question_index=updated_state["question_index"],
                rag_sources=list(updated_state.get("retrieved_sources") or []),
                parent_question_id=parent_id,
            )

        session.status = str(updated_state.get("status", "in_progress"))
        session.question_index = int(updated_state.get("question_index", session.question_index))
        session.follow_up_count = int(updated_state.get("follow_up_count", 0))
        session.graph_state = updated_state
        if session.status == "completed" and session.completed_at is None:
            session.completed_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(session)
        return _to_session_response(db, session)

    async def end_interview(
        self,
        db: Session,
        user_id: int,
        session_id: str,
    ) -> InterviewSessionResponse:
        async with self._get_session_lock(session_id):
            db.expire_all()
            session = get_owned_session(db, session_id, user_id)
            if session is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Interview session not found.",
                )

            if session.status != "completed":
                session.status = "completed"
                session.completed_at = datetime.now(timezone.utc)
                updated_state = dict(session.graph_state or {})
                updated_state["status"] = "completed"
                updated_state["current_question"] = None
                session.graph_state = updated_state
                db.commit()
                db.refresh(session)

            return _to_session_response(db, session)

    async def delete_interview(
        self,
        db: Session,
        user_id: int,
        session_id: str,
    ) -> dict[str, Any]:
        async with self._get_session_lock(session_id):
            db.expire_all()
            session = get_owned_session(db, session_id, user_id)
            if session is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Interview session not found.",
                )

            db.delete(session)
            db.commit()
            clear_session_checkpoints([session_id], checkpointer=self.checkpointer)
            return {"deleted": True, "session_id": session_id}
