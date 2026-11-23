from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from app.core.security import create_access_token
from app.main import app
from app.modules.interview import router as interview_router
from app.modules.practice import router as practice_router
from tests.integration.test_auth import sqlite_client


def register(client, email):
    response = client.post("/auth/register", json={"email": email, "password": "strong-test-password"})
    assert response.status_code == 201
    return {"Authorization": "Bearer " + create_access_token(str(response.json()["id"]))}


def test_successful_login_does_not_reset_victim_account_admission(sqlite_client):
    register(sqlite_client, "victim@example.com")
    register(sqlite_client, "attacker@example.com")
    for _ in range(5):
        assert sqlite_client.post("/auth/login", json={"email": "victim@example.com", "password": "wrong"}).status_code == 401
        assert sqlite_client.post("/auth/login", json={"email": "attacker@example.com", "password": "strong-test-password"}).status_code == 200
    denied = sqlite_client.post("/auth/login", json={"email": "victim@example.com", "password": "wrong"})
    assert denied.status_code == 429
    assert int(denied.headers["Retry-After"]) > 0


def test_registration_is_bounded_before_hashing_or_database_writes(sqlite_client, monkeypatch):
    from app.modules.auth import router

    real_hash = router.hash_password
    calls = []

    def counted(password):
        calls.append(True)
        return real_hash(password)

    monkeypatch.setattr(router, "hash_password", counted)
    for number in range(5):
        register(sqlite_client, f"candidate{number}@example.com")
    denied = sqlite_client.post("/auth/register", json={"email": "extra@example.com", "password": "strong-test-password"})
    assert denied.status_code == 429
    assert len(calls) == 5


def test_ai_routes_share_one_admission_limit_before_service_calls(sqlite_client, monkeypatch):
    headers = register(sqlite_client, "candidate@example.com")
    interview = AsyncMock(side_effect=HTTPException(404, "Not found"))
    practice = AsyncMock(side_effect=HTTPException(404, "Not found"))
    monkeypatch.setattr(interview_router.service, "start_interview", interview)
    monkeypatch.setattr(practice_router.service, "create_session", practice)
    for number in range(12):
        response = sqlite_client.post(
            "/interview/start" if number % 2 else "/practice/sessions",
            json={"analysis_id": 1} if number % 2 else {"topic": "SQL"}, headers=headers,
        )
        assert response.status_code == 404
    denied = sqlite_client.post("/interview/start", json={"analysis_id": 1}, headers=headers)
    assert denied.status_code == 429
    assert interview.await_count + practice.await_count == 12
    assert sqlite_client.get("/auth/me", headers=headers).status_code == 200


@pytest.mark.parametrize("email", ["' OR 1=1 --", "candidate@example.com' --"])
def test_sql_injection_payload_does_not_authenticate(sqlite_client, email):
    register(sqlite_client, "candidate@example.com")
    denied = sqlite_client.post("/auth/login", json={"email": email, "password": "strong-test-password"})
    assert denied.status_code == 401


def test_all_paid_routes_require_shared_authenticated_admission():
    from app.api.dependencies import get_ai_user, get_current_user

    expected = {
        ("POST", "/resume/analyze"), ("POST", "/interview/start"),
        ("POST", "/interview/{session_id}/answer"), ("POST", "/interview/{session_id}/end"),
        ("POST", "/interview/{session_id}/retry-question"),
        ("POST", "/practice/sessions"), ("POST", "/practice/sessions/{session_id}/questions"),
        ("POST", "/practice/questions/{question_id}/attempts"),
        ("POST", "/reports/interviews/{session_id}/generate"),
        ("GET", "/speech/token"), ("POST", "/speech/token"), ("POST", "/speech/synthesize"),
    }

    def dependency_calls(dependant):
        return {dependant.call} | set().union(*(dependency_calls(d) for d in dependant.dependencies))

    def routes_including_lazy_routers(routes):
        for route in routes:
            original_router = getattr(route, "original_router", None)
            if original_router is not None:
                yield from routes_including_lazy_routers(original_router.routes)
            else:
                yield route

    found = set()
    for route in routes_including_lazy_routers(app.routes):
        for method in getattr(route, "methods", []):
            key = (method, route.path)
            if key in expected:
                calls = dependency_calls(route.dependant)
                assert get_ai_user in calls and get_current_user in calls, key
                found.add(key)
    assert found == expected


@pytest.mark.parametrize("path,payload", [
    ("/interview/start", {"analysis_id": 1}),
    ("/practice/sessions", {"topic": "SQL"}),
    ("/speech/token", None),
    ("/speech/synthesize", {"text": "Interview question"}),
    ("/reports/interviews/not-owned/generate", None),
])
def test_anonymous_paid_requests_are_rejected(sqlite_client, path, payload):
    assert sqlite_client.post(path, json=payload).status_code == 401


def test_invalid_pdf_is_rejected_before_ai_or_persistence(sqlite_client, monkeypatch):
    from app.modules.resume.router import service

    headers = register(sqlite_client, "pdf@example.com")
    generate = AsyncMock()
    monkeypatch.setattr(service, "analyze", generate)
    response = sqlite_client.post(
        "/resume/analyze", headers=headers, data={"job_role": "Software Engineer"},
        files={"file": ("resume.pdf", b"%PDF-1.4\nnot a valid document", "application/pdf")},
    )
    assert response.status_code == 422
    generate.assert_not_awaited()
