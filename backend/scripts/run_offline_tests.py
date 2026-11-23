"""Container entrypoint for the public isolated test runner; never a live DB."""

import importlib
import json
import os
from pathlib import Path
import sys

sys.path.insert(0, "/app")
from sqlalchemy.engine import make_url
from app.core.config import settings


def main():
    host = make_url(settings.database_url).host or ""
    if not host.startswith("prepmate-test-"):
        raise RuntimeError(
            "Use scripts/test_backend_isolated.py; refusing non-disposable database"
        )
    # Preserve explicit ASGI/MockTransport tests while blocking paid HTTP clients.
    blocked_requests = {}
    for name in ["httpx", "httpx2"]:
        try:
            module = importlib.import_module(name)
        except ImportError:
            continue

        async def blocked_async(*args, _http=module, **kwargs):
            blocked_requests[_http.__name__] = (
                blocked_requests.get(_http.__name__, 0) + 1
            )
            raise _http.ConnectError("External HTTP disabled for offline tests")

        def blocked_sync(*args, _http=module, **kwargs):
            blocked_requests[_http.__name__] = (
                blocked_requests.get(_http.__name__, 0) + 1
            )
            raise _http.ConnectError("External HTTP disabled for offline tests")

        module.AsyncHTTPTransport.handle_async_request = blocked_async
        module.HTTPTransport.handle_request = blocked_sync
    from alembic.config import Config
    from alembic import command

    command.upgrade(Config("/app/alembic.ini"), "head")
    os.environ.update(PREPMATE_VECTOR_POSTGRES="1", PREPMATE_KNOWLEDGE_POSTGRES="1", PREPMATE_PERSISTENCE_POSTGRES="1", PREPMATE_STAGING_POSTGRES="1")
    import pytest

    code = pytest.main(
        [
            "/app/tests",
            "-q",
            "-p",
            "no:cacheprovider",
            "--basetemp=/tmp/prepmate-pytest",
            "--junitxml=/app/storage/pytest.xml",
        ]
    )
    Path("/app/storage/result.json").write_text(
        json.dumps(
            dict(
                backend_exit_code=int(code),
                fresh_migrations=True,
                disposable_postgres=True,
                external_http_disabled=True,
                blocked_transport_attempts=blocked_requests,
                live_database_access=False,
            ),
            indent=2,
        )
        + "\n"
    )
    raise SystemExit(code)


if __name__ == "__main__":
    main()
