from fastapi import FastAPI
from sqlalchemy import text
from backend.app.services.qdrant_service import ensure_collection, get_collection_info
from backend.app.db.database import engine

app = FastAPI(
    title="AI-Powered Digital Asset Management",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "ai-dam-api",
    }


@app.get("/health/database")
def database_health_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
        "status": "ok",
        "database": "postgresql",
    }

@app.get("/health/qdrant")
def qdrant_health_check():
    ensure_collection()
    info = get_collection_info()

    return {
        "status": "ok",
        "collection": "asset_embeddings",
        "vectors_count": info.points_count,
        "vector_size": 768,
    }