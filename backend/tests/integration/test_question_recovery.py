"""Recovery never regrades, changes mock tier, or saves an invalid question."""

import json
import os
import re
import uuid

import anyio
import pytest
from fastapi import HTTPException
from langgraph.checkpoint.memory import MemorySaver
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.base import Base
from app.db.models.interview_session import InterviewSession
from app.db.models.resume import Resume, ResumeAnalysis
from app.db.models.turn import InterviewTurn
from app.db.models.user import User
from app.modules.interview import nodes
from app.modules.interview.generation_errors import QuestionGenerationUnavailable
from app.modules.interview.router import service as api_service
from app.modules.interview.schemas import (
    InterviewQuestion,
    StartInterviewRequest,
    SubmitAnswerRequest,
)
from app.modules.interview.service import InterviewService
from tests.integration.test_interview_flow import (
    interview_env,
    _create_user_and_analysis,
    ScriptedInterviewLLM,
)


def controlled_generation(monkeypatch):
    control = {"unavailable": False, "calls": 0}

    async def generate(**kwargs):
        control["calls"] += 1
        if control["unavailable"]:
            raise QuestionGenerationUnavailable(kwargs["topic"])
        return InterviewQuestion(
            question_id=kwargs["question_id"],
            topic=kwargs["topic"],
            difficulty=kwargs["difficulty"],
            question_type="applied",
            reasoning_family=f"test_private_family_{kwargs['question_index']}",
            question_text=f"A cache has concurrent writes and cancellation. How would you preserve publication order at step {kwargs['question_index']}?",
        )

    monkeypatch.setattr(nodes, "generate_interview_question", generate)
    return control


def test_api_saved_grade_refresh_restart_and_idempotent_retry(
    interview_env, monkeypatch
):
    client, sessions, llm = interview_env
    llm.follow_up_first = False
    control = controlled_generation(monkeypatch)
    headers, analysis = _create_user_and_analysis(
        client, sessions, "generation-recovery@example.com"
    )
    other, _ = _create_user_and_analysis(
        client, sessions, "generation-other@example.com"
    )
    start = client.post(
        "/interview/start",
        headers=headers,
        json={
            "analysis_id": analysis,
            "starting_difficulty": "hard",
            "progression_mode": "mock",
            "max_questions": 2,
            "max_follow_ups": 0,
        },
    )
    assert start.status_code == 201
    session = start.json()
    sid = session["session_id"]
    qid = session["current_question"]["question_id"]
    control["unavailable"] = True
    answer = {
        "question_id": qid,
        "answer": "Use a generation token and atomic publication with cancellation-safe cleanup.",
    }
    failed = client.post(f"/interview/{sid}/answer", headers=headers, json=answer)
    assert failed.status_code == 503 and "answer was saved" in failed.json()["detail"]
    assert llm.eval_counter == 1
    loaded = client.get(f"/interview/{sid}", headers=headers).json()
    assert loaded["generation_unavailable"] and loaded["current_question"] is None
    assert (
        loaded["status"] == "in_progress"
        and loaded["conversation_history"][0]["answer_text"] == answer["answer"]
    )
    with sessions() as db:
        turn = db.scalar(select(InterviewTurn).where(InterviewTurn.session_id == sid))
        original = json.loads(json.dumps(turn.evaluation))
        assert original["grading_status"] == "completed"
        assert (
            len(
                list(
                    db.scalars(
                        select(InterviewTurn).where(InterviewTurn.session_id == sid)
                    )
                )
            )
            == 1
        )
    assert (
        client.post(
            f"/interview/{sid}/answer", headers=headers, json=answer
        ).status_code
        == 409
    )
    assert client.post(f"/interview/{sid}/retry-question").status_code == 401
    assert (
        client.post(f"/interview/{sid}/retry-question", headers=other).status_code
        == 404
    )
    assert (
        client.post(f"/interview/{sid}/retry-question", headers=headers).status_code
        == 503
    )
    assert llm.eval_counter == 1
    monkeypatch.setattr(api_service, "checkpointer", MemorySaver())
    control["unavailable"] = False
    recovered = client.post(f"/interview/{sid}/retry-question", headers=headers)
    assert recovered.status_code == 200
    current = recovered.json()
    assert not current["generation_unavailable"]
    assert (
        current["current_question"]["difficulty"] == "hard"
        and current["question_index"] == 2
    )
    calls = control["calls"]
    again = client.post(f"/interview/{sid}/retry-question", headers=headers)
    assert (
        again.json()["current_question"] == current["current_question"]
        and control["calls"] == calls
    )
    assert llm.eval_counter == 1
    with sessions() as db:
        turns = list(
            db.scalars(
                select(InterviewTurn)
                .where(InterviewTurn.session_id == sid)
                .order_by(InterviewTurn.id)
            )
        )
        assert (
            len(turns) == 2
            and turns[0].evaluation == original
            and turns[1].evaluation is None
        )
    done = client.post(
        f"/interview/{sid}/answer",
        headers=headers,
        json={
            "question_id": current["current_question"]["question_id"],
            "answer": "A durable compare-and-swap prevents stale publication.",
        },
    )
    assert (
        done.status_code == 200
        and done.json()["status"] == "completed"
        and llm.eval_counter == 2
    )


def test_start_unavailable_creates_no_session(interview_env, monkeypatch):
    client, sessions, _ = interview_env
    control = controlled_generation(monkeypatch)
    control["unavailable"] = True
    headers, analysis = _create_user_and_analysis(
        client, sessions, "no-generated-session@example.com"
    )
    result = client.post(
        "/interview/start",
        headers=headers,
        json={"analysis_id": analysis, "starting_difficulty": "hard"},
    )
    assert (
        result.status_code == 503
        and "no interview was started" in result.json()["detail"]
    )
    with sessions() as db:
        assert list(db.scalars(select(InterviewSession))) == []


@pytest.mark.skipif(
    os.getenv("PREPMATE_KNOWLEDGE_POSTGRES") != "1", reason="isolated PostgreSQL schema"
)
def test_postgresql_grade_and_pending_generation_survive_restart(monkeypatch):
    name = "test_phase71_" + uuid.uuid4().hex
    base = create_engine(settings.database_url)
    with base.begin() as c:
        c.execute(text(f'CREATE SCHEMA "{name}"'))
    engine = base.execution_options(schema_translate_map={None: name})
    Base.metadata.create_all(engine)
    control = controlled_generation(monkeypatch)
    llm = ScriptedInterviewLLM(follow_up_first=False)

    async def scenario():
        with Session(engine, expire_on_commit=False) as db:
            user = User(
                email="isolated-recovery@example.com",
                password_hash="not-a-login-password",
            )
            db.add(user)
            db.flush()
            resume = Resume(user_id=user.id, filename="synthetic.pdf")
            db.add(resume)
            db.flush()
            analysis = ResumeAnalysis(
                resume_id=resume.id,
                job_role="Software Engineer",
                result_json={"resume_skills": ["SQL"], "matched_skills": ["SQL"]},
            )
            db.add(analysis)
            db.commit()
            uid, aid = user.id, analysis.id
            service = InterviewService(llm_provider=llm, checkpointer=MemorySaver())
            start = await service.start_interview(
                db,
                uid,
                StartInterviewRequest(
                    analysis_id=aid,
                    starting_difficulty="hard",
                    progression_mode="mock",
                    max_questions=2,
                    max_follow_ups=0,
                ),
            )
            sid = start.session_id
            qid = start.current_question.question_id
            control["unavailable"] = True
            with pytest.raises(HTTPException) as unavailable:
                await service.submit_answer(
                    db,
                    uid,
                    sid,
                    SubmitAnswerRequest(
                        question_id=qid,
                        answer="Preserve the invariant with an atomic update and check the committed version.",
                    ),
                )
            assert unavailable.value.status_code == 503
        # Fresh Session and fresh service/checkpointer, not just in-memory history.
        with Session(engine, expire_on_commit=False) as db:
            saved = db.scalar(
                select(InterviewTurn).where(InterviewTurn.session_id == sid)
            )
            grade = json.loads(json.dumps(saved.evaluation))
            assert grade["grading_status"] == "completed"
            restarted = InterviewService(llm_provider=llm, checkpointer=MemorySaver())
            stored_session = db.get(InterviewSession, sid)
            assert (
                "test_private_family_1"
                in stored_session.graph_state["asked_question_fingerprints"]
            )
            loaded = restarted.get_session(db, uid, sid)
            assert loaded.generation_unavailable and loaded.current_question is None
            control["unavailable"] = False
            result = await restarted.retry_question(db, uid, sid)
            assert (
                result.current_question.difficulty == "hard"
                and not result.generation_unavailable
            )
            db.expire_all()
            assert (
                db.scalar(
                    select(InterviewTurn).where(
                        InterviewTurn.question_id == qid,
                        InterviewTurn.session_id == sid,
                    )
                ).evaluation
                == grade
            )
            assert llm.eval_counter == 1

    try:
        anyio.run(scenario)
    finally:
        assert re.fullmatch(r"test_phase71_[0-9a-f]{32}", name)
        with base.begin() as c:
            c.execute(text(f'DROP SCHEMA "{name}" CASCADE'))
        base.dispose()


def test_unavailable_grading_stays_unavailable_when_question_generation_also_fails(
    interview_env, monkeypatch
):
    client, sessions, llm = interview_env
    control = controlled_generation(monkeypatch)
    headers, analysis = _create_user_and_analysis(
        client, sessions, "unavailable-grade@example.com"
    )
    start = client.post(
        "/interview/start",
        headers=headers,
        json={
            "analysis_id": analysis,
            "starting_difficulty": "hard",
            "progression_mode": "mock",
            "max_questions": 2,
            "max_follow_ups": 0,
        },
    ).json()
    llm.fail_all = True
    control["unavailable"] = True
    result = client.post(
        f"/interview/{start['session_id']}/answer",
        headers=headers,
        json={
            "question_id": start["current_question"]["question_id"],
            "answer": "A candidate answer whose grade is unavailable.",
        },
    )
    assert result.status_code == 503
    with sessions() as db:
        turn = db.scalar(
            select(InterviewTurn).where(InterviewTurn.session_id == start["session_id"])
        )
        assert (
            turn.evaluation["grading_status"] == "unavailable"
            and turn.evaluation.get("overall_score") is None
        )
        assert turn.answer_text
    ended = client.post(f"/interview/{start['session_id']}/end", headers=headers)
    assert (
        ended.status_code == 200
        and ended.json()["status"] == "completed"
        and not ended.json()["generation_unavailable"]
    )
