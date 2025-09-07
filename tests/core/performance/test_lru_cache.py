from __future__ import annotations

from src.core.performance.lru_cache import LRUCache


def test_lru_cache_evicts_oldest():
    c = LRUCache[str, int](capacity=2)
    c.put("a", 1)
    c.put("b", 2)
    # Access 'a' to make it most recent
    assert c.get("a") == 1
    # Insert 'c' should evict 'b'
    c.put("c", 3)
    assert c.get("b") is None
    assert c.get("a") == 1
    assert c.get("c") == 3

