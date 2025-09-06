from __future__ import annotations

from pathlib import Path
from typing import Iterable

from src.core.documents.base import DocumentProcessor
from src.core.documents.models import DocumentContent, PageContent
from src.core.exceptions.exceptions import DocumentProcessingError


class PDFProcessor(DocumentProcessor):
    """PDF processor using pdfplumber for text extraction (requirement 2.2)."""

    @property
    def name(self) -> str:  # pragma: no cover - trivial
        return "pdf-plumber"

    @property
    def supported_suffixes(self) -> Iterable[str]:  # pragma: no cover - trivial
        return [".pdf"]

    def process(self, file_path: Path) -> DocumentContent:
        try:
            # Import inside method to avoid hard dependency at module import time in tests
            import pdfplumber  # type: ignore

            with pdfplumber.open(str(file_path)) as pdf:  # type: ignore[attr-defined]
                title = getattr(getattr(pdf, "metadata", {}), "get", lambda *_: None)("Title")
                if not title:
                    # Attempt dict-style access if metadata is a dict
                    meta = getattr(pdf, "metadata", {})
                    if isinstance(meta, dict):
                        title = meta.get("Title")
                if not title:
                    title = file_path.stem

                pages = []
                for idx, page in enumerate(getattr(pdf, "pages", []) or []):
                    # pdfplumber Page has extract_text(); default to empty string if None
                    text = page.extract_text() or ""
                    pages.append(PageContent(page_number=idx, text=text))

                return DocumentContent(file_path=file_path, title=title, pages=pages)
        except DocumentProcessingError:
            raise
        except Exception as exc:  # pragma: no cover - wrapped for robustness
            raise DocumentProcessingError(f"Failed to process PDF: {file_path} ({exc})") from exc

