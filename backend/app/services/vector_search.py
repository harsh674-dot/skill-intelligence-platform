from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.content_chunk import ContentChunk
from app.services.embeddings import generate_embedding


def search_content(
    db: Session,
    query: str,
    limit: int = 5,
):
    """
    Search uploaded learning content using
    cosine similarity between query and chunk embeddings.
    """

    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    query_embedding = generate_embedding(query)

    similarity = (
        1 - ContentChunk.embedding.cosine_distance(query_embedding)
    ).label("similarity")

    statement = (
        select(
            ContentChunk.id,
            ContentChunk.learning_content_id,
            ContentChunk.chunk_index,
            ContentChunk.chunk_text,
            similarity,
        )
        .where(ContentChunk.embedding.is_not(None))
        .order_by(similarity.desc())
        .limit(limit)
    )

    results = db.execute(statement).all()

    return results