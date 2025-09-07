from __future__ import annotations

from typing import Callable, List, Optional

from PyQt6.QtCore import QThread, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
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
        self._current_topic: Optional[str] = None
        self._last_results: List[SearchResult] = []

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
        self.loading_lbl = QLabel("")
        self.loading_lbl.setStyleSheet("color: gray;")

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
        self.topic_tree.itemSelectionChanged.connect(self._on_topic_changed)

        # Sorting controls
        self.sort_combo = QComboBox(self)
        self.sort_combo.addItems(["Relevance", "Name"])  # Date omitted due to data constraints
        self.sort_combo.currentTextChanged.connect(self._apply_sort)

        grid.addWidget(QLabel("Query:"), 0, 0)
        grid.addWidget(self.query_edit, 0, 1)
        grid.addWidget(self.search_btn, 0, 2)
        grid.addWidget(self.loading_lbl, 0, 3)
        grid.addLayout(filters, 1, 0, 1, 3)
        grid.addWidget(QLabel("Sort:"), 1, 3)
        grid.addWidget(self.sort_combo, 1, 4)
        grid.addWidget(self.results, 2, 0, 1, 3)
        grid.addWidget(self.topic_tree, 2, 3, 1, 2)

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
        task = SearchTask(query=text, limit=25, topic_filter=self._current_topic)
        self.loading_lbl.setText("Searching…")
        QTimer.singleShot(0, lambda: self._worker.run(task))

    # ---- Results handling ----
    def _on_results_ready(self, res: list) -> None:  # list[SearchResult]
        self._last_results = list(res)
        self._apply_sort()
        self.loading_lbl.setText("")

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

    # ---- Sorting and topics ----
    def _apply_sort(self) -> None:
        self.results.clear()
        items = list(self._last_results)
        mode = self.sort_combo.currentText() if hasattr(self, "sort_combo") else "Relevance"
        if mode == "Name":
            items.sort(key=lambda r: (r.document_title or ""))
        else:
            items.sort(key=lambda r: r.relevance_score, reverse=True)
        for r in items:
            score = f"[{r.relevance_score:.2f}]"
            item = QListWidgetItem(f"{score} {r.document_title} — {r.snippet}")
            item.setData(256, (r.document_id, r.page_number))
            self.results.addItem(item)

    def _on_topic_changed(self) -> None:
        sel = self.topic_tree.selectedItems()
        if not sel:
            self._current_topic = None
        else:
            # Build path from ancestry, skip root 'All Topics'
            node = sel[0]
            parts: List[str] = []
            while node and node.parent() is not None:
                parts.insert(0, node.text(0))
                node = node.parent()
            self._current_topic = "/".join(parts) if parts else None
        # Re-run search if a query is present
        if self.query_edit.text().strip():
            self._trigger_search()
