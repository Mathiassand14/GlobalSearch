from __future__ import annotations

from pathlib import Path

import pytest

PyQt6 = pytest.importorskip("PyQt6")
from PyQt6.QtWidgets import QFileDialog

from src.core.config import ConfigurationManager
from src.gui.file_manager_window import FileManagerWindow


def test_add_directory_updates_config(qtbot, tmp_path: Path, monkeypatch):
    cfg_path = tmp_path / "settings.json"
    mgr = ConfigurationManager(config_path=cfg_path)
    mgr.save(mgr.load())

    win = FileManagerWindow(mgr)
    qtbot.addWidget(win)
    win.show()

    # Mock QFileDialog to return tmp_path
    monkeypatch.setattr(QFileDialog, "getExistingDirectory", staticmethod(lambda *a, **k: str(tmp_path)))
    win.btn_add.click()

    # Reload and check
    cfg = mgr.load()
    assert str(tmp_path) in cfg.document_directories
    assert win.list.count() >= 1

