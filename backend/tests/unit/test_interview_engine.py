"""Unit tests for LangGraph interview topic selection, RAG, generation, and next-step."""

import json
from types import SimpleNamespace
from unittest.mock import AsyncMock

import anyio

from app.integrations.llm.base import LLMError
from app.modules.interview.next_step import decide_next_action
from app.modules.interview.nodes import InterviewNodes
from app.modules.interview.question_generator import (
    generate_follow_up_question,
    generate_interview_question,
)
from app.modules.interview.topic_selector import select_next_topic


def test_topic_selector_uses_candidate_skills_and_avoids_repeats():
    ctx = {
        "target_role": "Backend Developer",
        "matched_skills": ["Python", "FastAPI"],
        "resume_skills": ["Python", "FastAPI", "PostgreSQL"],
        "missing_skills": ["Redis"],
    }
    t1, _ = select_next_topic(ctx, asked_topics=[], question_index=1)
    t2, _ = select_next_topic(ctx, asked_topics=[t1], question_index=2)
    t3, qt3 = select_next_topic(ctx, asked_topics=[t1, t2], question_index=3)

    assert t1 == "Python"
    assert t2 == "FastAPI"
    assert t3 == "Redis"
    assert qt3 == "gap_probe"


def test_next_step_follow_up_and_completion_limits():
    assert (
        decide_next_action(
            evaluation={"follow_up_needed": True},
            follow_up_count=0,
            max_follow_ups=1,
            question_index=1,
            max_questions=8,
        )
        == "follow_up"
    )
    assert (
        decide_next_action(
            evaluation={"follow_up_needed": True},
            follow_up_count=1,
            max_follow_ups=1,
            question_index=1,
            max_questions=8,
        )
        == "next_question"
    )
    assert (
        decide_next_action(
            evaluation={"follow_up_needed": False},
            follow_up_count=0,
            max_follow_ups=1,
            question_index=8,
            max_questions=8,
        )
        == "complete"
    )


def test_question_generator_validates_structured_json():
    async def scenario():
        provider = AsyncMock()
        provider.generate.return_value = json.dumps(
            {
                "topic": "FastAPI",
                "difficulty": "medium",
                "question_type": "applied",
                "question_text": "How does FastAPI resolve nested Depends() dependencies?",
            }
        )
        q = await generate_interview_question(
            provider=provider,
            question_id="q_001",
            target_role="Backend Developer",
            topic="FastAPI",
            question_type="applied",
            difficulty="medium",
            question_index=1,
            max_questions=8,
            candidate_context={"matched_skills": ["FastAPI"]},
            retrieved_context="",
            previous_questions=[],
        )
        assert q.question_id == "q_001"
        assert q.topic == "FastAPI"
        assert "Depends()" in q.question_text
        assert q.is_follow_up is False

    anyio.run(scenario)


def test_question_generator_falls_back_on_llm_error_and_bad_json():
    async def scenario():
        err_provider = AsyncMock()
        err_provider.generate.side_effect = LLMError("timeout")
        q1 = await generate_interview_question(
            provider=err_provider,
            question_id="q_001",
            target_role="Backend Developer",
            topic="PostgreSQL",
            question_type="conceptual",
            difficulty="easy",
            question_index=1,
            max_questions=5,
            candidate_context={},
            retrieved_context="",
            previous_questions=[],
        )
        assert q1.question_id == "q_001"
        assert "PostgreSQL" in q1.question_text

        bad_provider = AsyncMock()
        bad_provider.generate.return_value = "{not valid json"
        q2 = await generate_follow_up_question(
            provider=bad_provider,
            question_id="q_001_fu_1",
            target_role="Backend Developer",
            topic="PostgreSQL",
            difficulty="easy",
            previous_question=q1.question_text,
            candidate_answer="Use indexes.",
            evaluation={"missing_concepts": ["B-tree vs GIN trade-offs"]},
            retrieved_context="",
        )
        assert q2.question_id == "q_001_fu_1"
        assert q2.is_follow_up is True
        assert "B-tree vs GIN trade-offs" in q2.question_text

    anyio.run(scenario)


def test_rag_retrieval_integration_populates_context_and_sources(monkeypatch):
    async def scenario():
        fake_chunk = SimpleNamespace(
            id=42,
            topic="PostgreSQL",
            subtopic="Indexing",
            source_name="PostgreSQL Docs",
            source_url="https://www.postgresql.org/docs/current/indexes.html",
            content="B-tree indexes handle equality and range queries efficiently.",
        )
        monkeypatch.setattr(
            "app.modules.interview.nodes.retrieve_chunks_async",
            AsyncMock(return_value=[fake_chunk]),
        )
        nodes = InterviewNodes(db=object())
        out = await nodes.retrieve_knowledge(
            {
                "target_role": "Backend Developer",
                "selected_topic": "PostgreSQL",
            }  # type: ignore[arg-type]
        )
        assert "B-tree indexes" in out["retrieved_context"]
        assert len(out["retrieved_sources"]) == 1
        assert out["retrieved_sources"][0]["chunk_id"] == 42

    anyio.run(scenario)
