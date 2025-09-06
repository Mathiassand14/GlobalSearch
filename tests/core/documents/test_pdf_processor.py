from __future__ import annotations

import types
from pathlib import Path

import pytest

from src.core.documents import DocumentManager, PDFProcessor
from src.core.exceptions.exceptions import DocumentProcessingError


class _FakePage:
    def __init__(self, text: str) -> None:
        self._text = text

    def extract_text(self) -> str:
        return self._text


class _FakePDF:
    def __init__(self, pages: list[_FakePage], metadata: dict | None = None) -> None:
        self.pages = pages
        self.metadata = metadata or {"Title": "Fake PDF"}

    def __enter__(self) -> "_FakePDF":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # noqa: ANN001
        return None


def test_pdf_processor_extracts_pages(monkeypatch) -> None:
    # Arrange fake pdfplumber module
    fake_module = types.SimpleNamespace()

    def fake_open(_path: str) -> _FakePDF:
        return _FakePDF([_FakePage("hello"), _FakePage("world")], metadata={"Title": "Doc"})

    fake_module.open = fake_open  # type: ignore[attr-defined]
    monkeypatch.setitem(__import__("sys").modules, "pdfplumber", fake_module)

    mgr = DocumentManager()
    mgr.register(PDFProcessor())

    # Act
    content = mgr.process(Path("/tmp/example.pdf"))

    # Assert
    assert content.title == "Doc"
    assert len(content.pages) == 2
    assert content.pages[0].text == "hello"
    assert content.pages[1].text == "world"


def test_pdf_processor_wraps_errors(monkeypatch) -> None:
    fake_module = types.SimpleNamespace()

    def fake_open(_path: str):  # noqa: ANN001
        raise RuntimeError("pdf corrupted or password-protected")

    fake_module.open = fake_open  # type: ignore[attr-defined]
    monkeypatch.setitem(__import__("sys").modules, "pdfplumber", fake_module)

    mgr = DocumentManager()
    mgr.register(PDFProcessor())

    with pytest.raises(DocumentProcessingError):
        mgr.process(Path("/tmp/bad.pdf"))

