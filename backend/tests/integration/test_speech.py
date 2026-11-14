"""Offline speech integration tests. Never use configured Azure credentials or user data."""

import httpx
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
from app.modules.speech import router as speech_router
from app.modules.speech.service import SpeechService


@pytest.fixture
def speech_env(monkeypatch):
    monkeypatch.setattr(settings, "jwt_secret_key", "offline-speech-test-key-at-least-32-characters")
    monkeypatch.setattr(settings, "azure_speech_key", "offline-subscription-key")
    monkeypatch.setattr(settings, "azure_speech_region", "eastasia")
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    User.__table__.create(engine)
    factory = sessionmaker(bind=engine)
    with factory() as db:
        db.add_all([User(id=1, email="speech@example.com", password_hash="unused"),
                    User(id=2, email="other@example.com", password_hash="unused")])
        db.commit()

    def override_db():
        with factory() as db:
            yield db

    previous = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = override_db
    service = SpeechService()
    monkeypatch.setattr(speech_router, "speech_service", service)
    upstream = {"status": 200, "error": False, "calls": [], "empty": False}

    def respond(request):
        upstream["calls"].append(request)
        if upstream["error"]:
            raise httpx.ConnectError("PRIVATE Azure diagnostic", request=request)
        if upstream["status"] != 200:
            return httpx.Response(upstream["status"], text="PRIVATE Azure diagnostic")
        payload = b"offline-speech-token" if "issueToken" in str(request.url) else b"offline-mp3"
        return httpx.Response(200, content=b"" if upstream["empty"] else payload)

    real_client = httpx.AsyncClient
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: real_client(
        transport=httpx.MockTransport(respond), **kwargs))
    try:
        with TestClient(app) as client:
            yield client, service, upstream, {"Authorization": f"Bearer {create_access_token('1')}"}
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)
        engine.dispose()


@pytest.mark.parametrize("method,path,body", [
    ("POST", "/speech/token", None), ("GET", "/speech/token", None),
    ("GET", "/speech/voices", None), ("POST", "/speech/synthesize", {"text": "Question"}),
])
def test_unauthorized(speech_env, method, path, body):
    client, _, upstream, _ = speech_env
    assert client.request(method, path, json=body).status_code == 401
    assert not upstream["calls"]


def test_voices(speech_env):
    client, _, _, headers = speech_env
    response = client.get("/speech/voices", headers=headers)
    assert response.status_code == 200
    assert {v["name"] for v in response.json()} == {
        "en-US-JennyNeural", "en-US-AndrewNeural", "en-US-AriaNeural", "en-US-GuyNeural"}


def test_token_cache_and_renewal(speech_env, monkeypatch):
    client, _, upstream, headers = speech_env
    clock = [1000.0]
    monkeypatch.setattr("app.modules.speech.service.time.monotonic", lambda: clock[0])
    first = client.post("/speech/token", headers=headers)
    assert first.status_code == 200
    assert first.headers["cache-control"] == "private, no-store"
    assert "offline-subscription-key" not in first.text
    clock[0] += 100
    cached = client.get("/speech/token", headers=headers)
    assert cached.json()["expires_in"] == 500
    assert len(upstream["calls"]) == 1
    clock[0] += 400
    assert client.post("/speech/token", headers=headers).json()["expires_in"] == 600
    assert len(upstream["calls"]) == 2


@pytest.mark.parametrize("kind,voice", [("technical", "en-US-JennyNeural"), ("hr", "en-US-AriaNeural")])
def test_synthesis_defaults_escape_text_and_disable_caching(speech_env, kind, voice):
    client, _, upstream, headers = speech_env
    response = client.post("/speech/synthesize", headers=headers,
                           json={"text": "A < B & C", "interview_type": kind})
    assert response.status_code == 200
    assert response.content == b"offline-mp3"
    assert response.headers["content-type"] == "audio/mpeg"
    assert response.headers["cache-control"] == "private, no-store"
    ssml = upstream["calls"][-1].content.decode()
    assert voice in ssml
    assert "A &lt; B &amp; C" in ssml


@pytest.mark.parametrize("voice", ["en-US-AndrewNeural", "en-US-GuyNeural"])
def test_supported_voice(speech_env, voice):
    client, _, upstream, headers = speech_env
    assert client.post("/speech/synthesize", headers=headers,
                       json={"text": "Question", "voice_name": voice}).status_code == 200
    assert voice.encode() in upstream["calls"][-1].content


@pytest.mark.parametrize("body", [
    {"text": "Question", "voice_name": "unknown"},
    {"text": "Question", "voice_name": "x'><audio src='evil'/>"},
    {"text": "Question", "interview_type": "invalid"}, {"text": ""}, {"text": "x" * 5001},
])
def test_invalid_input_never_calls_azure(speech_env, body):
    client, _, upstream, headers = speech_env
    assert client.post("/speech/synthesize", headers=headers, json=body).status_code == 422
    assert not upstream["calls"]


@pytest.mark.parametrize("path", ["/speech/token", "/speech/synthesize"])
@pytest.mark.parametrize("failure", ["http", "network", "empty"])
def test_azure_failures_are_controlled(speech_env, path, failure):
    client, _, upstream, headers = speech_env
    upstream.update(status=403 if failure == "http" else 200,
                    error=failure == "network", empty=failure == "empty")
    response = client.post(path, headers=headers, json={"text": "Question"})
    assert response.status_code == 502
    assert "PRIVATE" not in response.text
    assert "offline-subscription-key" not in response.text


@pytest.mark.parametrize("path,attribute", [
    ("/speech/token", "_max_requests_per_window"),
    ("/speech/synthesize", "_max_synthesis_requests_per_window"),
])
def test_rate_limit_is_per_user_and_expires(speech_env, monkeypatch, path, attribute):
    client, service, upstream, headers = speech_env
    clock = [1000.0]
    monkeypatch.setattr("app.modules.speech.service.time.monotonic", lambda: clock[0])
    setattr(service, attribute, 2)
    for _ in range(2):
        assert client.post(path, headers=headers, json={"text": "Question"}).status_code == 200
    count = len(upstream["calls"])
    denied = client.post(path, headers=headers, json={"text": "Question"})
    assert denied.status_code == 429
    assert int(denied.headers["retry-after"]) > 0
    assert len(upstream["calls"]) == count
    other = {"Authorization": f"Bearer {create_access_token('2')}"}
    assert client.post(path, headers=other, json={"text": "Question"}).status_code == 200
    clock[0] += 61
    assert client.post(path, headers=headers, json={"text": "Question"}).status_code == 200


@pytest.mark.parametrize("path", ["/speech/token", "/speech/synthesize"])
def test_unconfigured_service(speech_env, monkeypatch, path):
    client, _, upstream, headers = speech_env
    monkeypatch.setattr(settings, "azure_speech_key", "")
    assert client.post(path, headers=headers, json={"text": "Question"}).status_code == 503
    assert not upstream["calls"]
