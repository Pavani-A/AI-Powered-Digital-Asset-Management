from fastapi import FastAPI
from sqlalchemy import text
from backend.app.services.qdrant_service import ensure_collection, get_collection_info
from backend.app.db.database import engine
from backend.app.services.scanner_service import scan_library
from uuid import UUID
from fastapi import HTTPException
from backend.app.services.ollama_service import generate_image_description
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
@app.post("/index/scan")
def scan_assets():
    return scan_library("data")

@app.post("/assets/{asset_id}/analyze")
def analyze_asset(asset_id: UUID):
    with engine.begin() as connection:
        asset = connection.execute(
            text(
                """
                SELECT
                    id,
                    original_path,
                    file_type
                FROM assets
                WHERE id = :asset_id
                """
            ),
            {"asset_id": asset_id},
        ).mappings().first()

    if not asset:
        raise HTTPException(
            status_code=404,
            detail="Asset not found",
        )

    if asset["file_type"] != "image":
        raise HTTPException(
            status_code=400,
            detail="This endpoint currently supports images only.",
        )

    try:
        description = generate_image_description(
            asset["original_path"]
        )

        with engine.begin() as connection:
            connection.execute(
                text(
                    """
                    UPDATE assets
                    SET
                        description = :description,
                        status = 'ai_processed',
                        error_message = NULL,
                        updated_at = NOW()
                    WHERE id = :asset_id
                    """
                ),
                {
                    "asset_id": asset_id,
                    "description": description,
                },
            )

        return {
            "status": "ok",
            "asset_id": str(asset_id),
            "description": description,
        }

    except Exception as exc:
        with engine.begin() as connection:
            connection.execute(
                text(
                    """
                    UPDATE assets
                    SET
                        status = 'failed',
                        error_message = :error_message,
                        updated_at = NOW()
                    WHERE id = :asset_id
                    """
                ),
                {
                    "asset_id": asset_id,
                    "error_message": str(exc),
                },
            )

        raise HTTPException(
            status_code=500,
            detail=f"AI analysis failed: {exc}",
        )