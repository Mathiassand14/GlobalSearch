from __future__ import annotations

import threading
from collections import defaultdict
from typing import Callable, DefaultDict, Dict, List, Type, TypeVar

from src.core.events.events import AppEvent


E = TypeVar("E", bound=AppEvent)
Subscriber = Callable[[E], None]


class EventBus:
    """Thread-safe pub/sub bus for core events (req 3.2, 3.3, 3.5)."""

    def __init__(self) -> None:
        self._subs: DefaultDict[Type[AppEvent], List[Subscriber[Any]]] = defaultdict(list)
        self._lock = threading.RLock()

    def subscribe(self, event_type: Type[E], handler: Subscriber[E]) -> None:
        with self._lock:
            self._subs[event_type].append(handler)  # type: ignore[arg-type]

    def unsubscribe(self, event_type: Type[E], handler: Subscriber[E]) -> None:
        with self._lock:
            handlers = self._subs.get(event_type)
            if not handlers:
                return
            try:
                handlers.remove(handler)  # type: ignore[arg-type]
            except ValueError:
                pass
            if not handlers:
                self._subs.pop(event_type, None)

    def publish(self, event: E) -> None:
        # Copy handlers snapshot to avoid holding lock during callbacks
        with self._lock:
            handlers = list(self._subs.get(type(event), ()))

        for h in handlers:
            try:
                h(event)  # type: ignore[misc]
            except Exception:
                # Swallow exceptions to keep bus healthy; GUI/log layer can wrap this
                continue

