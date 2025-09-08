from __future__ import annotations

from pathlib import Path

import pytest

PyQt6 = pytest.importorskip("PyQt6")

from PyQt6.QtCore import QThread

from src.gui.workers.indexing_worker import IndexingWorker


def test_indexing_worker_emits_progress(qtbot, tmp_path: Path):
    # Create sample files
    for i in range(3):
        (tmp_path / f"f{i}.txt").write_text("hello", encoding="utf-8")

    w = IndexingWorker()
    t = QThread()
    w.moveToThread(t)
    t.start()

    seen = {"progress": 0, "done": False}

    def on_prog(total, processed, failed, current_file):  # noqa: ANN001
        seen["progress"] += 1

    def on_done(total, processed, failed):  # noqa: ANN001
        seen["done"] = True

    w.progress.connect(on_prog)
    w.completed.connect(on_done)

    w.index_directories([tmp_path])
    qtbot.wait(10)
    t.quit(); t.wait(100)

    assert seen["progress"] >= 3
    assert seen["done"] is True

