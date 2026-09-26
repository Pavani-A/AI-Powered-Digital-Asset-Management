from __future__ import annotations

from typing import Any

from qdrant_client.models import (
    FieldCondition,
    Filter,
    MatchValue,
)
from sqlalchemy import text

from backend.app.db.database import SessionLocal
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
    Perform semantic search and enrich the results with PostgreSQL metadata.
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

    points = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        query_filter=query_filter,
        with_payload=True,
        limit=limit,
    ).points

    if not points:
        return []

    asset_ids = [
        point.payload.get("asset_id")
        for point in points
        if point.payload and point.payload.get("asset_id")
    ]

    db = SessionLocal()

    try:
        assets_by_id: dict[str, dict[str, Any]] = {}

        for asset_id in asset_ids:
            asset = db.execute(
                text(
                    """
                    SELECT
                        id,
                        filename,
                        original_path,
                        file_type,
                        mime_type,
                        size_bytes,
                        width,
                        height,
                        duration_seconds,
                        frame_rate,
                        page_count,
                        description,
                        status
                    FROM assets
                    WHERE id = :asset_id
                    """
                ),
                {"asset_id": asset_id},
            ).mappings().first()

            if asset:
                assets_by_id[str(asset["id"])] = dict(asset)

    finally:
        db.close()

    results: list[dict[str, Any]] = []

    for point in points:
        payload = point.payload or {}
        asset_id = payload.get("asset_id")

        if not asset_id:
            continue

        asset = assets_by_id.get(str(asset_id))

        if not asset:
            continue

        results.append(
            {
                "asset_id": str(asset["id"]),
                "filename": asset["filename"],
                "file_type": asset["file_type"],
                "mime_type": asset["mime_type"],
                "size_bytes": asset["size_bytes"],
                "width": asset["width"],
                "height": asset["height"],
                "duration_seconds": asset["duration_seconds"],
                "frame_rate": asset["frame_rate"],
                "page_count": asset["page_count"],
                "description": asset["description"],
                "status": asset["status"],
                "original_path": asset["original_path"],
                "score": point.score,
            }
        )

    return results