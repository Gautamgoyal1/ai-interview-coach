"""Executable expected rows for reviewed kernels, in isolated PostgreSQL only.

This verifies concrete alternative query shapes, not candidate answers or grades.
The operator restores a disposable DB and sets PREPMATE_KNOWLEDGE_POSTGRES.
"""
import os

import pytest
from sqlalchemy import create_engine, text

from app.core.config import settings


@pytest.fixture
def sql_connection():
    if os.getenv("PREPMATE_KNOWLEDGE_POSTGRES") != "1":
        pytest.skip("Requires the isolated PostgreSQL regression operator")
    engine = create_engine(settings.database_url)
    with engine.connect() as c:
        transaction = c.begin()
        try:
            yield c
        finally:
            transaction.rollback()
    engine.dispose()


def test_independent_counts_do_not_multiply_or_drop_zero_users(sql_connection):
    c=sql_connection
    for statement in [
        "CREATE TEMP TABLE users(id integer PRIMARY KEY) ON COMMIT DROP",
        "CREATE TEMP TABLE posts(id integer PRIMARY KEY,user_id integer) ON COMMIT DROP",
        "CREATE TEMP TABLE likes(id integer PRIMARY KEY,user_id integer) ON COMMIT DROP",
        "INSERT INTO users VALUES (1),(2),(3)",
        "INSERT INTO posts VALUES (1,1),(2,1),(3,2)",
        "INSERT INTO likes VALUES (1,1),(2,1),(3,1)",
    ]:c.execute(text(statement))
    rows=c.execute(text("""SELECT u.id,
        COALESCE(p.n,0),COALESCE(l.n,0) FROM users u
        LEFT JOIN (SELECT user_id,COUNT(*) n FROM posts GROUP BY user_id) p ON p.user_id=u.id
        LEFT JOIN (SELECT user_id,COUNT(*) n FROM likes GROUP BY user_id) l ON l.user_id=u.id
        ORDER BY u.id""")).all()
    assert [tuple(r) for r in rows]==[(1,2,3),(2,1,0),(3,0,0)]


def test_latest_eligibility_has_observable_tie_and_preserves_only_ineligible_parents(sql_connection):
    c=sql_connection
    for statement in [
        "CREATE TEMP TABLE users(id integer PRIMARY KEY) ON COMMIT DROP",
        "CREATE TEMP TABLE edits(id integer PRIMARY KEY,user_id integer,at integer,approved boolean) ON COMMIT DROP",
        "INSERT INTO users VALUES (1),(2),(3)",
        "INSERT INTO edits VALUES (1,1,10,true),(2,1,10,true),(3,1,NULL,true),(4,2,30,false),(5,2,40,NULL)",
    ]:c.execute(text(statement))
    rows=c.execute(text("""WITH ranked AS (
        SELECT id,user_id,ROW_NUMBER() OVER(PARTITION BY user_id ORDER BY at DESC,id DESC) n
        FROM edits WHERE approved=true AND at IS NOT NULL)
        SELECT u.id,r.id FROM users u LEFT JOIN ranked r ON r.user_id=u.id AND r.n=1 ORDER BY u.id""")).all()
    assert [tuple(r) for r in rows]==[(1,2),(2,None),(3,None)]


def test_snapshot_selection_does_not_reduce_aggregate_or_admit_boundary_rows(sql_connection):
    c=sql_connection
    for statement in [
        "CREATE TEMP TABLE accounts(id integer PRIMARY KEY) ON COMMIT DROP",
        "CREATE TEMP TABLE events(id integer PRIMARY KEY,account_id integer,at timestamptz,eligible boolean,amount integer) ON COMMIT DROP",
        "INSERT INTO accounts VALUES (1),(2),(3),(4)",
        """INSERT INTO events VALUES
        (1,1,'2026-01-01T00:00:00Z',true,3),(2,1,'2026-01-10T00:00:00Z',true,7),
        (3,1,'2026-01-10T00:00:00Z',true,NULL),(4,1,'2026-02-01T00:00:00Z',true,100),
        (5,2,'2026-01-10T00:00:00Z',false,100),(6,2,'2026-01-10T00:00:00Z',NULL,100),
        (7,3,'2026-01-10T00:00:00Z',true,NULL),(8,3,NULL,true,100)""",
    ]:c.execute(text(statement))
    rows=c.execute(text("""WITH scoped AS (
        SELECT * FROM events WHERE eligible=true AND at>='2026-01-01T00:00:00Z' AND at<'2026-02-01T00:00:00Z'),
        ranked AS (SELECT *,ROW_NUMBER() OVER(PARTITION BY account_id ORDER BY at DESC,id DESC) n FROM scoped),
        totals AS (SELECT account_id,COUNT(*) n,COALESCE(SUM(amount),0) total FROM scoped GROUP BY account_id)
        SELECT a.id,r.id,COALESCE(t.n,0),COALESCE(t.total,0) FROM accounts a
        LEFT JOIN ranked r ON r.account_id=a.id AND r.n=1
        LEFT JOIN totals t ON t.account_id=a.id ORDER BY a.id""")).all()
    assert [tuple(r) for r in rows]==[(1,3,3,10),(2,None,0,0),(3,7,1,0),(4,None,0,0)]
