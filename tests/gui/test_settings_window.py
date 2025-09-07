from __future__ import annotations

import json
from pathlib import Path

import pytest

PyQt6 = pytest.importorskip("PyQt6")

from src.core.config import ConfigurationManager
from src.gui.settings_window import SettingsWindow


def test_settings_persist_changes(qtbot, tmp_path: Path):
    cfg_path = tmp_path / "settings.json"
    # Ensure file exists with defaults
    mgr = ConfigurationManager(config_path=cfg_path)
    mgr.save(mgr.load())

    win = SettingsWindow(mgr)
    qtbot.addWidget(win)
    win.show()

    # Wait briefly for async load
    qtbot.wait(50)

    # Change a couple settings
    win.chk_semantic.setChecked(False)
    win.spin_sem_thresh.setValue(0.55)
    win.btn_save.click()

    # Read back from disk
    loaded = mgr.load()
    assert loaded.search_settings.enable_ai_search is False
    assert loaded.search_settings.semantic_similarity_threshold == 0.55

