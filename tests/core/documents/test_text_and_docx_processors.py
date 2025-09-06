from __future__ import annotations

import types
from pathlib import Path

from src.core.documents import DocxProcessor, DocumentManager, TextProcessor


def test_text_processor_reads_utf8(tmp_path: Path) -> None:
    p = tmp_path / "note.txt"
    content = "héllo world"  # includes non-ascii
    p.write_text(content, encoding="utf-8")
    mgr = DocumentManager()
    mgr.register(TextProcessor())
    dc = mgr.process(p)
    assert dc.pages[0].text == content


def test_docx_processor_reads_paragraphs(monkeypatch) -> None:
    # Fake python-docx Document
    class _FakeParagraph:
        def __init__(self, text: str) -> None:
            self.text = text

    class _FakeDocument:
        def __init__(self) -> None:
            self.paragraphs = [_FakeParagraph("Hello"), _FakeParagraph("World")]

    fake_docx = types.SimpleNamespace(Document=lambda path: _FakeDocument())
    monkeypatch.setitem(__import__("sys").modules, "docx", fake_docx)

    mgr = DocumentManager()
    mgr.register(DocxProcessor())
    dc = mgr.process(Path("/tmp/sample.docx"))
    assert dc.pages[0].text == "Hello\nWorld"

