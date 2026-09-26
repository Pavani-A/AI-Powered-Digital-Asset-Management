from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
from typing import Any

from backend.app.db.database import settings


def get_video_duration(path: Path) -> float:
    """Get video duration in seconds using ffprobe."""
    command = [
        settings.ffprobe_path,
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(path),
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True,
    )

    duration = result.stdout.strip()

    if not duration:
        raise RuntimeError(
            "Could not determine video duration."
        )

    return float(duration)


def choose_sample_timestamps(
    duration: float,
    max_frames: int = 5,
) -> list[float]:
    """
    Choose evenly distributed timestamps for visual sampling.

    For very short videos, fewer timestamps are used.
    """
    if duration <= 0:
        return [0.0]

    if duration < 3:
        return [duration / 2]

    frame_count = min(max_frames, 5)

    if frame_count == 1:
        return [duration / 2]

    # Avoid sampling exactly at the end of the video.
    start = duration * 0.1
    end = duration * 0.9

    step = (end - start) / (frame_count - 1)

    return [
        round(start + (step * index), 2)
        for index in range(frame_count)
    ]


def extract_video_frames(
    path: str | Path,
    *,
    max_frames: int = 5,
    max_image_size: int = 384,
) -> list[dict[str, Any]]:
    """
    Extract a small number of resized JPEG frames from a video.

    Frames are stored in a temporary directory and automatically
    removed when this function finishes.
    """
    video_path = Path(path)

    if not video_path.exists():
        raise FileNotFoundError(
            f"Video not found: {video_path}"
        )

    duration = get_video_duration(video_path)

    timestamps = choose_sample_timestamps(
        duration,
        max_frames=max_frames,
    )

    frames: list[dict[str, Any]] = []

    with tempfile.TemporaryDirectory(
        prefix="dam-video-frames-"
    ) as temp_dir:
        temp_path = Path(temp_dir)

        for index, timestamp in enumerate(timestamps):
            output_path = (
                temp_path / f"frame_{index:02d}.jpg"
            )

            command = [
                settings.ffmpeg_path,
                "-y",
                "-ss",
                str(timestamp),
                "-i",
                str(video_path),
                "-frames:v",
                "1",
                "-vf",
                f"scale={max_image_size}:-1",
                "-q:v",
                "5",
                str(output_path),
            ]

            try:
                subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    check=True,
                )
            except subprocess.CalledProcessError as exc:
                raise RuntimeError(
                    f"Failed to extract frame at "
                    f"{timestamp}s: {exc.stderr}"
                ) from exc

            if not output_path.exists():
                raise RuntimeError(
                    f"FFmpeg did not create frame: "
                    f"{output_path}"
                )

            frame_bytes = output_path.read_bytes()

            frames.append(
                {
                    "timestamp": timestamp,
                    "filename": output_path.name,
                    "bytes": frame_bytes,
                }
            )

    return frames