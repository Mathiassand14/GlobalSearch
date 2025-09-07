from __future__ import annotations

import threading
from typing import List

from src.core.events import EventBus, IndexingProgress, SearchResultSelected, WindowClosed


def test_subscribe_publish_unsubscribe() -> None:
    bus = EventBus()
    seen: List[str] = []

    def on_selected(ev: SearchResultSelected) -> None:
        seen.append(f"{ev.document_id}:{ev.page_number}")

    bus.subscribe(SearchResultSelected, on_selected)
    bus.publish(SearchResultSelected(document_id="d1", page_number=2, query="x"))
    assert seen == ["d1:2"]

    bus.unsubscribe(SearchResultSelected, on_selected)
    bus.publish(SearchResultSelected(document_id="d2", page_number=0, query="x"))
    assert seen == ["d1:2"]  # unchanged


def test_thread_safety_publish_from_multiple_threads() -> None:
    bus = EventBus()
    count = 0
    lock = threading.Lock()

    def on_progress(ev: IndexingProgress) -> None:
        nonlocal count
        with lock:
            count += 1

    bus.subscribe(IndexingProgress, on_progress)

    threads = []
    for _ in range(10):
        t = threading.Thread(target=lambda: bus.publish(IndexingProgress(total=10, processed=1)))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    assert count == 10


def test_different_event_types_do_not_interfere() -> None:
    bus = EventBus()
    seen = []

    def on_close(ev: WindowClosed) -> None:
        seen.append(ev.window_name)

    bus.subscribe(WindowClosed, on_close)
    bus.publish(WindowClosed(window_name="search"))
    bus.publish(SearchResultSelected(document_id="x", page_number=1, query="q"))
    assert seen == ["search"]

