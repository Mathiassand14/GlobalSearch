from __future__ import annotations

from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal


class TextLoadWorker(QObject):
    loaded = pyqtSignal(str)
    error = pyqtSignal(str)

    def load(self, file_path: str) -> None:
        try:
            p = Path(file_path)
            # Try common encodings
            for enc in ("utf-8", "utf-8-sig", "latin-1"):
                try:
                    content = p.read_text(encoding=enc)
                    self.loaded.emit(content)
                    return
                except UnicodeDecodeError:
                    continue
            # Fallback with replacement
            content = p.read_bytes().decode("utf-8", errors="replace")
            self.loaded.emit(content)
        except Exception as exc:  # pragma: no cover - defensive
            self.error.emit(str(exc))

