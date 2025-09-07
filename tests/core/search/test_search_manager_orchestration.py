from __future__ import annotations

import time

from src.core.models.configuration import ApplicationConfig, SearchSettings
from src.core.search import SearchManager


class _FakeES:
    def __init__(self) -> None:
        self.calls = 0

    def search(self, index: str, size: int, query: dict, highlight: dict):  # noqa: ANN001
        self.calls += 1
        return {"hits": {"hits": []}}


def _provider(q: str, n: int):  # noqa: ANN001
    return [("D1", "hello world"), ("D2", "help docs"), ("D3", "helium atom")]


def test_ttl_cache_returns_cached_results():
    cfg = ApplicationConfig(search_settings=SearchSettings(enable_spelling_correction=False, enable_ai_search=False))
    es = _FakeES()
    sm = SearchManager(config=cfg, es_client=es, candidate_provider=_provider, cache_ttl_seconds=1.0)
    sm.search("hello", limit=5)
    first = es.calls
    sm.search("hello", limit=5)
    assert es.calls == first  # cached


def test_autocomplete_from_provider():
    cfg = ApplicationConfig()
    sm = SearchManager(config=cfg, candidate_provider=_provider)
    sugg = sm.suggest("he", limit=3)
    # Expect tokens starting with 'he' ordered by frequency
    assert sugg and sugg[0].lower().startswith("he")

