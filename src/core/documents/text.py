from __future__ import annotations

from pathlib import Path
from typing import Iterable

from src.core.documents.base import DocumentProcessor
from src.core.documents.models import DocumentContent


def _read_with_detection(file_path: Path) -> str:
    # Try common encodings without external deps
    encodings = ("utf-8", "utf-8-sig", "latin-1")
    for enc in encodings:
        try:
            return file_path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    # Fallback: binary decode with replacement to avoid crash
    return file_path.read_bytes().decode("utf-8", errors="replace")


class TextProcessor(DocumentProcessor):
    @property
    def name(self) -> str:  # pragma: no cover - trivial
        return "text"

    @property
    def supported_suffixes(self) -> Iterable[str]:  # pragma: no cover - trivial
        return [".txt", ".md"]

    def process(self, file_path: Path) -> DocumentContent:
        text = _read_with_detection(file_path)
        title = file_path.stem
        return DocumentContent.from_text(file_path=file_path, title=title, text=text)

