"""Turn grading persistence across graph transitions; opt-in isolated PostgreSQL schema."""
import os
import uuid
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from langgraph.checkpoint.memory import MemorySaver
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.db.session import get_db
from app.db.models import User, Resume, ResumeAnalysis, InterviewSession, InterviewTurn, InterviewReport
from app.main import app
from app.modules.interview.router import service
from app.modules.interview.service import _evaluation_for_turn
from app.modules.interview.rubric import RUBRIC_DIMENSIONS, HR_RUBRIC_DIMENSIONS
from tests.integration.test_interview_flow import ScriptedInterviewLLM, _create_user_and_analysis
from tests.integration.test_phase4a_personalization_and_hr import ScriptedHRLLM


@pytest.fixture
def persistence_env(monkeypatch):
    monkeypatch.setattr(settings, 'jwt_secret_key', 'persistence-test-secret-at-least-32-bytes')
    schema = None
    if os.getenv('PREPMATE_PERSISTENCE_POSTGRES') == '1':
        base = create_engine(settings.database_url)
        schema = 'test_voice_' + uuid.uuid4().hex
        with base.begin() as connection:
            connection.execute(text(f'CREATE SCHEMA "{schema}"'))
        engine = base.execution_options(schema_translate_map={None: schema})
    else:
        engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    for model in (User, Resume, ResumeAnalysis, InterviewSession, InterviewTurn, InterviewReport):
        model.__table__.create(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    def database():
        with factory() as db:
            yield db
    previous = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = database
    monkeypatch.setattr(service, 'checkpointer', MemorySaver())
    # Never invoke embedding or LLM services, even in PostgreSQL mode.
    monkeypatch.setattr('app.modules.interview.nodes.retrieve_chunks_async', AsyncMock(return_value=[]))
    monkeypatch.setattr('app.modules.reports.service.retrieve_chunks_async', AsyncMock(return_value=[]))
    monkeypatch.setattr('app.modules.reports.service.generate_recommendations', AsyncMock(return_value=[]))
    try:
        with TestClient(app) as client:
            yield client, factory
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)
        if schema:
            # Only the schema uniquely created above; never application tables.
            with base.begin() as connection:
                connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        engine.dispose()


@pytest.mark.parametrize('kind', ['technical', 'hr'])
@pytest.mark.parametrize('follow_up', [False, True])
@pytest.mark.parametrize('failure', [False, True])
def test_persist_each_turn_across_progression_restart_duplicates_and_reports(persistence_env, monkeypatch, kind, follow_up, failure):
    client, factory = persistence_env
    llm = (ScriptedHRLLM(need_follow_up=follow_up, fail_all=failure) if kind == 'hr'
           else ScriptedInterviewLLM(follow_up_first=follow_up, fail_all=failure))
    monkeypatch.setattr(service, 'llm_provider', llm)
    headers, analysis = _create_user_and_analysis(client, factory, 'persistence@example.com')
    response = client.post('/interview/start', headers=headers, json={
        'analysis_id': analysis, 'interview_type': kind, 'max_questions': 2, 'max_follow_ups': 1})
    assert response.status_code == 201
    state = response.json()
    sid = state['session_id']
    snapshots = {}
    seen_follow_up = False
    while state['status'] != 'completed':
        question = state['current_question']
        qid = question['question_id']
        seen_follow_up |= question['is_follow_up']
        # Recover from a missing process checkpoint on every transition.
        monkeypatch.setattr(service, 'checkpointer', MemorySaver())
        assert client.get(f'/interview/{sid}', headers=headers).json()['current_question']['question_id'] == qid
        response = client.post(f'/interview/{sid}/answer', headers=headers,
                               json={'question_id': qid, 'answer': 'A detailed answer with context and a practical example.'})
        assert response.status_code == 200
        state = response.json()
        with factory() as db:
            turn = db.query(InterviewTurn).filter_by(session_id=sid, question_id=qid).one()
            grade = turn.evaluation
            assert grade is not None
            assert grade['rubric_version'] == ('v1.0-hr' if kind == 'hr' else 'v1.0')
            if failure:
                assert grade['grading_status'] == 'unavailable'
                assert grade['overall_score'] is None
            else:
                assert grade['grading_status'] == 'completed'
                dims = HR_RUBRIC_DIMENSIONS if kind == 'hr' else RUBRIC_DIMENSIONS
                assert all(grade[dim]['score'] is not None for dim in dims)
            # Compare to the grade for this exact question, not the next question.
            stored = db.get(InterviewSession, sid).graph_state
            assert grade == _evaluation_for_turn(stored, qid)
            snapshots[qid] = grade
        duplicate = client.post(f'/interview/{sid}/answer', headers=headers,
                                json={'question_id': qid, 'answer': 'Attempt to overwrite'})
        assert duplicate.status_code in (400, 409)
        with factory() as db:
            for turn in db.query(InterviewTurn).filter_by(session_id=sid).all():
                if turn.question_id in snapshots:
                    assert turn.evaluation == snapshots[turn.question_id]
                    assert turn.answer_text != 'Attempt to overwrite'
    if not failure:
        assert seen_follow_up == follow_up
    report = client.post(f'/reports/interviews/{sid}/generate', headers=headers)
    assert report.status_code == 200, report.text
    coverage = report.json()['evaluation_coverage']
    assert coverage['evaluated_count'] == (0 if failure else len(snapshots))
    assert coverage['unavailable_count'] == (len(snapshots) if failure else 0)
    with factory() as db:
        persisted = db.query(InterviewReport).filter_by(session_id=sid).one()
        assert persisted.evaluation_coverage == coverage


def test_missing_history_never_reuses_another_turn_or_transient_grade():
    state = {'current_evaluation': {'overall_score': 99}, 'evaluation_history': [
        {'question_id': 'other', 'overall_score': 95}]}
    assert _evaluation_for_turn(state, 'submitted') == {'grading_status': 'unavailable', 'overall_score': None}
