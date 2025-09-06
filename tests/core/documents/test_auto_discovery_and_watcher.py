from __future__ import annotations

import time
from pathlib import Path
from typing import List

from src.core.documents import DocumentManager, FileWatcher


def test_auto_register_builtin_registers_suffixes() -> None:
    mgr = DocumentManager()
    mgr.auto_register_builtin()
    # At least these should be present regardless of optional libs
    assert ".pdf" in mgr.registered_suffixes
    assert ".txt" in mgr.registered_suffixes
    assert ".md" in mgr.registered_suffixes


def test_file_watcher_detects_new_supported_file(tmp_path: Path) -> None:
    mgr = DocumentManager()
    mgr.auto_register_builtin()
    watcher = FileWatcher(mgr, interval_sec=0.1)
    watcher.add_directory(tmp_path)

    seen: List[Path] = []

    watcher.start(lambda p: seen.append(p))

    # Create a supported file
    f = tmp_path / "new_note.md"
    f.write_text("hello", encoding="utf-8")

    timeout = time.time() + 3
    while not seen and time.time() < timeout:
        time.sleep(0.05)

    watcher.stop()
    assert seen and seen[0].name == "new_note.md"

