from __future__ import annotations

from uuid import UUID

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from backend.app.db.database import settings


COLLECTION_NAME = "asset_embeddings"
VECTOR_SIZE = 768

client = QdrantClient(url=settings.qdrant_url)


def ensure_collection() -> None:
    """Create the asset embedding collection if it does not exist."""
    if client.collection_exists(COLLECTION_NAME):
        return

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=VECTOR_SIZE,
            distance=Distance.COSINE,
        ),
    )


def get_collection_info():
    """Return basic information about the asset embedding collection."""
    ensure_collection()
    return client.get_collection(COLLECTION_NAME)


def upsert_asset_embedding(
    asset_id: UUID,
    vector: list[float],
    *,
    filename: str,
    file_type: str,
) -> None:
    """
    Store or replace the embedding for an asset.

    The asset UUID is used as the Qdrant point ID so re-indexing
    the same asset does not create another vector.
    """
    if len(vector) != VECTOR_SIZE:
        raise ValueError(
            f"Invalid vector dimension: {len(vector)}. "
            f"Expected {VECTOR_SIZE}."
        )

    ensure_collection()

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=str(asset_id),
                vector=vector,
                payload={
                    "asset_id": str(asset_id),
                    "filename": filename,
                    "file_type": file_type,
                },
            )
        ],
        wait=True,
    )