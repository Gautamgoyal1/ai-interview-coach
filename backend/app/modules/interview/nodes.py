"""LangGraph node implementations for the adaptive AI interview workflow."""

import logging
from typing import Any

from langgraph.types import interrupt
from sqlalchemy.orm import Session

from app.integrations.llm.base import LLMError, LLMProvider
from app.integrations.llm.factory import get_llm_provider
from app.modules.interview.adaptive import (
    compute_adaptive_update,
    difficulty_for_next_topic,
    starting_difficulty_for_level,
)
from app.modules.interview.calibration import (
    DEFAULT_EXPERIENCE_LEVEL,
    normalize_experience_level,
)
from app.modules.interview.deduplication import compute_question_fingerprint
from app.modules.interview.grader import grade_interview_answer
from app.modules.interview.hr_generator import (
    generate_hr_follow_up,
    generate_hr_question,
)
from app.modules.interview.hr_grader import grade_hr_interview_answer
from app.modules.interview.hr_question_bank import select_hr_category
from app.modules.interview.next_step import decide_adaptive_next_step
from app.modules.interview.question_generator import (
    generate_follow_up_question,
    generate_interview_question,
)
from app.modules.interview.state import InterviewState
from app.modules.interview.topic_selector import select_topic_with_focus
from app.modules.knowledge.retriever import retrieve_chunks_async

logger = logging.getLogger(__name__)


def _safe_get_provider(provider: LLMProvider | None) -> LLMProvider | None:
    if provider is not None:
        return provider
    try:
        return get_llm_provider()
    except LLMError as exc:
        logger.warning("LLM provider unavailable: %s", exc)
        return None


def _difficulty_for_index(
    question_index: int,
    max_questions: int,
    experience_level: str = DEFAULT_EXPERIENCE_LEVEL,
) -> str:
    """Backward-compatible helper returning initial difficulty for an experience level."""
    _ = (question_index, max_questions)
    return starting_difficulty_for_level(experience_level)


class InterviewNodes:
    """Container binding DB session and optional LLM provider for graph nodes."""

    def __init__(
        self,
        db: Session | None = None,
        llm_provider: LLMProvider | None = None,
    ) -> None:
        self.db = db
        self.llm_provider = llm_provider

    async def load_candidate_context(
        self,
        state: InterviewState,
    ) -> dict[str, Any]:
        """Normalize candidate context and initialize adaptive state with safe defaults."""
        ctx = dict(state.get("candidate_context") or {})
        ctx.setdefault("target_role", state["target_role"])
        ctx.setdefault("resume_skills", [])
        ctx.setdefault("matched_skills", [])
        ctx.setdefault("missing_skills", [])
        ctx.setdefault("strengths", [])
        ctx.setdefault("improvement_suggestions", [])
        ctx.setdefault("projects", [])
        level = normalize_experience_level(state.get("experience_level"))
        interview_type = str(state.get("interview_type") or "technical").strip().lower()
        progression_mode = str(state.get("progression_mode") or "adaptive").strip().lower()
        starting_diff = state.get("starting_difficulty")
        initial_diff = state.get("current_difficulty") or starting_diff or starting_difficulty_for_level(level)

        return {
            "candidate_context": ctx,
            "experience_level": level,
            "interview_type": interview_type,
            "progression_mode": progression_mode,
            "starting_difficulty": starting_diff or initial_diff,
            "current_difficulty": initial_diff,
            "difficulty_history": list(state.get("difficulty_history") or []),
            "recent_scores": list(state.get("recent_scores") or []),
            "consecutive_strong_answers": int(state.get("consecutive_strong_answers") or 0),
            "consecutive_weak_answers": int(state.get("consecutive_weak_answers") or 0),
            "topic_performance": dict(state.get("topic_performance") or {}),
            "asked_question_fingerprints": list(state.get("asked_question_fingerprints") or []),
            "recent_cross_session_questions": list(state.get("recent_cross_session_questions") or []),
            "last_evaluation": state.get("last_evaluation"),
            "follow_up_reason": state.get("follow_up_reason"),
            "follow_up_type": state.get("follow_up_type"),
            "status": "in_progress",
        }

    async def select_topic(self, state: InterviewState) -> dict[str, Any]:
        """Select the next topic and adapt difficulty."""
        asked_topics = list(state.get("asked_topics") or [])
        is_hr = str(state.get("interview_type") or "").strip().lower() == "hr"

        if is_hr:
            category = select_hr_category(
                question_index=state["question_index"],
                asked_categories=asked_topics,
                max_questions=state.get("max_questions", 8),
            )
            asked_topics.append(category)
            cur_diff = state.get("current_difficulty") or state.get("starting_difficulty") or "medium"
            return {
                "selected_topic": category,
                "question_focus": "behavioral",
                "asked_topics": asked_topics,
                "current_difficulty": cur_diff,
                "current_question": {
                    "question_type": "conceptual",
                },
            }

        last_topic = asked_topics[-1] if asked_topics else ""
        topic, q_type, q_focus = select_topic_with_focus(
            candidate_context=state["candidate_context"],
            asked_topics=asked_topics,
            question_index=state["question_index"],
            max_questions=state.get("max_questions", 8),
        )
        asked_topics.append(topic)

        level = normalize_experience_level(state.get("experience_level"))
        global_diff = state.get("current_difficulty") or starting_difficulty_for_level(level)
        adapted_diff = difficulty_for_next_topic(
            global_difficulty=global_diff,
            next_topic=topic,
            last_topic=last_topic,
            consecutive_weak_answers=int(state.get("consecutive_weak_answers") or 0),
            recent_scores=list(state.get("recent_scores") or []),
            topic_performance=dict(state.get("topic_performance") or {}),
            experience_level=level,
        )

        return {
            "selected_topic": topic,
            "question_focus": q_focus,
            "asked_topics": asked_topics,
            "current_difficulty": adapted_diff,
            "current_question": {
                "question_type": q_type,
            },
        }

    async def retrieve_knowledge(self, state: InterviewState) -> dict[str, Any]:
        """Retrieve relevant knowledge chunks via existing pgvector RAG (skipped for HR)."""
        is_hr = str(state.get("interview_type") or "").strip().lower() == "hr"
        if is_hr or self.db is None:
            return {"retrieved_context": "", "retrieved_sources": []}

        topic = state.get("selected_topic") or state["target_role"]
        query = f"{state['target_role']} {topic}".strip()

        try:
            chunks = await retrieve_chunks_async(
                db=self.db,
                query=query,
                top_k=3,
            )
        except Exception as exc:  # pragma: no cover - fallback for empty/non-pgvector DB
            logger.info(
                "RAG retrieval skipped/fallback for topic '%s': %s",
                topic,
                type(exc).__name__,
            )
            return {"retrieved_context": "", "retrieved_sources": []}

        if not chunks:
            return {"retrieved_context": "", "retrieved_sources": []}

        snippets = []
        sources = []
        for chunk in chunks:
            snippets.append(f"[{chunk.topic}] {chunk.content.strip()}")
            sources.append(
                {
                    "chunk_id": chunk.id,
                    "topic": chunk.topic,
                    "subtopic": chunk.subtopic,
                    "source_name": chunk.source_name,
                    "source_url": chunk.source_url,
                }
            )

        return {
            "retrieved_context": "\n\n".join(snippets),
            "retrieved_sources": sources,
        }

    async def generate_question(self, state: InterviewState) -> dict[str, Any]:
        """Generate an adaptive, deduplicated primary question grounded in profile & RAG."""
        provider = _safe_get_provider(self.llm_provider)
        q_idx = state["question_index"]
        question_id = f"q_{q_idx:03d}"
        topic = state.get("selected_topic") or state["target_role"]
        pending_type = (state.get("current_question") or {}).get(
            "question_type", "conceptual"
        )
        level = normalize_experience_level(state.get("experience_level"))
        difficulty = state.get("current_difficulty") or starting_difficulty_for_level(level)

        session_questions = [
            turn["question_text"]
            for turn in (state.get("conversation_history") or [])
            if turn.get("question_text")
        ]
        cross_session = list(state.get("recent_cross_session_questions") or [])
        all_previous = session_questions + cross_session
        fingerprints = list(state.get("asked_question_fingerprints") or [])

        is_hr = str(state.get("interview_type") or "").strip().lower() == "hr"

        if is_hr:
            question = await generate_hr_question(
                provider=provider,
                question_id=question_id,
                target_role=state["target_role"],
                category=topic,
                difficulty=difficulty,
                question_index=q_idx,
                max_questions=state["max_questions"],
                candidate_context=state["candidate_context"],
                previous_questions=all_previous,
                experience_level=level,
                asked_fingerprints=fingerprints,
            )
        else:
            question = await generate_interview_question(
                provider=provider,
                question_id=question_id,
                target_role=state["target_role"],
                topic=topic,
                question_type=pending_type,
                difficulty=difficulty,
                question_index=q_idx,
                max_questions=state["max_questions"],
                candidate_context=state["candidate_context"],
                retrieved_context=state.get("retrieved_context") or "",
                previous_questions=all_previous,
                experience_level=level,
                question_focus=state.get("question_focus") or "fundamental",
                asked_fingerprints=fingerprints,
                topic_performance=state.get("topic_performance") or {},
            )

        q_dict = question.model_dump()
        fp = compute_question_fingerprint(q_dict["topic"], q_dict["question_text"])
        if fp not in fingerprints:
            fingerprints.append(fp)

        diff_history = list(state.get("difficulty_history") or [])
        diff_history.append(q_dict["difficulty"])

        history = list(state.get("conversation_history") or [])
        history.append(
            {
                "question_id": q_dict["question_id"],
                "question_index": q_idx,
                "is_follow_up": False,
                "topic": q_dict["topic"],
                "difficulty": q_dict["difficulty"],
                "question_type": q_dict["question_type"],
                "question_text": q_dict["question_text"],
                "answer_text": None,
            }
        )

        return {
            "current_question": q_dict,
            "current_answer": None,
            "current_evaluation": None,
            "follow_up_count": 0,
            "follow_up_reason": None,
            "follow_up_type": None,
            "current_difficulty": q_dict["difficulty"],
            "difficulty_history": diff_history,
            "asked_question_fingerprints": fingerprints,
            "conversation_history": history,
        }

    async def wait_for_answer(self, state: InterviewState) -> dict[str, Any]:
        """Pause LangGraph execution via interrupt() until candidate submits answer."""
        answer = interrupt({"question": state.get("current_question")})
        return {"current_answer": str(answer).strip()}

    async def evaluate_answer(self, state: InterviewState) -> dict[str, Any]:
        """Evaluate the submitted answer and update adaptive difficulty & topic state."""
        question = state.get("current_question") or {}
        answer = (state.get("current_answer") or "").strip()
        provider = _safe_get_provider(self.llm_provider)
        level = normalize_experience_level(state.get("experience_level"))
        topic = question.get("topic", state.get("selected_topic", ""))
        cur_diff = question.get("difficulty") or state.get("current_difficulty") or starting_difficulty_for_level(level)
        is_hr = str(state.get("interview_type") or "").strip().lower() == "hr"

        if is_hr:
            evaluation = await grade_hr_interview_answer(
                provider=provider,
                target_role=state["target_role"],
                category=topic,
                difficulty=cur_diff,
                question_text=question.get("question_text", ""),
                answer_text=answer,
                experience_level=level,
            )
        else:
            evaluation = await grade_interview_answer(
                provider=provider,
                target_role=state["target_role"],
                topic=topic,
                difficulty=cur_diff,
                question_text=question.get("question_text", ""),
                answer_text=answer,
                retrieved_context=state.get("retrieved_context") or "",
                experience_level=level,
            )

        eval_dict = evaluation.model_dump()

        history = list(state.get("conversation_history") or [])
        for turn in reversed(history):
            if turn.get("question_id") == question.get("question_id"):
                turn["answer_text"] = answer
                break

        eval_history = list(state.get("evaluation_history") or [])
        eval_history.append(
            {
                "question_id": question.get("question_id"),
                "topic": topic,
                **eval_dict,
            }
        )

        adaptive_update = compute_adaptive_update(
            current_difficulty=state.get("current_difficulty") or cur_diff,
            experience_level=level,
            evaluation=eval_dict,
            recent_scores=list(state.get("recent_scores") or []),
            consecutive_strong_answers=int(state.get("consecutive_strong_answers") or 0),
            consecutive_weak_answers=int(state.get("consecutive_weak_answers") or 0),
            topic_performance=dict(state.get("topic_performance") or {}),
            topic=topic,
            progression_mode=state.get("progression_mode", "adaptive"),
            starting_difficulty=state.get("starting_difficulty"),
        )

        return {
            "current_evaluation": eval_dict,
            "last_evaluation": eval_dict,
            "conversation_history": history,
            "evaluation_history": eval_history,
            "current_difficulty": adaptive_update["next_difficulty"],
            "recent_scores": adaptive_update["recent_scores"],
            "consecutive_strong_answers": adaptive_update["consecutive_strong_answers"],
            "consecutive_weak_answers": adaptive_update["consecutive_weak_answers"],
            "topic_performance": adaptive_update["topic_performance"],
        }

    async def decide_next_step(self, state: InterviewState) -> dict[str, Any]:
        """Compute explicit next_action and follow-up intent from evaluation & limits."""
        question = state.get("current_question") or {}
        action, fu_type, fu_reason = decide_adaptive_next_step(
            evaluation=state.get("current_evaluation"),
            follow_up_count=state.get("follow_up_count", 0),
            max_follow_ups=state.get("max_follow_ups", 1),
            question_index=state.get("question_index", 1),
            max_questions=state.get("max_questions", 8),
            question_type=question.get("question_type", "conceptual"),
            current_difficulty=question.get("difficulty") or state.get("current_difficulty") or "medium",
        )
        return {
            "next_action": action,
            "follow_up_type": fu_type,
            "follow_up_reason": fu_reason,
        }

    async def generate_follow_up(self, state: InterviewState) -> dict[str, Any]:
        """Generate a targeted, intent-aware follow-up question and increment follow_up_count."""
        provider = _safe_get_provider(self.llm_provider)
        prev_q = state.get("current_question") or {}
        q_idx = state["question_index"]
        next_fu = state.get("follow_up_count", 0) + 1
        fu_question_id = f"q_{q_idx:03d}_fu_{next_fu}"
        level = normalize_experience_level(state.get("experience_level"))
        is_hr = str(state.get("interview_type") or "").strip().lower() == "hr"

        if is_hr:
            follow_up = await generate_hr_follow_up(
                provider=provider,
                question_id=fu_question_id,
                target_role=state["target_role"],
                category=prev_q.get("topic", state.get("selected_topic", "")),
                difficulty=prev_q.get("difficulty", "medium"),
                previous_question=prev_q.get("question_text", ""),
                candidate_answer=state.get("current_answer") or "",
                evaluation=state.get("current_evaluation") or {},
                experience_level=level,
                follow_up_type=state.get("follow_up_type"),
            )
        else:
            follow_up = await generate_follow_up_question(
                provider=provider,
                question_id=fu_question_id,
                target_role=state["target_role"],
                topic=prev_q.get("topic", state.get("selected_topic", "")),
                difficulty=prev_q.get("difficulty", "medium"),
                previous_question=prev_q.get("question_text", ""),
                candidate_answer=state.get("current_answer") or "",
                evaluation=state.get("current_evaluation") or {},
                retrieved_context=state.get("retrieved_context") or "",
                experience_level=level,
                follow_up_type=state.get("follow_up_type"),
            )

        q_dict = follow_up.model_dump()
        fingerprints = list(state.get("asked_question_fingerprints") or [])
        fp = compute_question_fingerprint(q_dict["topic"], q_dict["question_text"])
        if fp not in fingerprints:
            fingerprints.append(fp)

        history = list(state.get("conversation_history") or [])
        history.append(
            {
                "question_id": q_dict["question_id"],
                "question_index": q_idx,
                "is_follow_up": True,
                "parent_question_id": prev_q.get("question_id"),
                "topic": q_dict["topic"],
                "difficulty": q_dict["difficulty"],
                "question_type": q_dict["question_type"],
                "question_text": q_dict["question_text"],
                "answer_text": None,
            }
        )

        return {
            "current_question": q_dict,
            "current_answer": None,
            "follow_up_count": next_fu,
            "asked_question_fingerprints": fingerprints,
            "conversation_history": history,
        }

    async def advance_question(self, state: InterviewState) -> dict[str, Any]:
        """Advance primary question_index and reset follow-up counter."""
        return {
            "question_index": state["question_index"] + 1,
            "follow_up_count": 0,
            "follow_up_reason": None,
            "follow_up_type": None,
            "current_answer": None,
        }

    async def complete_interview(self, state: InterviewState) -> dict[str, Any]:
        """Mark the interview session as completed."""
        return {
            "status": "completed",
            "current_question": None,
            "next_action": "complete",
        }
