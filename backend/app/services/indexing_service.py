from __future__ import annotations

from pathlib import Path
from uuid import UUID

from sqlalchemy import text

from backend.app.db.database import SessionLocal
from backend.app.services.embedding_service import generate_embedding
from backend.app.services.ollama_service import generate_image_description
from backend.app.services.qdrant_service import upsert_asset_embedding


def index_asset(asset_id: UUID) -> dict:
    """
    Process one asset through AI enrichment, embedding generation,
    and Qdrant indexing.

    Currently, image AI enrichment is supported.
    PDF and video enrichment will be added in their respective stages.
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
                    status
                FROM assets
                WHERE id = :asset_id
                """
            ),
            {"asset_id": asset_id},
        ).mappings().first()

        if not asset:
            raise ValueError(f"Asset not found: {asset_id}")

        # Already completely indexed.
        if asset["status"] == "indexed":
            return {
                "status": "skipped",
                "reason": "Asset is already indexed.",
                "asset_id": str(asset_id),
            }

        asset_path = Path(asset["original_path"])

        if not asset_path.exists():
            error_message = f"Asset file does not exist: {asset_path}"

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

            raise FileNotFoundError(error_message)

        description = asset["description"]

        # Generate AI understanding only when it does not already exist.
        if not description:
            if asset["file_type"] != "image":
                raise NotImplementedError(
                    f"AI enrichment for '{asset['file_type']}' "
                    "is not implemented yet."
                )

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
                {"asset_id": asset_id},
            )
            db.commit()

            description = generate_image_description(asset_path)

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

        # Convert searchable text into a semantic vector.
        vector = generate_embedding(description)

        # Store/update the vector in Qdrant.
        upsert_asset_embedding(
            UUID(str(asset["id"])),
            vector,
            filename=asset["filename"],
            file_type=asset["file_type"],
        )

        # Mark the complete pipeline as finished.
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
            {"asset_id": asset_id},
        )
        db.commit()

        return {
            "status": "indexed",
            "asset_id": str(asset_id),
            "filename": asset["filename"],
        }

    except Exception as exc:
        db.rollback()

        try:
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
                    "error_message": str(exc),
                },
            )
            db.commit()
        except Exception:
            db.rollback()

        raise

    finally:
        db.close()