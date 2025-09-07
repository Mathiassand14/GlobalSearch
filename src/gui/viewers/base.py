from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget


class DocumentViewerWindow(QWidget):
    """Base viewer window with simple navigation controls."""

    request_close = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Document Viewer")
        self._build_chrome()

    def _build_chrome(self) -> None:
        outer = QVBoxLayout(self)
        self.toolbar = QHBoxLayout()
        self.prev_btn = QPushButton("Prev", self)
        self.next_btn = QPushButton("Next", self)
        self.page_lbl = QLabel("Page: 1", self)
        self.toolbar.addWidget(self.prev_btn)
        self.toolbar.addWidget(self.next_btn)
        self.toolbar.addWidget(self.page_lbl)
        outer.addLayout(self.toolbar)

    # API to implement in subclasses
    def open_document(self, file_path: str, page: int = 0) -> None:  # pragma: no cover - abstract
        raise NotImplementedError

