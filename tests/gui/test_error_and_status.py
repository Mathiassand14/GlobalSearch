from __future__ import annotations

import pytest

PyQt6 = pytest.importorskip("PyQt6")

from src.gui.widgets.status_bar import StatusLabel


def test_status_label_states(qtbot):
    s = StatusLabel()
    qtbot.addWidget(s)
    s.set_ok("OK")
    assert "OK" in s.text()
    s.set_warn("WARN")
    assert "WARN" in s.text()
    s.set_error("ERR")
    assert "ERR" in s.text()

