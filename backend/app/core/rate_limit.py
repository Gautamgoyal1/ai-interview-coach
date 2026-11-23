
"""Single-worker, thread-safe HTTP admission limits; never trust forwarded IP headers here."""

from collections import defaultdict, deque
from threading import Lock
from time import monotonic
from contextlib import contextmanager
from hashlib import sha256
from math import ceil

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
        for ip, bucket in list(_failed_attempts.items()):
            _remove_expired_attempts(bucket, now)
            if not bucket:
                _failed_attempts.pop(ip, None)
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


class RequestLimiter:
    """Atomically consume all applicable quotas, with bounded key storage."""

    def __init__(self, max_keys: int = 10000):
        self.max_keys = max_keys
        self._buckets: dict[tuple[str, int], deque[float]] = {}
        self._active: dict[str, int] = {}
        self._mutex = Lock()

    def clear(self) -> None:
        with self._mutex:
            self._buckets.clear()
            self._active.clear()

    def consume(self, rules: list[tuple[str, int, int]]) -> None:
        now = monotonic()
        with self._mutex:
            for key, entries in list(self._buckets.items()):
                while entries and entries[0] <= now - key[1]:
                    entries.popleft()
                if not entries:
                    self._buckets.pop(key)
            new_keys = {(key, window) for key, _, window in rules} - self._buckets.keys()
            if len(self._buckets) + len(new_keys) > self.max_keys:
                self._reject(60)
            for key, limit, window in rules:
                entries = self._buckets.get((key, window), ())
                if len(entries) >= limit:
                    self._reject(max(1, ceil(entries[0] + window - now)))
            for key, _, window in rules:
                self._buckets.setdefault((key, window), deque()).append(now)

    @staticmethod
    def _reject(retry: int) -> None:
        raise HTTPException(429, "Too many requests. Please try again later.", headers={"Retry-After": str(retry)})

    @contextmanager
    def slots(self, rules: list[tuple[str, int]]):
        with self._mutex:
            if any(self._active.get(key, 0) >= limit for key, limit in rules):
                self._reject(1)
            for key, _ in rules:
                self._active[key] = self._active.get(key, 0) + 1
        try:
            yield
        finally:
            with self._mutex:
                for key, _ in rules:
                    count = self._active[key] - 1
                    if count:
                        self._active[key] = count
                    else:
                        self._active.pop(key)


request_limiter = RequestLimiter()


def admit_login(client_ip: str, email: str) -> None:
    # A successful login cannot erase this independent attempt counter.
    account = sha256(email.strip().lower().encode()).hexdigest()
    request_limiter.consume([
        (f"login:ip:{client_ip}", 20, 60),
        (f"login:account:{account}", 5, 60),
        ("login:global", 200, 60),
    ])


def admit_registration(client_ip: str) -> None:
    request_limiter.consume([
        (f"register:ip:{client_ip}", 5, 3600),
        ("register:global", 50, 3600),
    ])


def admit_ai(user_id: int, client_ip: str) -> None:
    # Shared across AI routes: changing endpoint or account does not reset the IP/global quota.
    request_limiter.consume([
        (f"ai:user:{user_id}", 12, 60), (f"ai:user:{user_id}", 200, 86400),
        (f"ai:ip:{client_ip}", 30, 60), (f"ai:ip:{client_ip}", 500, 86400),
        ("ai:global", 60, 60), ("ai:global", 2000, 86400),
    ])
