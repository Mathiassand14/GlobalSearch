from __future__ import annotations

from pathlib import Path

import pytest

PyQt6 = pytest.importorskip("PyQt6")

from src.gui.viewers import TextViewerWindow


def test_text_viewer_loads_content(qtbot, tmp_path: Path):
    f = tmp_path / "note.txt"
    content = "hello world\nthis is a test"
    f.write_text(content, encoding="utf-8")

    win = TextViewerWindow()
    qtbot.addWidget(win)
    win.show()
    win.open_document(str(f))

    qtbot.wait(50)
    assert content in win.findChild(type(win)._editor).__class__  # dummy to use attribute
    # Safer: read text from the editor directly
    assert content in win.findChild(type(win._editor)).toPlainText()

