
"""In-memory rate limiting for authentication endpoints."""

from collections import defaultdict, deque
from threading import Lock
from time import monotonic

from fastapi import HTTPException, status


LOGIN_WINDOW_SECONDS = 60
MAX_FAILED_LOGIN_ATTEMPTS = 5

_failed_attempts: dict[str, deque[float]] = defaultdict(deque)
_lock = Lock()


def _remove_expired_attempts(
    attempts: deque[float],
    now: float,
) -> None:
    """Remove failed attempts outside the rolling time window."""
    cutoff = now - LOGIN_WINDOW_SECONDS

    while attempts and attempts[0] <= cutoff:
        attempts.popleft()


def check_login_rate_limit(client_ip: str) -> None:
    """Reject login requests after too many recent failures."""
    now = monotonic()

    with _lock:
        attempts = _failed_attempts[client_ip]
        _remove_expired_attempts(attempts, now)

        if len(attempts) >= MAX_FAILED_LOGIN_ATTEMPTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many failed login attempts. Please try again later.",
                headers={"Retry-After": str(LOGIN_WINDOW_SECONDS)},
            )


def record_failed_login(client_ip: str) -> None:
    """Record a failed login attempt."""
    now = monotonic()

    with _lock:
        attempts = _failed_attempts[client_ip]
        _remove_expired_attempts(attempts, now)
        attempts.append(now)


def clear_login_attempts(client_ip: str) -> None:
    """Clear failed attempts after a successful login."""
    with _lock:
        _failed_attempts.pop(client_ip, None)
