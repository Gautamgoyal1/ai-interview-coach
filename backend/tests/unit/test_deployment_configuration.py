from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy.exc import OperationalError

from app.core.config import Settings, settings
from app.core.response_headers import ResponseHeadersMiddleware
from app.main import app


def config(**kwargs):
    return Settings(_env_file=None, **kwargs)


@pytest.mark.parametrize("origin", ["*", "https://*.example.com", "https://ui.example/path", "https://u:p@ui.example", "https://ui.example/", "file://ui.example"])
def test_cors_rejects_ambiguous_origins(origin):
    with pytest.raises(ValidationError):
        config(cors_origins=[origin])


def test_production_requires_public_https_and_database_tls():
    with pytest.raises(ValidationError):
        config(app_env="production", database_url="postgresql+psycopg://example/db?sslmode=require")
    with pytest.raises(ValidationError):
        config(app_env="production", cors_origins=["https://ui.example"], database_url="postgresql+psycopg://example/db")
    value = config(app_env="production", cors_origins=["https://ui.example"], database_url="postgresql+psycopg://example/db?sslmode=require")
    assert value.db_pool_size + value.db_max_overflow == 10


def test_invalid_configuration_does_not_print_secrets():
    with pytest.raises(ValidationError) as error:
        config(app_env="production", cors_origins=["https://ui.example"], database_url="postgresql+psycopg://user:private-password@example/db")
    assert "private-password" not in str(error.value)


def test_cors_allows_configured_browser_and_rejects_other_origins():
    with TestClient(app) as client:
        for origin, expected in [(settings.cors_origins[0], 200), ("https://attacker.invalid", 400)]:
            response = client.options("/auth/login", headers={"Origin": origin, "Access-Control-Request-Method": "POST", "Access-Control-Request-Headers": "authorization,content-type"})
            assert response.status_code == expected
            assert response.headers.get("Access-Control-Allow-Origin") == (origin if expected == 200 else None)
        response = client.get("/auth/me")
        assert response.status_code == 401
        assert response.headers["Cache-Control"] == "private, no-store"
        assert response.headers["X-Content-Type-Options"] == "nosniff"


def test_readiness_fails_closed_without_database_details(monkeypatch):
    from app import main
    fake = Mock()
    fake.connect.side_effect = OperationalError("private query", {}, RuntimeError("private host/password"))
    monkeypatch.setattr(main, "engine", fake)
    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
        response = client.get("/health/ready")
        assert response.status_code == 503
        assert response.json() == {"detail": "Database is temporarily unavailable."}
    fake.dispose.assert_called_once()


def test_production_response_policy_applies_to_rejections():
    async def endpoint(scope, receive, send):
        await send({"type": "http.response.start", "status": 429, "headers": []})
        await send({"type": "http.response.body", "body": b"bounded"})
    response = TestClient(ResponseHeadersMiddleware(endpoint, production=True)).get("/")
    assert response.headers["Strict-Transport-Security"] == "max-age=31536000"
    assert response.headers["Content-Security-Policy"] == "default-src 'none'; frame-ancestors 'none'"
