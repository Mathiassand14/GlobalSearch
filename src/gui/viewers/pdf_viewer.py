from __future__ import annotations

from typing import Optional

from PyQt6.QtWidgets import QWidget, QVBoxLayout

from .base import DocumentViewerWindow


class PDFViewerWindow(DocumentViewerWindow):
    """PDF viewer using Qt PDF if available (req 3.2, 3.3, 3.4)."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._doc = None
        self._view = None
        self._current_page = 0
        self._init_view()

    def _init_view(self) -> None:
        try:
            from PyQt6.QtPdf import QPdfDocument  # type: ignore
            from PyQt6.QtPdfWidgets import QPdfView  # type: ignore

            self._doc = QPdfDocument(self)
            self._view = QPdfView(self)
            self._view.setDocument(self._doc)
            # attach view to layout after toolbar
            layout: QVBoxLayout = self.layout()  # type: ignore
            layout.addWidget(self._view)
            # Connect navigation
            self.prev_btn.clicked.connect(self._go_prev)
            self.next_btn.clicked.connect(self._go_next)
        except Exception:
            # Qt PDF not available; leave viewer empty
            pass

    def open_document(self, file_path: str, page: int = 0) -> None:
        if self._doc is None:
            return
        self._doc.load(file_path)
        self._current_page = max(0, min(page, self._doc.pageCount() - 1))
        self._view.setPage(self._current_page)
        self._update_page_label()

    def _go_prev(self) -> None:
        if self._doc is None:
            return
        if self._current_page > 0:
            self._current_page -= 1
            self._view.setPage(self._current_page)
            self._update_page_label()

    def _go_next(self) -> None:
        if self._doc is None:
            return
        if self._current_page + 1 < self._doc.pageCount():
            self._current_page += 1
            self._view.setPage(self._current_page)
            self._update_page_label()

    def _update_page_label(self) -> None:
        if self._doc is None:
            return
        self.page_lbl.setText(f"Page: {self._current_page + 1} / {self._doc.pageCount()}")

