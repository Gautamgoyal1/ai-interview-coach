"""Real pgvector storage tests in a disposable, guarded schema."""

import os
import re
import uuid

import pytest
from sqlalchemy import Column, Integer, MetaData, Table, create_engine, select, text
from pgvector.sqlalchemy import Vector

from app.core.config import settings
from app.modules.knowledge.verification import verify_stored_vector

pytestmark = pytest.mark.skipif(
    os.getenv("PREPMATE_VECTOR_POSTGRES") != "1", reason="isolated PostgreSQL opt-in"
)


@pytest.fixture
def stored_vector():
    schema = "test_vector_" + uuid.uuid4().hex
    engine = create_engine(settings.database_url)
    table = Table(
        "vectors",
        MetaData(),
        Column("id", Integer, primary_key=True),
        Column("embedding", Vector(768)),
        schema=schema,
    )
    try:
        with engine.begin() as conn:
            conn.execute(text(f'CREATE SCHEMA "{schema}"'))
            table.create(conn)
            expected = [0.123456789, -0.234567891] + [0.00123456789] * 766
            conn.execute(table.insert().values(id=1, embedding=expected))
        # New connection: test persisted values rather than ORM identity-map data.
        with engine.connect() as conn:
            actual = conn.scalar(select(table.c.embedding).where(table.c.id == 1))
        yield engine, table, actual, expected
    finally:
        assert re.fullmatch(r"test_vector_[0-9a-f]{32}", schema)
        with engine.begin() as conn:
            conn.execute(text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))
        engine.dispose()


def test_persisted_fractional_vector_roundtrip(stored_vector):
    _, _, actual, expected = stored_vector
    verify_stored_vector(actual, expected)


def test_corrupted_persisted_component_is_rejected(stored_vector):
    engine, table, _, expected = stored_vector
    changed = expected.copy()
    changed[0] = -changed[0]
    with engine.begin() as conn:
        conn.execute(table.update().where(table.c.id == 1).values(embedding=changed))
    with engine.connect() as conn:
        actual = conn.scalar(select(table.c.embedding).where(table.c.id == 1))
    with pytest.raises(ValueError, match="differs"):
        verify_stored_vector(actual, expected)
