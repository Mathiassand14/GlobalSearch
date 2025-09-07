from __future__ import annotations

import pytest

PyQt6 = pytest.importorskip("PyQt6")

try:
    pytest.importorskip("PyQt6.QtPdf")
    pytest.importorskip("PyQt6.QtPdfWidgets")
except Exception:
    pytest.skip("Qt PDF not available", allow_module_level=True)

from src.gui.viewers import PDFViewerWindow


def test_pdf_viewer_instantiation(qtbot):
    win = PDFViewerWindow()
    qtbot.addWidget(win)
    win.show()
    # Without a real file, just ensure widget is constructed
    assert win.windowTitle()

