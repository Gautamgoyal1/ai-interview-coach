
from sqlalchemy import select
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


def _query_chunks_by_embedding(
    db: Session,
    query_embedding: list[float],
    top_k: int,
    topic: str | None = None,
    role: str | None = None,
) -> list[Chunk]:
    stmt = select(Chunk)

    if topic:
        stmt = stmt.where(Chunk.topic == topic)

    if role:
        stmt = stmt.where(Chunk.role == role)

    stmt = (
        stmt
        .order_by(Chunk.embedding.cosine_distance(query_embedding))
        .limit(top_k)
    )

    return list(db.scalars(stmt).all())


async def retrieve_chunks_async(
    db: Session,
    query: str,
    top_k: int = 5,
    topic: str | None = None,
    role: str | None = None,
) -> list[Chunk]:
    """Asynchronously retrieve the top-k chunks most similar to a query."""
    cleaned_query = _validate_retrieval_params(query, top_k)
    query_embedding = await _embed_query(cleaned_query)
    return _query_chunks_by_embedding(
        db=db,
        query_embedding=query_embedding,
        top_k=top_k,
        topic=topic,
        role=role,
    )


def retrieve_chunks(
    db: Session,
    query: str,
    top_k: int = 5,
    topic: str | None = None,
    role: str | None = None,
) -> list[Chunk]:
    """Retrieve the top-k chunks most similar to a question."""
    cleaned_query = _validate_retrieval_params(query, top_k)

    # Run the async embedding function from this synchronous function.
    import asyncio

    query_embedding = asyncio.run(_embed_query(cleaned_query))
    return _query_chunks_by_embedding(
        db=db,
        query_embedding=query_embedding,
        top_k=top_k,
        topic=topic,
        role=role,
    )
