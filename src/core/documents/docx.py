from __future__ import annotations

from pathlib import Path
from typing import Iterable

from src.core.documents.base import DocumentProcessor
from src.core.documents.models import DocumentContent
from src.core.exceptions.exceptions import DocumentProcessingError


class DocxProcessor(DocumentProcessor):
    @property
    def name(self) -> str:  # pragma: no cover - trivial
        return "docx"

    @property
    def supported_suffixes(self) -> Iterable[str]:  # pragma: no cover - trivial
        return [".docx"]

    def process(self, file_path: Path) -> DocumentContent:
        try:
            import docx  # type: ignore

            d = docx.Document(str(file_path))  # type: ignore[attr-defined]
            paragraphs = [p.text or "" for p in getattr(d, "paragraphs", [])]
            text = "\n".join(paragraphs)
            title = file_path.stem
            return DocumentContent.from_text(file_path=file_path, title=title, text=text)
        except DocumentProcessingError:
            raise
        except Exception as exc:  # pragma: no cover
            raise DocumentProcessingError(f"Failed to process DOCX: {file_path} ({exc})") from exc

