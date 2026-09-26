from __future__ import annotations

from pathlib import Path
from uuid import UUID

from sqlalchemy import text

from backend.app.db.database import SessionLocal
from backend.app.services.embedding_service import generate_embedding
from backend.app.services.ollama_service import (
    generate_image_description,
    generate_video_description,
)
from backend.app.services.pdf_service import extract_pdf_text
from backend.app.services.qdrant_service import upsert_asset_embedding
from backend.app.services.video_service import extract_video_frames


# Keep the text sent to the embedding model reasonably bounded.
# The complete PDF text is still stored in PostgreSQL.
PDF_EMBED_MAX_CHARS = 8000


def create_indexing_job(
    total_files: int,
) -> UUID:
    """
    Create a new indexing job and return its UUID.

    The job tracks overall indexing progress so that the frontend
    can later display progress such as:
        12 / 100 files processed
        10 successful
        2 failed
    """
    if total_files < 0:
        raise ValueError("total_files cannot be negative.")

    db = SessionLocal()

    try:
        result = db.execute(
            text(
                """
                INSERT INTO indexing_jobs (
                    total_files,
                    processed_files,
                    successful_files,
                    failed_files,
                    skipped_files,
                    status,
                    started_at
                )
                VALUES (
                    :total_files,
                    0,
                    0,
                    0,
                    0,
                    'running',
                    NOW()
                )
                RETURNING id
                """
            ),
            {
                "total_files": total_files,
            },
        )

        job_id = result.scalar_one()

        db.commit()

        return UUID(str(job_id))

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def update_indexing_job(
    db,
    job_id: UUID,
    *,
    outcome: str,
) -> None:
    """
    Record the outcome of one asset in an indexing job.

    outcome must be one of:
    - success
    - failed
    - skipped

    processed_files is incremented for every completed asset attempt,
    including skipped assets.
    """
    if outcome not in {"success", "failed", "skipped"}:
        raise ValueError(
            "Invalid indexing job outcome. "
            "Expected 'success', 'failed', or 'skipped'."
        )

    successful_increment = 1 if outcome == "success" else 0
    failed_increment = 1 if outcome == "failed" else 0
    skipped_increment = 1 if outcome == "skipped" else 0

    db.execute(
        text(
            """
            UPDATE indexing_jobs
            SET
                processed_files = processed_files + 1,
                successful_files = successful_files + :successful_increment,
                failed_files = failed_files + :failed_increment,
                skipped_files = skipped_files + :skipped_increment,
                status = CASE
                    WHEN processed_files + 1 >= total_files
                        THEN 'completed'
                    ELSE 'running'
                END,
                completed_at = CASE
                    WHEN processed_files + 1 >= total_files
                        THEN NOW()
                    ELSE completed_at
                END
            WHERE id = :job_id
            """
        ),
        {
            "job_id": job_id,
            "successful_increment": successful_increment,
            "failed_increment": failed_increment,
            "skipped_increment": skipped_increment,
        },
    )

    db.commit()


def mark_asset_failed(
    db,
    asset_id: UUID,
    error_message: str,
) -> None:
    """Store a failed processing state in PostgreSQL."""
    db.execute(
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
            "error_message": error_message,
        },
    )

    db.commit()


def index_asset(
    asset_id: UUID,
    *,
    job_id: UUID | None = None,
) -> dict:
    """
    Process one asset through:

    1. AI/content understanding
    2. Searchable text generation
    3. Embedding generation
    4. Qdrant indexing
    5. PostgreSQL status update
    6. Optional indexing-job progress update

    Supported asset types:
    - Images: Moondream
    - Videos: sampled frames + Moondream
    - PDFs: PyMuPDF text extraction

    PDF OCR for image-only/scanned PDFs is not implemented yet.

    job_id is optional so existing callers continue to work.
    """

    db = SessionLocal()

    try:
        asset = db.execute(
            text(
                """
                SELECT
                    id,
                    filename,
                    original_path,
                    file_type,
                    description,
                    extracted_text,
                    status
                FROM assets
                WHERE id = :asset_id
                """
            ),
            {
                "asset_id": asset_id,
            },
        ).mappings().first()

        if not asset:
            raise ValueError(
                f"Asset not found: {asset_id}"
            )

        # ---------------------------------------------------------
        # ALREADY INDEXED
        # ---------------------------------------------------------
        if asset["status"] == "indexed":

            result = {
                "status": "skipped",
                "reason": "Asset is already indexed.",
                "asset_id": str(asset_id),
                "filename": asset["filename"],
            }

            if job_id is not None:
                update_indexing_job(
                    db,
                    job_id,
                    outcome="skipped",
                )

            return result

        asset_path = Path(asset["original_path"])

        # ---------------------------------------------------------
        # FILE EXISTENCE
        # ---------------------------------------------------------
        if not asset_path.exists():

            error_message = (
                f"Asset file does not exist: {asset_path}"
            )

            mark_asset_failed(
                db,
                asset_id,
                error_message,
            )

            if job_id is not None:
                update_indexing_job(
                    db,
                    job_id,
                    outcome="failed",
                )

            raise FileNotFoundError(error_message)

        description = asset["description"]

        # ---------------------------------------------------------
        # IMAGE / VIDEO / PDF CONTENT UNDERSTANDING
        # ---------------------------------------------------------
        if not description:

            db.execute(
                text(
                    """
                    UPDATE assets
                    SET
                        status = 'ai_processing',
                        error_message = NULL,
                        updated_at = NOW()
                    WHERE id = :asset_id
                    """
                ),
                {
                    "asset_id": asset_id,
                },
            )

            db.commit()

            # -------------------------
            # IMAGE
            # -------------------------
            if asset["file_type"] == "image":

                description = generate_image_description(
                    asset_path
                )

            # -------------------------
            # VIDEO
            # -------------------------
            elif asset["file_type"] == "video":

                frames = extract_video_frames(
                    asset_path,
                    max_frames=5,
                    max_image_size=384,
                )

                description = generate_video_description(
                    frames
                )

            # -------------------------
            # PDF
            # -------------------------
            elif asset["file_type"] == "pdf":

                pdf_text = extract_pdf_text(
                    asset_path
                )

                if not pdf_text:
                    raise ValueError(
                        "PDF contains no extractable text. "
                        "OCR fallback is not implemented yet."
                    )

                # Store the complete extracted document text.
                db.execute(
                    text(
                        """
                        UPDATE assets
                        SET
                            extracted_text = :extracted_text,
                            updated_at = NOW()
                        WHERE id = :asset_id
                        """
                    ),
                    {
                        "asset_id": asset_id,
                        "extracted_text": pdf_text,
                    },
                )

                db.commit()

                # Use actual document content for semantic search.
                #
                # The complete text remains in extracted_text.
                # A bounded portion is kept in description so that
                # embedding generation stays manageable for local models.
                if len(pdf_text) > PDF_EMBED_MAX_CHARS:
                    description = pdf_text[:PDF_EMBED_MAX_CHARS]
                else:
                    description = pdf_text

            else:
                raise NotImplementedError(
                    f"AI enrichment for "
                    f"'{asset['file_type']}' "
                    "is not implemented."
                )

            # -----------------------------------------------------
            # SAVE SEARCHABLE CONTENT
            # -----------------------------------------------------
            db.execute(
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

            db.commit()

        # ---------------------------------------------------------
        # EMBEDDING
        # ---------------------------------------------------------
        if not description:
            raise ValueError(
                "No searchable content available for embedding."
            )

        vector = generate_embedding(
            description
        )

        # ---------------------------------------------------------
        # QDRANT
        # ---------------------------------------------------------
        upsert_asset_embedding(
            UUID(str(asset["id"])),
            vector,
            filename=asset["filename"],
            file_type=asset["file_type"],
        )

        # ---------------------------------------------------------
        # COMPLETE ASSET
        # ---------------------------------------------------------
        db.execute(
            text(
                """
                UPDATE assets
                SET
                    status = 'indexed',
                    error_message = NULL,
                    updated_at = NOW()
                WHERE id = :asset_id
                """
            ),
            {
                "asset_id": asset_id,
            },
        )

        db.commit()

        if job_id is not None:
            update_indexing_job(
                db,
                job_id,
                outcome="success",
            )

        return {
            "status": "indexed",
            "asset_id": str(asset_id),
            "filename": asset["filename"],
            "file_type": asset["file_type"],
        }

    except Exception as exc:

        db.rollback()

        try:
            mark_asset_failed(
                db,
                asset_id,
                str(exc),
            )
        except Exception:
            db.rollback()

        if job_id is not None:
            try:
                update_indexing_job(
                    db,
                    job_id,
                    outcome="failed",
                )
            except Exception:
                db.rollback()

        raise

    finally:
        db.close()