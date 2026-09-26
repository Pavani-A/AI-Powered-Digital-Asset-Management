from __future__ import annotations

import json
from urllib import request

from backend.app.db.database import settings


OLLAMA_EMBED_URL = f"{settings.ollama_base_url}/api/embed"
EMBEDDING_MODEL = "embeddinggemma:latest"
EXPECTED_DIMENSION = 768


def generate_embedding(text: str) -> list[float]:
    """
    Generate a semantic embedding for the supplied text.
    """
    text = text.strip()

    if not text:
        raise ValueError("Cannot generate an embedding for empty text.")

    payload = {
        "model": EMBEDDING_MODEL,
        "input": text,
    }

    body = json.dumps(payload).encode("utf-8")

    http_request = request.Request(
        OLLAMA_EMBED_URL,
        data=body,
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with request.urlopen(
        http_request,
        timeout=settings.ai_request_timeout_seconds,
    ) as response:
        result = json.loads(
            response.read().decode("utf-8")
        )

    embeddings = result.get("embeddings")

    if not embeddings:
        raise RuntimeError("Ollama returned no embeddings.")

    vector = embeddings[0]

    if len(vector) != EXPECTED_DIMENSION:
        raise RuntimeError(
            f"Unexpected embedding dimension: "
            f"{len(vector)}. Expected {EXPECTED_DIMENSION}."
        )

    return vector