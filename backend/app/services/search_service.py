from __future__ import annotations

from typing import Any

from qdrant_client.models import (
    FieldCondition,
    Filter,
    MatchValue,
)

from backend.app.services.embedding_service import generate_embedding
from backend.app.services.qdrant_service import (
    COLLECTION_NAME,
    client,
)


def search_assets(
    query: str,
    *,
    limit: int = 10,
    file_type: str | None = None,
) -> list[dict[str, Any]]:
    """
    Perform semantic search over indexed assets.

    The user query is embedded using the same embedding model
    used during indexing, then searched against Qdrant.
    """
    query = query.strip()

    if not query:
        raise ValueError("Search query cannot be empty.")

    if limit < 1 or limit > 100:
        raise ValueError("limit must be between 1 and 100.")

    query_vector = generate_embedding(query)

    query_filter = None

    if file_type:
        query_filter = Filter(
            must=[
                FieldCondition(
                    key="file_type",
                    match=MatchValue(value=file_type),
                )
            ]
        )

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        query_filter=query_filter,
        with_payload=True,
        limit=limit,
    ).points

    return [
        {
            "asset_id": point.payload.get("asset_id"),
            "filename": point.payload.get("filename"),
            "file_type": point.payload.get("file_type"),
            "score": point.score,
        }
        for point in results
    ]