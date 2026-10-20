
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from passlib.context import CryptContext

from app.core.config import settings


_password_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    """Hash a password before storing it."""
    if not password:
        raise ValueError("Password cannot be empty.")

    if len(password.encode("utf-8")) > 72:
        raise ValueError("Password must not exceed 72 UTF-8 bytes.")

    return _password_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Return whether the password matches the stored hash."""
    if not password or len(password.encode("utf-8")) > 72:
        return False

    try:
        return _password_context.verify(password, password_hash)
    except (ValueError, TypeError):
        return False


def _jwt_secret() -> str:
    """Return the configured JWT secret."""
    secret = settings.jwt_secret_key

    if not secret or not secret.strip():
        raise RuntimeError("JWT_SECRET_KEY must be configured.")

    return secret


def validate_jwt_configuration() -> None:
    """Fail startup when the JWT signing configuration is unsafe."""
    secret = settings.jwt_secret_key

    if not secret or not secret.strip():
        raise RuntimeError("JWT_SECRET_KEY must be configured.")

    if secret != secret.strip():
        raise RuntimeError(
            "JWT_SECRET_KEY must not contain leading or trailing whitespace."
        )

    placeholders = {
        "secret",
        "changeme",
        "change-me",
        "your-secret-key",
        "your_jwt_secret_key",
    }

    if secret.lower() in placeholders:
        raise RuntimeError(
            "JWT_SECRET_KEY must not use a placeholder value."
        )

    if len(secret.encode("utf-8")) < 32:
        raise RuntimeError(
            "JWT_SECRET_KEY must be at least 32 bytes long."
        )

    if settings.jwt_algorithm != "HS256":
        raise RuntimeError(
            "JWT_ALGORITHM must be HS256 for this configuration."
        )


def create_access_token(
    subject: str,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT access token."""
    if not subject:
        raise ValueError("Token subject cannot be empty.")

    now = datetime.now(timezone.utc)
    expires_at = now + (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=settings.access_token_expire_minutes)
    )

    payload: dict[str, Any] = {
        "sub": subject,
        "iat": now,
        "exp": expires_at,
        "type": "access",
    }

    return jwt.encode(
        payload,
        _jwt_secret(),
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> dict[str, Any]:
    """Validate a JWT and return its claims."""
    payload = jwt.decode(
        token,
        _jwt_secret(),
        algorithms=[settings.jwt_algorithm],
        options={"require": ["sub", "exp", "iat", "type"]},
    )

    if payload.get("type") != "access":
        raise jwt.InvalidTokenError("Invalid token type.")

    return payload
