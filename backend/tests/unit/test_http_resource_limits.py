import asyncio
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi import HTTPException
from starlette.responses import JSONResponse

from app.core import rate_limit
from app.core.body_limit import RequestBodyLimitMiddleware
from app.core.rate_limit import RequestLimiter


def test_admission_is_atomic_under_concurrent_attempts():
    limiter = RequestLimiter()

    def attempt(_):
        try:
            limiter.consume([("one-account", 5, 60)])
            return 200
        except HTTPException as exc:
            return exc.status_code

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(attempt, range(20)))
    assert results.count(200) == 5
    assert results.count(429) == 15


def test_quota_expiry_key_bound_and_failed_multi_rule_admission(monkeypatch):
    now = [100.0]
    monkeypatch.setattr(rate_limit, "monotonic", lambda: now[0])
    limiter = RequestLimiter(max_keys=2)
    limiter.consume([("global", 1, 60)])
    with pytest.raises(HTTPException):
        limiter.consume([("new-user", 5, 60), ("global", 1, 60)])
    assert ("new-user", 60) not in limiter._buckets
    limiter.consume([("other", 2, 60)])
    with pytest.raises(HTTPException):
        limiter.consume([("overflow", 2, 60)])
    now[0] += 61
    limiter.consume([("overflow", 2, 60)])
    assert len(limiter._buckets) == 1


def test_concurrency_capacity_is_released_on_provider_failure():
    limiter = RequestLimiter()
    with pytest.raises(ValueError):
        with limiter.slots([("global", 1)]):
            with pytest.raises(HTTPException) as denied:
                with limiter.slots([("global", 1)]):
                    pytest.fail("Busy provider capacity must not be admitted")
            assert denied.value.status_code == 429
            raise ValueError("simulated provider failure")
    with limiter.slots([("global", 1)]):
        assert limiter._active["global"] == 1
    assert not limiter._active


def test_ai_quota_cannot_be_bypassed_by_switching_accounts_or_endpoints():
    for user in range(30):
        rate_limit.admit_ai(user, "192.0.2.1")
    with pytest.raises(HTTPException):
        rate_limit.admit_ai(999, "192.0.2.1")
    rate_limit.admit_ai(999, "192.0.2.2")


@pytest.mark.parametrize("headers,chunks", [
    ([(b"content-length", b"9")], []),
    ([], [b"1234", b"56789"]),
    ([(b"content-length", b"1")], [b"123456789"]),
])
def test_body_limit_rejects_before_downstream_or_multipart_parsing(headers, chunks):
    async def scenario():
        reached = []
        messages = []

        async def downstream(*args):
            reached.append(True)

        async def receive():
            body = chunks.pop(0)
            return {"type": "http.request", "body": body, "more_body": bool(chunks)}

        async def send(message):
            messages.append(message)

        middleware = RequestBodyLimitMiddleware(downstream, max_bytes=8)
        await middleware({"type": "http", "method": "POST", "headers": headers}, receive, send)
        assert messages[0]["status"] == 413
        assert not reached
        assert middleware._active == 0

    asyncio.run(scenario())


def test_body_timeout_and_busy_capacity_are_bounded():
    async def scenario():
        async def never_called(*args):
            pytest.fail("Downstream parser must not run")

        async def receive():
            await asyncio.sleep(1)

        middleware = RequestBodyLimitMiddleware(never_called, timeout=0.01, max_active=1)
        scope = {"type": "http", "method": "POST", "headers": []}
        messages = []

        async def send(message):
            messages.append(message)

        await middleware(scope, receive, send)
        assert messages[0]["status"] == 408
        assert middleware._active == 0
        middleware._active = 1
        messages.clear()
        await middleware(scope, receive, send)
        assert messages[0]["status"] == 503

    asyncio.run(scenario())


def test_bounded_body_replays_without_changing_valid_request_bytes():
    async def scenario():
        chunks = [b"valid ", b"body"]
        messages = []

        async def receive():
            return {"type": "http.request", "body": chunks.pop(0), "more_body": bool(chunks)}

        async def downstream(scope, receive, send):
            assert middleware._active == 0
            assert not middleware._clients
            message = await receive()
            assert message["body"] == b"valid body"
            assert not message["more_body"]
            await JSONResponse({"ok": True})(scope, receive, send)

        async def send(message):
            messages.append(message)

        middleware = RequestBodyLimitMiddleware(downstream, max_bytes=20)
        await middleware({"type": "http", "method": "POST", "headers": []}, receive, send)
        assert messages[0]["status"] == 200
        assert middleware._active == 0

    asyncio.run(scenario())


def test_one_slow_client_cannot_occupy_all_body_readers():
    async def scenario():
        async def downstream(*args):
            pytest.fail("No complete body should be admitted")

        async def receive():
            pytest.fail("Busy client body must not be read")

        messages = []

        async def send(message):
            messages.append(message)

        middleware = RequestBodyLimitMiddleware(downstream)
        middleware._active = 2
        middleware._clients["192.0.2.1"] = 2
        await middleware({"type": "http", "method": "POST", "headers": [], "client": ("192.0.2.1", 1234)}, receive, send)
        assert messages[0]["status"] == 503
        assert middleware._active == 2

    asyncio.run(scenario())
