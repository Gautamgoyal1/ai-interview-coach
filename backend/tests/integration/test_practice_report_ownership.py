import uuid

import pytest
from sqlalchemy import func, select

from app.db.models.interview_session import InterviewSession
from app.db.models.practice import PracticeSession
from app.db.models.report import InterviewReport
from tests.integration.test_phase4b_practice_and_coach import fixture_client_and_session as client_and_session, _create_user_and_auth


def test_foreign_and_missing_report_associations_fail_before_generation(client_and_session):
    client, SessionLocal, provider = client_and_session
    owner, _ = _create_user_and_auth(client, SessionLocal, "report-owner@example.com")
    _, headers = _create_user_and_auth(client, SessionLocal, "report-other@example.com")
    with SessionLocal() as db:
        session = InterviewSession(id=str(uuid.uuid4()), user_id=owner, resume_analysis_id=1, target_role="Software Engineer", status="completed", configuration={})
        db.add(session); db.flush()
        report = InterviewReport(session_id=session.id, user_id=owner, target_role="Software Engineer", interview_type="hr", overall_score=None, status="completed", rubric_version="v1.0")
        db.add(report); db.commit(); report_id = report.id
    for value in [report_id, report_id + 999]:
        response = client.post("/practice/sessions", headers=headers, json={"topic": "Teamwork", "source_report_id": value, "interview_type": "hr"})
        assert response.status_code == 404
        assert response.json() == {"detail": "Source report not found."}
    with SessionLocal() as db:
        assert db.scalar(select(func.count()).select_from(PracticeSession)) == 0
    assert provider.question_count == 0


def test_own_report_preserves_track_and_generates_practice(client_and_session):
    client, SessionLocal, provider = client_and_session
    owner, headers = _create_user_and_auth(client, SessionLocal, "own-report@example.com")
    with SessionLocal() as db:
        session = InterviewSession(id=str(uuid.uuid4()), user_id=owner, resume_analysis_id=1, target_role="Software Engineer", status="completed", configuration={})
        db.add(session); db.flush()
        report = InterviewReport(session_id=session.id, user_id=owner, target_role="Software Engineer", interview_type="technical", overall_score=None, status="completed", rubric_version="v1.0")
        db.add(report); db.commit(); report_id = report.id
    payload = {"topic": "SQL", "source_report_id": report_id, "interview_type": "hr"}
    assert client.post("/practice/sessions", headers=headers, json=payload).status_code == 422
    payload["interview_type"] = "technical"
    response = client.post("/practice/sessions", headers=headers, json=payload)
    assert response.status_code == 201
    assert response.json()["source_report_id"] == report_id
    assert response.json()["interview_type"] == "technical"
