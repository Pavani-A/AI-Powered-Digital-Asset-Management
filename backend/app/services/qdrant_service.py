from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from backend.app.db.database import settings


COLLECTION_NAME = "asset_embeddings"
VECTOR_SIZE = 768


client = QdrantClient(url=settings.qdrant_url)


def ensure_collection() -> None:
    """Create the asset embedding collection if it does not already exist."""
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
    return client.get_collection(COLLECTION_NAME)