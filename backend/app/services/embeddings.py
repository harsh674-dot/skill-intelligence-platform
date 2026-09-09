from sentence_transformers import SentenceTransformer


# Free, local embedding model.
# Produces 384-dimensional embeddings.
MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)


def generate_embedding(text: str) -> list[float]:
    """
    Generate a 384-dimensional embedding locally.
    No API key or internet request is required after
    the model has been downloaded.
    """

    if not text or not text.strip():
        raise ValueError("Cannot generate embedding for empty text.")

    embedding = model.encode(
        text,
        normalize_embeddings=True,
    )

    return embedding.tolist()