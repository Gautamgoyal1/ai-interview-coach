from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.core.config import Settings, settings
from app.core import staging_budget
from app.db.models.staging_usage import StagingAIUsage


def test_staging_requires_explicit_testers_small_concurrency_and_pool():
    common = dict(_env_file=None, staging_enabled=True, ai_global_concurrency=2)
    with pytest.raises(ValidationError):
        Settings(**common, staging_allowed_emails=[])
    with pytest.raises(ValidationError):
        Settings(**{**common, 'ai_global_concurrency': 3}, staging_allowed_emails=['tester@example.com'])
    with pytest.raises(ValidationError):
        Settings(**common, staging_allowed_emails=['tester@example.com'], db_pool_size=1, db_max_overflow=1)
    assert Settings(**common, staging_allowed_emails=[' TESTER@example.com ', 'tester@example.com']).staging_allowed_emails == ['tester@example.com']


@pytest.mark.parametrize('value', ['*', '0.0.0.0/0', '::/0', 'proxy.example'])
def test_unbounded_or_unresolved_proxy_trust_is_rejected(value):
    with pytest.raises(ValidationError):
        Settings(_env_file=None, forwarded_allow_ips=value)


@pytest.mark.parametrize('value', ['', '127.0.0.1', '10.4.0.0/16,::1'])
def test_explicit_proxy_config(value):
    assert Settings(_env_file=None, forwarded_allow_ips=value).forwarded_allow_ips == value


def test_cloud_staging_requires_database_identity_verification():
    values = dict(_env_file=None, app_env='production', cors_origins=['https://ui.example'], staging_enabled=True,
                  staging_allowed_emails=['tester@example.com'], ai_global_concurrency=2)
    with pytest.raises(ValidationError):
        Settings(**values, database_url='postgresql+psycopg://host/db?sslmode=require')
    assert Settings(**values, database_url='postgresql+psycopg://host/db?sslmode=verify-full').staging_enabled


def test_untrusted_forwarded_headers_cannot_change_limiter_identity():
    from fastapi.testclient import TestClient
    from starlette.responses import JSONResponse
    from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
    async def endpoint(scope, receive, send):
        await JSONResponse({'ip':scope['client'][0], 'scheme':scope['scheme']})(scope, receive, send)
    headers = {'X-Forwarded-For':'attacker-controlled', 'X-Forwarded-Proto':'https'}
    client = TestClient(ProxyHeadersMiddleware(endpoint, trusted_hosts=[]))
    assert client.get('/', headers=headers).json() == {'ip':'testclient','scheme':'http'}


def test_durable_limits_atomic_rollback_and_new_engine_recovery(tmp_path, monkeypatch):
    url = 'sqlite:///' + (tmp_path / 'quota.sqlite').as_posix()
    engine = create_engine(url)
    StagingAIUsage.__table__.create(engine)
    factory = sessionmaker(engine)
    monkeypatch.setattr(staging_budget, 'SessionLocal', factory)
    monkeypatch.setattr(settings, 'staging_ai_user_daily_limit', 1)
    monkeypatch.setattr(settings, 'staging_ai_global_daily_limit', 2)
    staging_budget.reserve_staging_request(7)
    with pytest.raises(HTTPException) as error:
        staging_budget.reserve_staging_request(7)
    assert error.value.status_code == 429
    assert int(error.value.headers['Retry-After']) > 0
    # Failed user reservation must not consume a global reservation.
    with factory() as db:
        assert db.scalar(select(StagingAIUsage.requests).where(StagingAIUsage.bucket == 'global')) == 1
    engine.dispose()
    replacement = create_engine(url)
    monkeypatch.setattr(staging_budget, 'SessionLocal', sessionmaker(replacement))
    staging_budget.reserve_staging_request(8)
    with pytest.raises(HTTPException) as error:
        staging_budget.reserve_staging_request(9)
    assert error.value.status_code == 429
    replacement.dispose()


def test_budget_database_failure_fails_closed(monkeypatch):
    from sqlalchemy.exc import OperationalError
    factory = Mock()
    factory.begin.side_effect = OperationalError('private query', {}, Exception('private password'))
    monkeypatch.setattr(staging_budget, 'SessionLocal', factory)
    with pytest.raises(HTTPException) as error:
        staging_budget.reserve_staging_request(1)
    assert error.value.status_code == 503
    assert 'private password' not in error.value.detail


def test_budget_resets_on_utc_day_not_process_restart(tmp_path, monkeypatch):
    engine = create_engine('sqlite:///' + (tmp_path / 'days.sqlite').as_posix())
    StagingAIUsage.__table__.create(engine)
    monkeypatch.setattr(staging_budget, 'SessionLocal', sessionmaker(engine))
    monkeypatch.setattr(settings, 'staging_ai_user_daily_limit', 1)
    class Clock(datetime):
        day = 1
        @classmethod
        def now(cls, tz=None):
            return datetime(2026, 1, cls.day, tzinfo=timezone.utc)
    monkeypatch.setattr(staging_budget, 'datetime', Clock)
    staging_budget.reserve_staging_request(1)
    Clock.day = 2
    staging_budget.reserve_staging_request(1)
    with sessionmaker(engine)() as db:
        assert len(db.scalars(select(StagingAIUsage)).all()) == 4
    engine.dispose()


def test_resume_service_does_not_construct_a_paid_provider_at_boot(monkeypatch):
    from app.modules.resume import service
    factory = Mock(side_effect=AssertionError('must remain lazy'))
    monkeypatch.setattr(service, 'get_llm_provider', factory)
    assert service.ResumeAnalysisService()._llm is None
    factory.assert_not_called()
