from __future__ import annotations

from collections import OrderedDict
from typing import Generic, Iterable, Iterator, MutableMapping, Optional, Tuple, TypeVar


K = TypeVar("K")
V = TypeVar("V")


class LRUCache(Generic[K, V]):
    """Simple LRU cache with fixed capacity and O(1) operations.

    Evicts the least-recently-used item when capacity is exceeded.
    """

    def __init__(self, capacity: int = 50) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be > 0")
        self._cap = int(capacity)
        self._data: "OrderedDict[K, V]" = OrderedDict()

    def __contains__(self, key: K) -> bool:  # pragma: no cover - trivial
        return key in self._data

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self._data)

    def get(self, key: K) -> Optional[V]:
        val = self._data.get(key)
        if val is not None:
            self._data.move_to_end(key)
        return val

    def put(self, key: K, value: V) -> None:
        if key in self._data:
            self._data.move_to_end(key)
        self._data[key] = value
        if len(self._data) > self._cap:
            self._data.popitem(last=False)

    def items(self) -> Iterator[Tuple[K, V]]:  # pragma: no cover - utility
        return iter(self._data.items())

    def clear(self) -> None:  # pragma: no cover - utility
        self._data.clear()

