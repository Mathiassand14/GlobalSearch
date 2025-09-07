from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import QThread
from PyQt6.QtGui import QTextCharFormat, QTextCursor, QColor
from PyQt6.QtWidgets import QTextEdit, QVBoxLayout, QWidget

from .base import DocumentViewerWindow
from src.gui.workers.text_loader import TextLoadWorker


class TextViewerWindow(DocumentViewerWindow):
    """Viewer for text/markdown files with simple term highlighting (req 3.2, 3.3, 3.4)."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._editor = QTextEdit(self)
        self._editor.setReadOnly(True)
        layout: QVBoxLayout = self.layout()  # type: ignore[assignment]
        layout.addWidget(self._editor)

        self._thread = QThread(self)
        self._worker = TextLoadWorker()
        self._worker.moveToThread(self._thread)
        self._worker.loaded.connect(self._on_loaded)
        self._thread.start()
        self._pending_terms: list[str] = []

    def open_document(self, file_path: str, page: int = 0) -> None:  # page ignored for text
        # Asynchronous load via worker
        QThread.currentThread()  # ensure Qt thread initialized
        self._editor.clear()
        self._worker.load(file_path)

    def set_highlight_terms(self, terms: list[str]) -> None:
        self._pending_terms = terms
        # Apply immediately if content exists
        if self._editor.toPlainText():
            self._apply_highlights()

    def _on_loaded(self, content: str) -> None:
        self._editor.setPlainText(content)
        self._apply_highlights()

    def _apply_highlights(self) -> None:
        if not self._pending_terms:
            return
        cursor = self._editor.textCursor()
        doc = self._editor.document()
        fmt = QTextCharFormat()
        fmt.setBackground(QColor("yellow"))

        for term in self._pending_terms:
            if not term:
                continue
            # Simple case-insensitive search
            cursor = QTextCursor(doc)
            flags = QTextCursor.FindFlag.FindCaseSensitively
            while True:
                cursor = doc.find(term, cursor)
                if cursor.isNull():
                    break
                cursor.mergeCharFormat(fmt)

    def closeEvent(self, event) -> None:  # noqa: N802
        self._thread.quit()
        self._thread.wait(1000)
        super().closeEvent(event)

