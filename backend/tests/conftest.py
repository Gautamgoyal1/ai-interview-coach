"""Reset process-local HTTP admission state between isolated tests."""

import pytest


@pytest.fixture(autouse=True)
def isolated_request_limits():
    from app.core.rate_limit import request_limiter

    request_limiter.clear()
    yield
    request_limiter.clear()
