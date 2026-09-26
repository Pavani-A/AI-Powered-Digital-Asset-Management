from __future__ import annotations

import base64
import io
import json
from pathlib import Path
from urllib import request

from PIL import Image

from backend.app.db.database import settings


OLLAMA_URL = f"{settings.ollama_base_url}/api/generate"


def prepare_image(path: Path) -> str:
    """
    Create a small in-memory JPEG representation.

    The original asset is never modified.
    """
    with Image.open(path) as image:
        image = image.convert("RGB")

        image.thumbnail(
            (
                settings.vision_max_image_size,
                settings.vision_max_image_size,
            ),
            Image.Resampling.LANCZOS,
        )

        buffer = io.BytesIO()

        image.save(
            buffer,
            format="JPEG",
            quality=settings.vision_jpeg_quality,
            optimize=True,
        )

    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def generate_image_description(path: str | Path) -> str:
    """
    Ask the configured local vision model to describe an image.
    """
    image_path = Path(path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"Asset not found: {image_path}"
        )

    encoded_image = prepare_image(image_path)

    payload = {
        "model": settings.ollama_vision_model,
        "prompt": (
            "Analyze this image for a digital asset management search system. "
            "Describe the main subject, objects, scene, activities, colors, "
            "and notable visual details. Mention visible text only when clearly "
            "readable. Use concise factual language. Do not invent details."
        ),
        "images": [encoded_image],
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 100,
        },
    }

    body = json.dumps(payload).encode("utf-8")

    http_request = request.Request(
        OLLAMA_URL,
        data=body,
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with request.urlopen(
        http_request,
        timeout=settings.ai_request_timeout_seconds,
    ) as response:
        result = json.loads(
            response.read().decode("utf-8")
        )

    description = result.get("response", "").strip()

    if not description:
        raise RuntimeError(
            "Ollama returned an empty response."
        )

    return description