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


def public_access(monkeypatch):
    monkeypatch.setattr(settings, 'staging_enabled', True)
    monkeypatch.setattr(settings, 'staging_access_mode', 'public')
    monkeypatch.setattr(settings, 'staging_allowed_emails', [])
    monkeypatch.setattr(settings, 'staging_registration_enabled', True)


def test_public_users_register_login_and_keep_distinct_authenticated_identities(sqlite_client, monkeypatch):
    public_access(monkeypatch)
    ids = []
    for email in ['new-candidate@example.com','another-candidate@example.org']:
        created = sqlite_client.post('/auth/register', json={'email':email,'password':'synthetic-test-password'})
        assert created.status_code == 201
        login = sqlite_client.post('/auth/login', json={'email':email,'password':'synthetic-test-password'})
        assert login.status_code == 200
        me = sqlite_client.get('/auth/me', headers={'Authorization':'Bearer '+login.json()['access_token']})
        assert me.status_code == 200 and me.json()['id'] == created.json()['id']
        ids.append(me.json()['id'])
    assert ids[0] != ids[1]
    assert sqlite_client.get('/auth/me').status_code == 401


def test_public_registration_remains_rate_limited(sqlite_client, monkeypatch):
    public_access(monkeypatch)
    for number in range(5):
        assert sqlite_client.post('/auth/register', json={'email':f'new{number}@example.com','password':'synthetic-test-password'}).status_code == 201
    assert sqlite_client.post('/auth/register', json={'email':'extra@example.com','password':'synthetic-test-password'}).status_code == 429


def test_public_ai_request_still_reserves_persistent_quota_before_provider(sqlite_client, monkeypatch):
    from fastapi import HTTPException
    public_access(monkeypatch)
    user = sqlite_client.post('/auth/register', json={'email':'new@example.com','password':'synthetic-test-password'}).json()
    headers = {'Authorization':'Bearer '+create_access_token(str(user['id']))}
    reserve = Mock(side_effect=HTTPException(429,'Daily quota reached'))
    provider = AsyncMock()
    monkeypatch.setattr(settings, 'ai_enabled', True)
    monkeypatch.setattr(dependencies, 'reserve_staging_request', reserve)
    monkeypatch.setattr(router.service, 'start_interview', provider)
    response = sqlite_client.post('/interview/start', json={'analysis_id':1}, headers=headers)
    assert response.status_code == 429
    reserve.assert_called_once_with(user['id'])
    provider.assert_not_awaited()


@pytest.mark.parametrize('path', ['/speech/token','/interview/start'])
def test_public_access_preserves_anonymous_ai_rejection(sqlite_client, monkeypatch, path):
    public_access(monkeypatch)
    reserve = Mock()
    monkeypatch.setattr(dependencies, 'reserve_staging_request', reserve)
    assert sqlite_client.post(path, json={'analysis_id':1}).status_code == 401
    reserve.assert_not_called()


def test_public_registration_can_be_closed_without_blocking_existing_login(sqlite_client, monkeypatch):
    public_access(monkeypatch)
    request = {'email':'existing@example.com','password':'synthetic-test-password'}
    assert sqlite_client.post('/auth/register', json=request).status_code == 201
    monkeypatch.setattr(settings, 'staging_registration_enabled', False)
    assert sqlite_client.post('/auth/register', json={'email':'new@example.com','password':'synthetic-test-password'}).status_code == 403
    assert sqlite_client.post('/auth/login', json=request).status_code == 200
