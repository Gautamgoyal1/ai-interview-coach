from unittest.mock import AsyncMock, Mock

import pytest

from app.api import dependencies
from app.core.config import settings
from app.core.security import create_access_token
from app.modules.interview import router
from tests.integration.test_auth import sqlite_client


def invited(sqlite_client, monkeypatch):
    user = sqlite_client.post('/auth/register', json={'email': 'tester@example.com', 'password': 'strong-test-password'}).json()
    monkeypatch.setattr(settings, 'staging_enabled', True)
    monkeypatch.setattr(settings, 'staging_allowed_emails', ['tester@example.com'])
    return {'Authorization': 'Bearer ' + create_access_token(str(user['id']))}


def test_registration_closed_and_uninvited_login_blocked_before_expensive_work(sqlite_client, monkeypatch):
    invited(sqlite_client, monkeypatch)
    from app.modules.auth import router as auth
    hash_password = Mock(side_effect=AssertionError('must not hash'))
    verify_password = Mock(side_effect=AssertionError('must not verify'))
    monkeypatch.setattr(auth, 'hash_password', hash_password)
    monkeypatch.setattr(auth, 'verify_password', verify_password)
    for email in ['tester@example.com', 'outsider@example.com']:
        assert sqlite_client.post('/auth/register', json={'email': email, 'password': 'strong-test-password'}).status_code == 403
    assert sqlite_client.post('/auth/login', json={'email': 'outsider@example.com', 'password': 'password'}).status_code == 403
    hash_password.assert_not_called()
    verify_password.assert_not_called()


def test_invited_login_and_existing_token_revocation(sqlite_client, monkeypatch):
    headers = invited(sqlite_client, monkeypatch)
    assert sqlite_client.post('/auth/login', json={'email': ' TESTER@example.com ', 'password': 'strong-test-password'}).status_code == 200
    assert sqlite_client.get('/auth/me', headers=headers).status_code == 200
    monkeypatch.setattr(settings, 'staging_allowed_emails', ['someone-else@example.com'])
    assert sqlite_client.get('/auth/me', headers=headers).status_code == 403


def test_temporary_registration_only_allows_exact_invited_address(sqlite_client, monkeypatch):
    invited(sqlite_client, monkeypatch)
    monkeypatch.setattr(settings, 'staging_registration_enabled', True)
    monkeypatch.setattr(settings, 'staging_allowed_emails', ['new@example.com'])
    assert sqlite_client.post('/auth/register', json={'email': 'new@example.com.evil', 'password': 'strong-test-password'}).status_code == 403
    assert sqlite_client.post('/auth/register', json={'email': 'new@example.com', 'password': 'strong-test-password'}).status_code == 201


@pytest.mark.parametrize('path,payload', [('/interview/start', {'analysis_id': 1}), ('/speech/token', None), ('/speech/synthesize', {'text': 'Question'}), ('/practice/sessions', {'topic': 'SQL'})])
def test_ai_kill_switch_before_budget_and_provider(sqlite_client, monkeypatch, path, payload):
    headers = invited(sqlite_client, monkeypatch)
    monkeypatch.setattr(settings, 'ai_enabled', False)
    reserve = Mock(side_effect=AssertionError('no usage'))
    monkeypatch.setattr(dependencies, 'reserve_staging_request', reserve)
    assert sqlite_client.post(path, json=payload, headers=headers).status_code == 503
    reserve.assert_not_called()
    assert sqlite_client.get('/auth/me', headers=headers).status_code == 200


def test_speech_can_be_disabled_independently(sqlite_client, monkeypatch):
    headers = invited(sqlite_client, monkeypatch)
    monkeypatch.setattr(settings, 'ai_enabled', True)
    monkeypatch.setattr(settings, 'speech_enabled', False)
    reserve = Mock(side_effect=AssertionError('no usage'))
    monkeypatch.setattr(dependencies, 'reserve_staging_request', reserve)
    for method in ['get', 'post']:
        assert getattr(sqlite_client, method)('/speech/token', headers=headers).status_code == 503
    reserve.assert_not_called()


def test_endpoint_failure_keeps_reservation_and_end_does_not_need_ai(sqlite_client, monkeypatch):
    from fastapi import HTTPException
    headers = invited(sqlite_client, monkeypatch)
    reserve = Mock()
    monkeypatch.setattr(dependencies, 'reserve_staging_request', reserve)
    start = AsyncMock(side_effect=HTTPException(404, 'Not found'))
    end = AsyncMock(side_effect=HTTPException(404, 'Not found'))
    monkeypatch.setattr(router.service, 'start_interview', start)
    monkeypatch.setattr(router.service, 'end_interview', end)
    assert sqlite_client.post('/interview/start', json={'analysis_id': 1}, headers=headers).status_code == 404
    reserve.assert_called_once()
    monkeypatch.setattr(settings, 'ai_enabled', False)
    assert sqlite_client.post('/interview/test/end', headers=headers).status_code == 404
    end.assert_awaited_once()
    assert reserve.call_count == 1
