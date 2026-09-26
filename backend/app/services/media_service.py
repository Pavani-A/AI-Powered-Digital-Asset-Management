from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import UUID

from sqlalchemy import text

from backend.app.db.database import SessionLocal


def get_asset_file(asset_id: UUID) -> dict[str, Any]:
    """
    Retrieve the local file information for an indexed asset.
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
                    mime_type
                FROM assets
                WHERE id = :asset_id
                """
            ),
            {"asset_id": asset_id},
        ).mappings().first()

        if not asset:
            raise ValueError(f"Asset not found: {asset_id}")

        path = Path(asset["original_path"])

        if not path.exists():
            raise FileNotFoundError(
                f"Asset file does not exist: {path}"
            )

        if not path.is_file():
            raise ValueError(
                f"Asset path is not a file: {path}"
            )

        return {
            "id": UUID(str(asset["id"])),
            "filename": asset["filename"],
            "original_path": path,
            "file_type": asset["file_type"],
            "mime_type": asset["mime_type"],
        }

    finally:
        db.close()