from app.modules.interview.difficulty_contract import context_difficulty
from sqlalchemy import select
from sqlalchemy import or_
from app.modules.resume.catalog import resolve_role
from app.modules.resume.scoring import extract_skills
from sqlalchemy.orm import Session

from app.db.models.chunk import Chunk
from app.modules.knowledge.embeddings import embed_texts


async def _embed_query(query: str) -> list[float]:
    embeddings = await embed_texts(
        [query],
        task_type="RETRIEVAL_QUERY",
    )
    return embeddings[0]


def _validate_retrieval_params(query: str, top_k: int) -> str:
    query = query.strip()

    if not query:
        raise ValueError("Query cannot be empty")
    if top_k < 1:
        raise ValueError("top_k must be at least 1")

    return query


def _eligible_statement(topic=None, role=None, difficulty=None, experience_level=None):
    stmt = select(Chunk).where(Chunk.role != "retired")

    if topic:
        topics = retrieval_topics(topic)
        stmt = stmt.where(or_(Chunk.topic.in_(topics), Chunk.subtopic.in_(topics)))
    if role:
        profile = resolve_role(role)
        if profile is None:
            return None
        stmt = stmt.where(
            Chunk.role.in_(profile.get("knowledge_roles", [profile["id"]]))
        )
    if difficulty:
        if difficulty not in {"easy", "medium", "hard"}:
            raise ValueError("Unknown retrieval difficulty")
        stmt = stmt.where(Chunk.difficulty == context_difficulty(difficulty, experience_level))

    return stmt


def _query_chunks_by_embedding(
    db: Session,
    query_embedding: list[float],
    top_k: int,
    topic: str | None = None,
    role: str | None = None,
    difficulty: str | None = None,
    experience_level: str | None = None,
) -> list[Chunk]:
    stmt = _eligible_statement(topic, role, difficulty, experience_level)
    if stmt is None:
        return []
    stmt = stmt.order_by(Chunk.embedding.cosine_distance(query_embedding)).limit(top_k)
    return list(db.scalars(stmt).all())


async def retrieve_chunks_async(
    db: Session,
    query: str,
    top_k: int = 5,
    topic: str | None = None,
    role: str | None = None,
    difficulty: str | None = None,
    experience_level: str | None = None,
) -> list[Chunk]:
    """Asynchronously retrieve the top-k chunks most similar to a query."""
    cleaned_query = _validate_retrieval_params(query, top_k)
    if role and resolve_role(role) is None:
        return []
    eligible = _eligible_statement(topic, role, difficulty, experience_level)
    if (
        eligible is None
        or db.scalar(eligible.with_only_columns(Chunk.id).limit(1)) is None
    ):
        return []
    query_embedding = await _embed_query(cleaned_query)
    return _query_chunks_by_embedding(
        db=db,
        query_embedding=query_embedding,
        top_k=top_k,
        topic=topic,
        role=role,
        difficulty=difficulty,
        experience_level=experience_level,
    )


def retrieve_chunks(
    db: Session,
    query: str,
    top_k: int = 5,
    topic: str | None = None,
    role: str | None = None,
    difficulty: str | None = None,
    experience_level: str | None = None,
) -> list[Chunk]:
    """Retrieve the top-k chunks most similar to a question."""
    cleaned_query = _validate_retrieval_params(query, top_k)

    # Run the async embedding function from this synchronous function.
    import asyncio

    if role and resolve_role(role) is None:
        return []
    eligible = _eligible_statement(topic, role, difficulty, experience_level)
    if (
        eligible is None
        or db.scalar(eligible.with_only_columns(Chunk.id).limit(1)) is None
    ):
        return []
    query_embedding = asyncio.run(_embed_query(cleaned_query))
    return _query_chunks_by_embedding(
        db=db,
        query_embedding=query_embedding,
        top_k=top_k,
        topic=topic,
        role=role,
        difficulty=difficulty,
        experience_level=experience_level,
    )


def retrieval_topics(value: str) -> list[str]:
    """Map display topics to knowledge identifiers, independently of resume aliases."""
    cleaned = value.strip().lower().replace("&", "and")
    display = {
        "arrays and linked lists": "data_structures",
        "stacks and queues": "data_structures",
        "hash maps": "data_structures",
        "time complexity": "algorithms",
        "sql vs nosql": "sql",
        "sql joins and indexing": "sql",
        "database indexing": "sql",
        "authentication and authorization": "security_fundamentals",
        "testing and debugging": "testing",
        "model evaluation metrics": "machine_learning",
        "classification metrics": "machine_learning",
        "cross-validation": "machine_learning",
    }
    topics = {
        cleaned.replace(" ", "_").replace("-", "_").replace("/", "_"),
        display.get(cleaned, ""),
    }
    for skill in extract_skills(value):
        topics.add(skill.replace(" ", "_").replace("-", "_").replace("/", "_"))
        if skill in {"machine learning", "model evaluation", "data preprocessing"}:
            topics.add("machine_learning")
    return sorted(topics - {""})
