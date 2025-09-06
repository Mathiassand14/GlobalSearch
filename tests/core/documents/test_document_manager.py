from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pytest

from src.core.documents import DocumentContent, DocumentManager, DocumentProcessor
from src.core.exceptions.exceptions import DocumentProcessingError


class _MockTextProcessor(DocumentProcessor):
    def __init__(self) -> None:
        self._calls = 0

    @property
    def name(self) -> str:
        return "mock-text"

    @property
    def supported_suffixes(self) -> Iterable[str]:
        return [".txt", ".md"]

    def process(self, file_path: Path) -> DocumentContent:
        self._calls += 1
        return DocumentContent.from_text(file_path, title=file_path.stem, text="hello world")


class _OtherProcessor(DocumentProcessor):
    @property
    def name(self) -> str:
        return "other"

    @property
    def supported_suffixes(self) -> Iterable[str]:
        return [".md", ".rst"]

    def process(self, file_path: Path) -> DocumentContent:  # pragma: no cover - not used
        return DocumentContent.from_text(file_path, title=file_path.stem, text="x")


def test_registration_and_routing_prefers_first_match(tmp_path: Path) -> None:
    mgr = DocumentManager()
    p1 = _MockTextProcessor()
    p2 = _OtherProcessor()
    mgr.register(p1)
    mgr.register(p2)

    # First registration for .md wins
    assert ".md" in mgr.registered_suffixes
    proc = mgr.get_processor_for(Path("note.MD"))
    assert proc is p1

    # .txt handled by p1 only
    proc_txt = mgr.get_processor_for(Path("file.txt"))
    assert proc_txt is p1

    content = mgr.process(tmp_path / "file.txt")
    assert content.title == "file"
    assert content.pages[0].text == "hello world"


def test_unknown_suffix_raises() -> None:
    mgr = DocumentManager()
    with pytest.raises(DocumentProcessingError):
        mgr.process(Path("unknown.xyz"))

