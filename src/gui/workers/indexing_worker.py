from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

from PyQt6.QtCore import QObject, pyqtSignal

from src.core.documents import DocumentManager
from src.core.documents.models import DocumentContent, PageContent
from src.core.exceptions.exceptions import DocumentProcessingError


class IndexingWorker(QObject):
    progress = pyqtSignal(int, int, int, str)  # total, processed, failed, current_file
    completed = pyqtSignal(int, int, int)
    error = pyqtSignal(str)

    def __init__(self, manager: Optional[DocumentManager] = None) -> None:
        super().__init__()
        self._mgr = manager or DocumentManager()
        self._mgr.auto_register_builtin()

    def index_directories(self, directories: Iterable[Path]) -> None:
        total = 0
        processed = 0
        failed = 0
        files: list[Path] = []
        for d in directories:
            if d.exists():
                files.extend([p for p in d.rglob("*") if p.is_file()])
        total = len(files)
        for p in files:
            try:
                self.progress.emit(total, processed, failed, str(p))
                content = self._mgr.process(p)
                # Placeholder: potential indexing via IndexManager could be invoked here
                processed += 1
            except DocumentProcessingError:
                failed += 1
            except Exception as exc:  # pragma: no cover
                failed += 1
                self.error.emit(str(exc))
        self.completed.emit(total, processed, failed)

