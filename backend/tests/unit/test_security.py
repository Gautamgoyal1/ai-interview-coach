
from datetime import timedelta

import jwt
import pytest

from app.core import security


TEST_JWT_SECRET = "test-secret-for-unit-tests-only-32-bytes-min"


def test_password_is_hashed_and_verifies():
    password = "Example-Strong-Password-123!"
    hashed = security.hash_password(password)

    assert hashed != password
    assert security.verify_password(password, hashed)
    assert not security.verify_password("wrong-password", hashed)


def test_empty_password_is_rejected():
    with pytest.raises(ValueError):
        security.hash_password("")


def test_password_over_bcrypt_limit_is_rejected():
    with pytest.raises(ValueError):
        security.hash_password("a" * 73)


def test_access_token_round_trip(monkeypatch):
    monkeypatch.setattr(
        security.settings,
        "jwt_secret_key",
        TEST_JWT_SECRET,
    )

    token = security.create_access_token("123")
    payload = security.decode_access_token(token)

    assert payload["sub"] == "123"
    assert payload["type"] == "access"


def test_expired_token_is_rejected(monkeypatch):
    monkeypatch.setattr(
        security.settings,
        "jwt_secret_key",
        TEST_JWT_SECRET,
    )

    token = security.create_access_token(
        "123",
        expires_delta=timedelta(seconds=-1),
    )

    with pytest.raises(jwt.ExpiredSignatureError):
        security.decode_access_token(token)


def test_wrong_secret_is_rejected(monkeypatch):
    monkeypatch.setattr(
        security.settings,
        "jwt_secret_key",
        TEST_JWT_SECRET,
    )
    token = security.create_access_token("123")

    monkeypatch.setattr(
        security.settings,
        "jwt_secret_key",
        "another-test-secret-that-is-at-least-32-bytes",
    )

    with pytest.raises(jwt.InvalidTokenError):
        security.decode_access_token(token)
