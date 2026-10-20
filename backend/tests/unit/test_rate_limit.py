
import pytest
from fastapi import HTTPException

from app.core import rate_limit


@pytest.fixture(autouse=True)
def clear_attempts():
    with rate_limit._lock:
        rate_limit._failed_attempts.clear()


def test_login_allowed_before_failure_limit():
    rate_limit.record_failed_login("192.0.2.1")

    rate_limit.check_login_rate_limit("192.0.2.1")


def test_login_blocked_after_five_failed_attempts():
    ip = "192.0.2.2"

    for _ in range(rate_limit.MAX_FAILED_LOGIN_ATTEMPTS):
        rate_limit.record_failed_login(ip)

    with pytest.raises(HTTPException) as exc_info:
        rate_limit.check_login_rate_limit(ip)

    assert exc_info.value.status_code == 429
    assert exc_info.value.headers["Retry-After"] == "60"


def test_different_ips_have_separate_limits():
    ip_a = "192.0.2.3"
    ip_b = "192.0.2.4"

    for _ in range(rate_limit.MAX_FAILED_LOGIN_ATTEMPTS):
        rate_limit.record_failed_login(ip_a)

    rate_limit.check_login_rate_limit(ip_b)


def test_success_clears_failed_attempts():
    ip = "192.0.2.5"

    for _ in range(rate_limit.MAX_FAILED_LOGIN_ATTEMPTS):
        rate_limit.record_failed_login(ip)

    rate_limit.clear_login_attempts(ip)

    rate_limit.check_login_rate_limit(ip)


def test_expired_attempts_are_removed(monkeypatch):
    current_time = [100.0]
    monkeypatch.setattr(
        rate_limit,
        "monotonic",
        lambda: current_time[0],
    )

    ip = "192.0.2.6"

    for _ in range(rate_limit.MAX_FAILED_LOGIN_ATTEMPTS):
        rate_limit.record_failed_login(ip)

    current_time[0] += rate_limit.LOGIN_WINDOW_SECONDS + 1

    rate_limit.check_login_rate_limit(ip)
