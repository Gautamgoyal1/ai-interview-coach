"""Supabase-like roles on a disposable migrated PostgreSQL database, never cloud."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import os
import uuid

from alembic import command
from alembic.config import Config
import pytest
from sqlalchemy import create_engine, text, select
from sqlalchemy.engine import make_url
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core import staging_budget
from app.db.models.staging_usage import StagingAIUsage

pytestmark = pytest.mark.skipif(os.getenv('PREPMATE_STAGING_POSTGRES') != '1', reason='disposable PostgreSQL only')
ROOT = Path(__file__).resolve().parents[2]
TABLES = ['users','resumes','resume_analyses','interview_sessions','interview_turns','interview_reports',
          'practice_sessions','practice_questions','practice_attempts','chunks','alembic_version','staging_ai_usage']


@pytest.fixture
def staging_pg(monkeypatch):
    url = make_url(settings.database_url)
    assert (url.host or '').startswith('prepmate-test-'), 'Refusing non-disposable database host'
    name = 'staging_test_' + uuid.uuid4().hex
    admin = create_engine(url, isolation_level='AUTOCOMMIT')
    with admin.connect() as db:
        db.execute(text(f'CREATE DATABASE "{name}"'))
        for role in ['anon', 'authenticated', 'service_role']:
            if not db.scalar(text('SELECT 1 FROM pg_roles WHERE rolname=:role'), {'role':role}):
                db.execute(text(f'CREATE ROLE {role} NOLOGIN'))
    target = create_engine(url.set(database=name))
    try:
        with monkeypatch.context() as patch:
            patch.setattr(settings, 'database_url', url.set(database=name).render_as_string(hide_password=False))
            command.upgrade(Config(str(ROOT / 'alembic.ini')), 'head')
        yield target
    finally:
        target.dispose()
        with admin.connect() as db:
            db.execute(text(f'DROP DATABASE "{name}" WITH (FORCE)'))
        admin.dispose()


def harden(engine):
    with engine.connect() as db:
        db.exec_driver_sql("SET prepmate.reviewed_dedicated_project = 'yes'")
        db.commit()
        db.execution_options(no_parameters=True).exec_driver_sql((ROOT / 'scripts/sql/restrict_supabase.sql').read_text())
        db.commit()


def test_supabase_roles_denied_and_runtime_can_persist(staging_pg):
    # Model the permissive default grants and even a column-level grant.
    with staging_pg.begin() as db:
        db.execute(text('GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated, service_role'))
        db.execute(text('GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated, service_role'))
        db.execute(text('GRANT SELECT(email) ON users TO anon'))
        db.execute(text('ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO anon'))
    harden(staging_pg)
    harden(staging_pg)  # Idempotence, including existing policy inspection.
    for role in ['anon', 'authenticated', 'service_role']:
        for table in TABLES:
            with staging_pg.connect() as db:
                db.execute(text(f'SET LOCAL ROLE {role}'))
                with pytest.raises(DBAPIError):
                    db.execute(text(f'SELECT * FROM public.{table} LIMIT 1'))
    with staging_pg.begin() as db:
        db.execute(text('SET LOCAL ROLE prepmate_runtime'))
        uid = db.scalar(text("INSERT INTO users(email,password_hash) VALUES ('synthetic@example.com','not-a-real-password') RETURNING id"))
        assert db.scalar(text('SELECT email FROM users WHERE id=:id'), {'id':uid}) == 'synthetic@example.com'
        db.execute(text("INSERT INTO staging_ai_usage VALUES (CURRENT_DATE, 'global', 1)"))
        db.execute(text("UPDATE staging_ai_usage SET requests=2 WHERE bucket='global'"))
        assert db.scalar(text("SELECT requests FROM staging_ai_usage WHERE bucket='global'")) == 2
        assert db.scalar(text('SELECT count(*) FROM chunks')) == 0
        assert db.scalar(text('SELECT version_num FROM alembic_version')) == 'b8c9d0e1f2a3'
        from scripts.staging_preflight import check_security
        assert check_security(db) == []
    for sql in ["UPDATE chunks SET role='sql_injection'", 'DELETE FROM staging_ai_usage', "UPDATE alembic_version SET version_num='bad'", 'CREATE TABLE public.unauthorized(id int)']:
        with staging_pg.connect() as db:
            db.execute(text('SET LOCAL ROLE prepmate_runtime'))
            with pytest.raises(DBAPIError):
                db.execute(text(sql))
    with staging_pg.begin() as db:
        db.execute(text('CREATE TABLE public.future_test(id integer)'))
        assert not db.scalar(text("SELECT has_table_privilege('anon','public.future_test','SELECT')"))


def test_hardening_requires_ack_and_rejects_unknown_policies_atomically(staging_pg):
    sql = (ROOT / 'scripts/sql/restrict_supabase.sql').read_text()
    with staging_pg.connect() as db:
        with pytest.raises(DBAPIError, match='acknowledgement'):
            db.execution_options(no_parameters=True).exec_driver_sql(sql)
    with staging_pg.begin() as db:
        db.execute(text('CREATE POLICY unexpected ON users TO anon USING (true)'))
        db.execute(text('GRANT SELECT ON users TO anon'))
    with pytest.raises(DBAPIError, match='Unreviewed RLS policy'):
        harden(staging_pg)
    with staging_pg.connect() as db:
        assert db.scalar(text("SELECT has_table_privilege('anon','users','SELECT')"))


def test_postgres_atomic_concurrent_quota_and_restart_recovery(staging_pg, monkeypatch):
    monkeypatch.setattr(staging_budget, 'SessionLocal', sessionmaker(staging_pg))
    monkeypatch.setattr(settings, 'staging_ai_global_daily_limit', 3)
    monkeypatch.setattr(settings, 'staging_ai_user_daily_limit', 2)
    from fastapi import HTTPException
    def reserve(_):
        try:
            staging_budget.reserve_staging_request(1)
            return 200
        except HTTPException as error:
            return error.status_code
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(reserve, range(6)))
    assert sorted(results) == [200,200,429,429,429,429]
    staging_pg.dispose()  # New SQL connections/process-local state cannot refund.
    staging_budget.reserve_staging_request(2)
    with pytest.raises(HTTPException) as error:
        staging_budget.reserve_staging_request(3)
    assert error.value.status_code == 429
    with sessionmaker(staging_pg)() as db:
        assert db.scalar(select(StagingAIUsage.requests).where(StagingAIUsage.bucket=='global')) == 3


def test_scoped_initialization_preview_apply_idempotence_and_runtime_retrieval(staging_pg):
    from tests.unit.test_staging_knowledge import inputs
    from scripts.export_staging_knowledge import reviewed_bundle
    from scripts.initialize_staging_knowledge import initialize, validate_bundle
    from scripts.staging_preflight import check_knowledge
    from app.db.models.chunk import Chunk
    from app.modules.knowledge.retriever import _query_chunks_by_embedding
    manifest,source,cache = inputs()
    rows = validate_bundle(reviewed_bundle(manifest,source,cache),manifest)
    from sqlalchemy.orm import Session
    with Session(staging_pg) as db, db.begin():
        db.execute(text('SET TRANSACTION READ ONLY'))
        assert initialize(db,rows,manifest)['inserts'] == 30
        assert db.scalar(select(text('count(*)')).select_from(Chunk)) == 0
    with Session(staging_pg) as db, db.begin():
        assert initialize(db,rows,manifest,apply=True)['inserts'] == 30
    with Session(staging_pg) as db, db.begin():
        assert initialize(db,rows,manifest,apply=True)['inserts'] == 0
    harden(staging_pg)
    with Session(staging_pg) as db:
        db.execute(text('SET LOCAL ROLE prepmate_runtime'))
        assert check_knowledge(db,manifest) == []
        for difficulty in ['easy','medium','hard']:
            results = _query_chunks_by_embedding(db,[1.0]*768,3,role='software_engineer',difficulty=difficulty)
            assert len(results) == 3
            assert all(row.role=='software_engineer' and row.difficulty==difficulty for row in results)


def test_initializer_rolls_back_bad_storage_and_refuses_unreviewed_rows(staging_pg):
    from tests.unit.test_staging_knowledge import inputs
    from scripts.export_staging_knowledge import reviewed_bundle
    from scripts.initialize_staging_knowledge import initialize
    from app.db.models.chunk import Chunk
    from sqlalchemy.orm import Session
    manifest,source,cache = inputs()
    rows = reviewed_bundle(manifest,source,cache)['rows']
    rows[0]['embedding'][0] = 1.5
    with pytest.raises(ValueError, match='verification failed'):
        with Session(staging_pg) as db, db.begin():
            initialize(db,rows,manifest,apply=True)
    with Session(staging_pg) as db, db.begin():
        assert db.scalar(select(text('count(*)')).select_from(Chunk)) == 0
        db.add(Chunk(**rows[0]))
    with pytest.raises(ValueError, match='nonempty/unreviewed'):
        with Session(staging_pg) as db, db.begin():
            initialize(db,rows,manifest,apply=True)
    with Session(staging_pg) as db:
        assert db.scalar(select(text('count(*)')).select_from(Chunk)) == 1
