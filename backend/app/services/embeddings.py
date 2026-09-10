"""
Vector embedding generation for learning content RAG pipeline.
Produces 384-dimensional normalized vector embeddings.
"""

import hashlib
import math
import re
from typing import Optional

_transformer_model = None
_model_attempted = False
MODEL_NAME = "all-MiniLM-L6-v2"


def _get_transformer_model():
    global _transformer_model, _model_attempted
    if _transformer_model is not None:
        return _transformer_model
    if _model_attempted:
        return None

    _model_attempted = True
    try:
        from sentence_transformers import SentenceTransformer
        _transformer_model = SentenceTransformer(MODEL_NAME)
        return _transformer_model
    except Exception as exc:
        print(f"[Embeddings] SentenceTransformer unavailable ({exc}). Using resilient fallback vectorizer.")
        return None


def _fallback_embedding(text: str, dim: int = 384) -> list[float]:
    """
    Deterministic normalized 384-dimensional embedding fallback.
    Uses token n-grams and hashing with L2 normalization to ensure
    consistent cosine similarity and prevent offline demo failure.
    """
    vector = [0.0] * dim
    tokens = re.findall(r"\b\w+\b", text.lower())
    if not tokens:
        tokens = ["empty"]

    for i, token in enumerate(tokens):
        # 1-gram
        h1 = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16) % dim
        vector[h1] += 1.0
        # 2-gram
        if i + 1 < len(tokens):
            bigram = f"{token}_{tokens[i+1]}"
            h2 = int(hashlib.sha256(bigram.encode("utf-8")).hexdigest(), 16) % dim
            vector[h2] += 1.5

    # L2 normalize
    norm = math.sqrt(sum(x * x for x in vector))
    if norm > 0:
        vector = [round(x / norm, 6) for x in vector]
    else:
        vector[0] = 1.0
    return vector


def generate_embedding(text: str) -> list[float]:
    """
    Generate a 384-dimensional normalized embedding.
    Uses SentenceTransformer if available, or falls back to
    deterministic semantic hashing to guarantee 100% demo reliability.
    """
    if not text or not text.strip():
        raise ValueError("Cannot generate embedding for empty text.")

    model = _get_transformer_model()
    if model is not None:
        try:
            embedding = model.encode(text, normalize_embeddings=True)
            return embedding.tolist()
        except Exception as exc:
            print(f"[Embeddings] Encoding failed ({exc}), falling back.")

    return _fallback_embedding(text, dim=384)