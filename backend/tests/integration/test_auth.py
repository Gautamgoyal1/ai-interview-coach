"""HTTP integration tests for registration, login, and /auth/me."""

from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.security import create_access_token
from app.db.models.user import User
from app.db.session import get_db
from app.main import app


@pytest.fixture
def sqlite_client(monkeypatch):
    """Provide a TestClient backed by an isolated in-memory SQLite DB."""
    monkeypatch.setattr(
        settings,
        "jwt_secret_key",
        "test-jwt-secret-key-at-least-32-bytes-long",
    )

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    User.__table__.create(bind=engine)
    TestingSession = sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    previous_override = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as client:
            yield client
    finally:
        if previous_override is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = previous_override
        engine.dispose()


def test_register_login_and_get_me_flow(sqlite_client: TestClient):
    """Users can register, log in for a JWT, and fetch /auth/me."""
    register_res = sqlite_client.post(
        "/auth/register",
        json={"email": "alice@example.com", "password": "strongpassword123"},
    )
    assert register_res.status_code == 201
    user_data = register_res.json()
    assert user_data["email"] == "alice@example.com"
    assert "id" in user_data

    login_res = sqlite_client.post(
        "/auth/login",
        json={"email": "alice@example.com", "password": "strongpassword123"},
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    assert token

    me_res = sqlite_client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "alice@example.com"
    assert me_res.json()["id"] == user_data["id"]


def test_register_duplicate_email_returns_409(sqlite_client: TestClient):
    """Registering the same email twice returns 409 Conflict."""
    payload = {"email": "dup@example.com", "password": "strongpassword123"}
    assert sqlite_client.post("/auth/register", json=payload).status_code == 201
    dup_res = sqlite_client.post("/auth/register", json=payload)
    assert dup_res.status_code == 409


def test_login_invalid_password_returns_401(sqlite_client: TestClient):
    """Wrong password returns 401 Unauthorized."""
    sqlite_client.post(
        "/auth/register",
        json={"email": "bob@example.com", "password": "strongpassword123"},
    )
    login_res = sqlite_client.post(
        "/auth/login",
        json={"email": "bob@example.com", "password": "wrongpassword"},
    )
    assert login_res.status_code == 401


def test_me_rejects_missing_invalid_and_expired_jwt(sqlite_client: TestClient):
    """Protected /auth/me rejects missing, malformed, and expired tokens."""
    assert sqlite_client.get("/auth/me").status_code == 401

    invalid_res = sqlite_client.get(
        "/auth/me",
        headers={"Authorization": "Bearer not-a-valid-jwt"},
    )
    assert invalid_res.status_code == 401

    expired_token = create_access_token(
        "1",
        expires_delta=timedelta(minutes=-5),
    )
    expired_res = sqlite_client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert expired_res.status_code == 401
