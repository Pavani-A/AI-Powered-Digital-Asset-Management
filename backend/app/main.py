from uuid import UUID

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware
from backend.app.db.database import engine
from backend.app.services.indexing_service import (
    create_indexing_job,
    index_asset,
)
from backend.app.services.media_service import get_asset_file
from backend.app.services.ollama_service import generate_image_description
from backend.app.services.qdrant_service import (
    ensure_collection,
    get_collection_info,
)
from backend.app.services.scanner_service import scan_library
from backend.app.services.search_service import search_assets


app = FastAPI(
    title="AI-Powered Digital Asset Management",
    version="0.1.0",
)
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
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


# ---------------------------------------------------------
# LIBRARY SCANNING
# ---------------------------------------------------------


@app.post("/index/scan")
def scan_assets():
    return scan_library("data")


# ---------------------------------------------------------
# BACKGROUND INDEXING
# ---------------------------------------------------------


def run_indexing_job(job_id: UUID) -> None:
    """
    Index all assets that are not currently indexed.

    Each asset updates the persistent indexing_jobs record,
    so the frontend can poll the job progress endpoint.
    """
    with engine.connect() as connection:
        assets = connection.execute(
            text(
                """
                SELECT id
                FROM assets
                WHERE status != 'indexed'
                ORDER BY created_at ASC
                """
            )
        ).scalars().all()

    for asset_id in assets:
        try:
            index_asset(
                UUID(str(asset_id)),
                job_id=job_id,
            )
        except Exception:
            # index_asset already records the failed asset and
            # increments the failed count for the indexing job.
            # Continue processing the remaining assets.
            continue


@app.post("/index/start")
def start_indexing(background_tasks: BackgroundTasks):
    """
    Start background indexing for all assets that are not indexed.

    Returns the job ID immediately so the frontend can poll
    /index/jobs/{job_id} for progress.
    """
    with engine.connect() as connection:
        assets = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM assets
                WHERE status != 'indexed'
                """
            )
        ).scalar_one()

    total_files = int(assets)

    job_id = create_indexing_job(
        total_files=total_files
    )

    # No assets need processing.
    if total_files == 0:
        with engine.begin() as connection:
            connection.execute(
                text(
                    """
                    UPDATE indexing_jobs
                    SET
                        status = 'completed',
                        completed_at = NOW()
                    WHERE id = :job_id
                    """
                ),
                {
                    "job_id": job_id,
                },
            )

        return {
            "status": "completed",
            "job_id": str(job_id),
            "total_files": 0,
            "message": "All assets are already indexed.",
        }

    background_tasks.add_task(
        run_indexing_job,
        job_id,
    )

    return {
        "status": "started",
        "job_id": str(job_id),
        "total_files": total_files,
    }


@app.get("/index/jobs/{job_id}")
def get_indexing_job_status(job_id: UUID):
    """
    Return the persistent progress of an indexing job.
    """
    with engine.connect() as connection:
        job = connection.execute(
            text(
                """
                SELECT
                    id,
                    total_files,
                    processed_files,
                    successful_files,
                    failed_files,
                    skipped_files,
                    status,
                    started_at,
                    completed_at,
                    created_at
                FROM indexing_jobs
                WHERE id = :job_id
                """
            ),
            {
                "job_id": job_id,
            },
        ).mappings().first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Indexing job not found",
        )

    total_files = int(job["total_files"])
    processed_files = int(job["processed_files"])

    if total_files > 0:
        progress_percent = round(
            (processed_files / total_files) * 100,
            2,
        )
    else:
        progress_percent = 100.0

    return {
        "id": str(job["id"]),
        "total_files": total_files,
        "processed_files": processed_files,
        "successful_files": int(job["successful_files"]),
        "failed_files": int(job["failed_files"]),
        "skipped_files": int(job["skipped_files"]),
        "status": job["status"],
        "progress_percent": progress_percent,
        "started_at": job["started_at"],
        "completed_at": job["completed_at"],
        "created_at": job["created_at"],
    }


# ---------------------------------------------------------
# DIRECT IMAGE ANALYSIS
# ---------------------------------------------------------


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
            {
                "asset_id": asset_id,
            },
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


# ---------------------------------------------------------
# SEMANTIC SEARCH
# ---------------------------------------------------------


@app.get("/search")
def search(
    q: str,
    limit: int = 10,
    file_type: str | None = None,
):
    try:
        return {
            "query": q,
            "results": search_assets(
                q,
                limit=limit,
                file_type=file_type,
            ),
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


# ---------------------------------------------------------
# ORIGINAL FILE / PREVIEW
# ---------------------------------------------------------


@app.get("/assets/{asset_id}/file")
def get_asset_file_response(asset_id: UUID):
    try:
        asset = get_asset_file(asset_id)

        return FileResponse(
            path=asset["original_path"],
            media_type=asset["mime_type"],
            filename=asset["filename"],
            content_disposition_type="inline",
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )