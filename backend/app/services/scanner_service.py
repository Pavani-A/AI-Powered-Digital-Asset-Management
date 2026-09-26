from __future__ import annotations
import pymupdf
import hashlib
import json
import mimetypes
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import fitz
from PIL import Image
from sqlalchemy import text

from backend.app.db.database import SessionLocal


SUPPORTED_EXTENSIONS = {
    "image": {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".bmp",
        ".gif",
        ".tiff",
    },
    "video": {
        ".mp4",
        ".mov",
        ".avi",
        ".mkv",
        ".webm",
        ".mpeg",
        ".mpg",
    },
    "pdf": {
        ".pdf",
    },
}


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Calculate SHA-256 without loading the entire file into memory."""
    digest = hashlib.sha256()

    with path.open("rb") as file:
        while chunk := file.read(chunk_size):
            digest.update(chunk)

    return digest.hexdigest()


def detect_file_type(path: Path) -> str | None:
    """Return the supported asset type based on file extension."""
    suffix = path.suffix.lower()

    for file_type, extensions in SUPPORTED_EXTENSIONS.items():
        if suffix in extensions:
            return file_type

    return None


def get_mime_type(path: Path) -> str | None:
    mime_type, _ = mimetypes.guess_type(path.name)
    return mime_type


def extract_image_metadata(path: Path) -> dict[str, Any]:
    with Image.open(path) as image:
        return {
            "width": image.width,
            "height": image.height,
        }


def extract_pdf_metadata(path: Path) -> dict[str, Any]:
    with fitz.open(path) as document:
        return {
            "page_count": document.page_count,
        }


def extract_video_metadata(path: Path) -> dict[str, Any]:
    """Extract basic video metadata using ffprobe."""
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-show_entries",
        "stream=codec_type,width,height,r_frame_rate",
        "-of",
        "json",
        str(path),
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True,
    )

    data = json.loads(result.stdout)

    video_stream = next(
        (
            stream
            for stream in data.get("streams", [])
            if stream.get("codec_type") == "video"
        ),
        {},
    )

    duration = data.get("format", {}).get("duration")

    frame_rate = None
    rate = video_stream.get("r_frame_rate")

    if rate and rate != "0/0":
        try:
            numerator, denominator = rate.split("/")
            if float(denominator) != 0:
                frame_rate = float(numerator) / float(denominator)
        except (ValueError, ZeroDivisionError):
            frame_rate = None

    return {
        "width": video_stream.get("width"),
        "height": video_stream.get("height"),
        "duration_seconds": float(duration) if duration else None,
        "frame_rate": frame_rate,
    }


def extract_metadata(path: Path, file_type: str) -> dict[str, Any]:
    metadata: dict[str, Any] = {}

    if file_type == "image":
        metadata.update(extract_image_metadata(path))

    elif file_type == "video":
        metadata.update(extract_video_metadata(path))

    elif file_type == "pdf":
        metadata.update(extract_pdf_metadata(path))

    return metadata


def is_unchanged(
    existing: dict[str, Any],
    size_bytes: int,
    modified_at: datetime,
) -> bool:
    """Avoid reprocessing files that have not changed."""
    existing_modified = existing["file_modified_at"]

    if existing_modified is None:
        return False

    return (
        existing["size_bytes"] == size_bytes
        and existing_modified == modified_at
    )


def get_existing_asset(db, path_str: str) -> dict[str, Any] | None:
    result = db.execute(
        text(
            """
            SELECT
                id,
                original_path,
                size_bytes,
                file_modified_at,
                sha256,
                status
            FROM assets
            WHERE original_path = :original_path
            """
        ),
        {"original_path": path_str},
    ).mappings().first()

    return dict(result) if result else None


def sha_exists(db, sha256: str, path_str: str) -> bool:
    result = db.execute(
        text(
            """
            SELECT 1
            FROM assets
            WHERE sha256 = :sha256
              AND original_path <> :original_path
            LIMIT 1
            """
        ),
        {
            "sha256": sha256,
            "original_path": path_str,
        },
    ).first()

    return result is not None


def insert_asset(
    db,
    *,
    path: Path,
    file_type: str,
    mime_type: str | None,
    size_bytes: int,
    sha256: str,
    modified_at: datetime,
    metadata: dict[str, Any],
) -> None:
    db.execute(
        text(
            """
            INSERT INTO assets (
                filename,
                original_path,
                file_type,
                mime_type,
                size_bytes,
                sha256,
                width,
                height,
                duration_seconds,
                frame_rate,
                page_count,
                status,
                file_modified_at
            )
            VALUES (
                :filename,
                :original_path,
                :file_type,
                :mime_type,
                :size_bytes,
                :sha256,
                :width,
                :height,
                :duration_seconds,
                :frame_rate,
                :page_count,
                'pending',
                :file_modified_at
            )
            """
        ),
        {
            "filename": path.name,
            "original_path": str(path.resolve()),
            "file_type": file_type,
            "mime_type": mime_type,
            "size_bytes": size_bytes,
            "sha256": sha256,
            "width": metadata.get("width"),
            "height": metadata.get("height"),
            "duration_seconds": metadata.get("duration_seconds"),
            "frame_rate": metadata.get("frame_rate"),
            "page_count": metadata.get("page_count"),
            "file_modified_at": modified_at,
        },
    )


def update_asset(
    db,
    *,
    asset_id,
    path: Path,
    file_type: str,
    mime_type: str | None,
    size_bytes: int,
    sha256: str,
    modified_at: datetime,
    metadata: dict[str, Any],
) -> None:
    db.execute(
        text(
            """
            UPDATE assets
            SET
                filename = :filename,
                file_type = :file_type,
                mime_type = :mime_type,
                size_bytes = :size_bytes,
                sha256 = :sha256,
                width = :width,
                height = :height,
                duration_seconds = :duration_seconds,
                frame_rate = :frame_rate,
                page_count = :page_count,
                status = 'pending',
                error_message = NULL,
                file_modified_at = :file_modified_at,
                updated_at = NOW()
            WHERE id = :asset_id
            """
        ),
        {
            "asset_id": asset_id,
            "filename": path.name,
            "file_type": file_type,
            "mime_type": mime_type,
            "size_bytes": size_bytes,
            "sha256": sha256,
            "width": metadata.get("width"),
            "height": metadata.get("height"),
            "duration_seconds": metadata.get("duration_seconds"),
            "frame_rate": metadata.get("frame_rate"),
            "page_count": metadata.get("page_count"),
            "file_modified_at": modified_at,
        },
    )


def scan_library(data_root: str | Path = "data") -> dict[str, int]:
    """
    Scan the local DAM library and register supported assets in PostgreSQL.

    Unchanged files are skipped.
    New files are inserted.
    Changed files are updated.
    Exact duplicate content is detected using SHA-256.
    """
    root = Path(data_root).resolve()

    if not root.exists():
        raise FileNotFoundError(f"Data directory does not exist: {root}")

    files = [
        path
        for path in root.rglob("*")
        if path.is_file() and detect_file_type(path) is not None
    ]

    db = SessionLocal()

    stats = {
        "total_files": len(files),
        "indexed": 0,
        "updated": 0,
        "skipped": 0,
        "duplicates": 0,
        "failed": 0,
    }

    try:
        for path in files:
            path_str = str(path.resolve())

            try:
                stat = path.stat()

                modified_at = datetime.fromtimestamp(
                    stat.st_mtime,
                    tz=timezone.utc,
                )

                size_bytes = stat.st_size
                file_type = detect_file_type(path)

                if file_type is None:
                    stats["skipped"] += 1
                    continue

                existing = get_existing_asset(db, path_str)

                # Incremental indexing:
                # unchanged size + modification time means no work is needed.
                if existing and is_unchanged(
                    existing,
                    size_bytes,
                    modified_at,
                ):
                    stats["skipped"] += 1
                    continue

                sha256 = sha256_file(path)

                # Prevent storing multiple copies of identical content.
                if sha_exists(db, sha256, path_str):
                    stats["duplicates"] += 1
                    continue

                metadata = extract_metadata(path, file_type)
                mime_type = get_mime_type(path)

                if existing:
                    update_asset(
                        db,
                        asset_id=existing["id"],
                        path=path,
                        file_type=file_type,
                        mime_type=mime_type,
                        size_bytes=size_bytes,
                        sha256=sha256,
                        modified_at=modified_at,
                        metadata=metadata,
                    )
                    stats["updated"] += 1

                else:
                    insert_asset(
                        db,
                        path=path,
                        file_type=file_type,
                        mime_type=mime_type,
                        size_bytes=size_bytes,
                        sha256=sha256,
                        modified_at=modified_at,
                        metadata=metadata,
                    )
                    stats["indexed"] += 1

                db.commit()

            except Exception as exc:
                db.rollback()

                if existing:
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
                            "asset_id": existing["id"],
                            "error_message": str(exc),
                        },
                    )
                    db.commit()

                stats["failed"] += 1

        return stats

    finally:
        db.close()