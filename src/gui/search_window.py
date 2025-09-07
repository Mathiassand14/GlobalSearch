from __future__ import annotations

from typing import Callable, List, Optional

from PyQt6.QtCore import QThread, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QWidget,
)

from src.core.events import EventBus, SearchResultSelected
from src.core.models.search import SearchResult
from src.gui.workers.search_worker import SearchTask, SearchWorker


SearchFn = Callable[[str, int], List[SearchResult]]


class SearchWindow(QWidget):
    """Main search window with debounced query input and results list (req 3.1, 4.2, 4.5)."""

    result_selected = pyqtSignal(str, int)  # document_id, page

    def __init__(
        self,
        search_fn: SearchFn,
        event_bus: Optional[EventBus] = None,
        debounce_ms: int = 300,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._event_bus = event_bus or EventBus()
        self._search_fn = search_fn
        self._debounce_ms = debounce_ms

        self._build_ui()
        self._wire_debounce()

        # Thread and worker setup
        self._thread = QThread(self)
        self._worker = SearchWorker(self._search_fn)
        self._worker.moveToThread(self._thread)
        self._worker.results_ready.connect(self._on_results_ready)
        self._thread.start()

    def _build_ui(self) -> None:
        self.setWindowTitle("GlobalSearch — Search")
        grid = QGridLayout(self)

        # Row 0: query + search button
        self.query_edit = QLineEdit(self)
        self.query_edit.setPlaceholderText("Type to search…")
        self.search_btn = QPushButton("Search", self)
        self.search_btn.clicked.connect(self._trigger_search_immediate)

        # Row 1: filters
        filters = QHBoxLayout()
        self.chk_exact = QCheckBox("Exact", self)
        self.chk_fuzzy = QCheckBox("Fuzzy", self)
        self.chk_semantic = QCheckBox("Semantic", self)
        self.chk_exact.setChecked(True)
        self.chk_fuzzy.setChecked(True)
        self.chk_semantic.setChecked(True)
        for w in (self.chk_exact, self.chk_fuzzy, self.chk_semantic):
            filters.addWidget(w)

        # Row 2: results list and topic tree side-by-side
        self.results = QListWidget(self)
        self.results.itemActivated.connect(self._on_item_activated)
        self.topic_tree = QTreeWidget(self)
        self.topic_tree.setHeaderLabels(["Topics"]) 
        # stub example topics
        root = QTreeWidgetItem(["All Topics"])
        self.topic_tree.addTopLevelItem(root)

        grid.addWidget(QLabel("Query:"), 0, 0)
        grid.addWidget(self.query_edit, 0, 1)
        grid.addWidget(self.search_btn, 0, 2)
        grid.addLayout(filters, 1, 0, 1, 3)
        grid.addWidget(self.results, 2, 0, 1, 2)
        grid.addWidget(self.topic_tree, 2, 2)

    def _wire_debounce(self) -> None:
        self._timer = QTimer(self)
        self._timer.setInterval(self._debounce_ms)
        self._timer.setSingleShot(True)
        self.query_edit.textEdited.connect(lambda _t: self._timer.start())
        self._timer.timeout.connect(self._trigger_search)

    # ---- Search trigger ----
    def _trigger_search_immediate(self) -> None:
        self._timer.stop()
        self._trigger_search()

    def _trigger_search(self) -> None:
        text = self.query_edit.text().strip()
        if not text:
            self.results.clear()
            return
        # Build task and invoke worker in thread
        task = SearchTask(query=text, limit=25)
        QTimer.singleShot(0, lambda: self._worker.run(task))

    # ---- Results handling ----
    def _on_results_ready(self, res: list) -> None:  # list[SearchResult]
        self.results.clear()
        for r in res:
            item = QListWidgetItem(f"{r.document_title} — {r.snippet}")
            item.setData(256, (r.document_id, r.page_number))  # Qt.UserRole
            self.results.addItem(item)

    def _on_item_activated(self, item: QListWidgetItem) -> None:
        data = item.data(256)  # Qt.UserRole
        if not data:
            return
        doc_id, page = data
        self.result_selected.emit(doc_id, page)
        self._event_bus.publish(SearchResultSelected(document_id=doc_id, page_number=page, query=self.query_edit.text()))

    def closeEvent(self, event) -> None:  # noqa: N802
        self._thread.quit()
        self._thread.wait(1500)
        super().closeEvent(event)

