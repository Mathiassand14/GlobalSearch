from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Callable, Iterable, Optional, Set

from src.core.documents.manager import DocumentManager


class FileWatcher:
    """Simple polling-based file watcher using pathlib for portability.

    Notifies a callback when new files are detected under watched directories
    that are supported by the provided DocumentManager.
    """

    def __init__(self, manager: DocumentManager, interval_sec: float = 1.0) -> None:
        self._manager = manager
        self._interval = max(0.1, float(interval_sec))
        self._dirs: Set[Path] = set()
        self._seen: Set[Path] = set()
        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()

    def add_directory(self, directory: Path) -> None:
        self._dirs.add(directory)

    def start(self, on_created: Callable[[Path], None]) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()

        def _run() -> None:
            while not self._stop.is_set():
                try:
                    for d in list(self._dirs):
                        for p in self._iter_files(d):
                            if p not in self._seen and self._manager.get_processor_for(p) is not None:
                                self._seen.add(p)
                                try:
                                    on_created(p)
                                except Exception:
                                    # Callback exceptions are swallowed to keep watcher alive
                                    pass
                except Exception:
                    pass
                time.sleep(self._interval)

        self._thread = threading.Thread(target=_run, name="file-watcher", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
            self._thread = None

    @staticmethod
    def _iter_files(directory: Path) -> Iterable[Path]:
        if not directory.exists():
            return []
        return (p for p in directory.rglob("*") if p.is_file())

