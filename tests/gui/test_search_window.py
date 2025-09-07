from __future__ import annotations

import typing as t

import pytest

PyQt6 = pytest.importorskip("PyQt6")
from PyQt6.QtCore import Qt

from src.core.models.search import MatchType, SearchResult
from src.gui import SearchWindow


def _fake_search(query: str, limit: int, topic_filter: str | None = None) -> list[SearchResult]:
    return [
        SearchResult(
            document_id="1",
            document_title="Doc1",
            page_number=0,
            snippet=f"hit: {query}",
            relevance_score=0.9,
            match_type=MatchType.EXACT,
            highlighted_text=f"hit: {query}",
        )
    ]


def test_debounced_search_populates_results(qtbot):
    win = SearchWindow(search_fn=_fake_search, debounce_ms=50)
    qtbot.addWidget(win)
    win.show()

    qtbot.keyClicks(win.query_edit, "test")
    qtbot.wait(100)  # allow debounce to fire and worker to run

    assert win.results.count() == 1
    item = win.results.item(0)
    assert "hit: test" in item.text()


def test_sorting_changes_order(qtbot):
    # Custom search returns two items in reverse order of name
    def _two(query: str, limit: int, topic_filter: str | None = None):
        return [
            SearchResult(
                document_id="1",
                document_title="Zeta",
                page_number=0,
                snippet="",
                relevance_score=0.5,
                match_type=MatchType.EXACT,
                highlighted_text="",
            ),
            SearchResult(
                document_id="2",
                document_title="Alpha",
                page_number=0,
                snippet="",
                relevance_score=0.9,
                match_type=MatchType.EXACT,
                highlighted_text="",
            ),
        ]

    win = SearchWindow(search_fn=_two, debounce_ms=10)
    qtbot.addWidget(win)
    win.show()
    win.query_edit.setText("x")
    win._trigger_search()
    qtbot.wait(50)

    # Default relevance: first should be Alpha (0.9)
    assert win.results.item(0).text().startswith("[0.90] Alpha")
    win.sort_combo.setCurrentText("Name")
    qtbot.wait(10)
    assert win.results.item(0).text().startswith("[0.50] Zeta")
