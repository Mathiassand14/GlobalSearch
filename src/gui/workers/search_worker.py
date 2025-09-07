from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List

from PyQt6.QtCore import QObject, pyqtSignal

from src.core.models.search import SearchResult


SearchFn = Callable[..., List[SearchResult]]


@dataclass(slots=True)
class SearchTask:
    query: str
    limit: int
    topic_filter: str | None = None


class SearchWorker(QObject):
    """Runs search function in a thread and emits results."""

    results_ready = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, search_fn: SearchFn) -> None:
        super().__init__()
        self._search_fn = search_fn

    def run(self, task: SearchTask) -> None:
        try:
            try:
                out = self._search_fn(task.query, task.limit, task.topic_filter)
            except TypeError:
                out = self._search_fn(task.query, task.limit)
            self.results_ready.emit(out)
        except Exception as exc:  # pragma: no cover - defensive
            self.error.emit(str(exc))
