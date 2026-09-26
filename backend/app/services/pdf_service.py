from __future__ import annotations

from pathlib import Path

import pymupdf


def extract_pdf_text(path: str | Path) -> str:
    """
    Extract searchable text from all pages of a PDF.

    Pages are separated by blank lines so the resulting text
    remains readable and usable for semantic search.
    """
    pdf_path = Path(path)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(
            f"Expected a PDF file: {pdf_path}"
        )

    pages: list[str] = []

    with pymupdf.open(pdf_path) as document:
        for page in document:
            page_text = page.get_text(
                "text",
                sort=True,
            ).strip()

            if page_text:
                pages.append(page_text)

    return "\n\n".join(pages).strip()


def chunk_text(
    text: str,
    *,
    max_chars: int = 4000,
    overlap: int = 400,
) -> list[str]:
    """
    Split text into overlapping chunks.

    Overlap helps preserve context across chunk boundaries.
    """
    text = text.strip()

    if not text:
        return []

    if max_chars <= 0:
        raise ValueError(
            "max_chars must be greater than zero."
        )

    if overlap < 0 or overlap >= max_chars:
        raise ValueError(
            "overlap must be >= 0 and < max_chars."
        )

    if len(text) <= max_chars:
        return [text]

    chunks: list[str] = []

    start = 0

    while start < len(text):
        end = min(
            start + max_chars,
            len(text),
        )

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = end - overlap

    return chunks


def extract_pdf_chunks(
    path: str | Path,
    *,
    max_chars: int = 4000,
    overlap: int = 400,
) -> list[dict[str, object]]:
    """
    Extract PDF text page by page and return searchable chunks.

    Each chunk contains:
    - page_number: one-based PDF page number
    - chunk_index: zero-based chunk number within that page
    - text: extracted text
    """
    pdf_path = Path(path)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(
            f"Expected a PDF file: {pdf_path}"
        )

    structured_chunks: list[dict[str, object]] = []

    with pymupdf.open(pdf_path) as document:
        for page_number, page in enumerate(
            document,
            start=1,
        ):
            page_text = page.get_text(
                "text",
                sort=True,
            ).strip()

            if not page_text:
                continue

            chunks = chunk_text(
                page_text,
                max_chars=max_chars,
                overlap=overlap,
            )

            for chunk_index, chunk in enumerate(chunks):
                structured_chunks.append(
                    {
                        "page_number": page_number,
                        "chunk_index": chunk_index,
                        "text": chunk,
                    }
                )

    return structured_chunks