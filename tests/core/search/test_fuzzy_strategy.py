from __future__ import annotations

from typing import Sequence

from src.core.models.configuration import ApplicationConfig, SearchSettings
from src.core.search.strategies import FuzzySearchStrategy


def _corpus() -> Sequence[str]:
    return ["introduction", "hello world", "banana bread", "elasticsearch"]


def test_build_query_contains_fuzziness():
    strat = FuzzySearchStrategy()
    q = strat.build_query("helo wrld")
    assert q["multi_match"]["fuzziness"] in ("AUTO", 1, 2)
    assert "fields" in q["multi_match"]


def test_suggestions_with_threshold(monkeypatch):
    cfg = ApplicationConfig(search_settings=SearchSettings(fuzzy_accuracy_target=0.6))
    strat = FuzzySearchStrategy(app_config=cfg, corpus_provider=_corpus)

    # Monkeypatch rapidfuzz process.extract to deterministic behavior
    class _Process:
        @staticmethod
        def extract(q, corpus, scorer=None, limit=5):  # noqa: ANN001
            # rank hello world high, others low
            out = []
            for i, c in enumerate(corpus):
                score = 90 if c == "hello world" else 20
                out.append((c, score, i))
            return out[:limit]

    class _Fuzz:
        @staticmethod
        def ratio(a, b):  # noqa: ANN001
            return 90 if b == "hello world" else 20

    import types as _types

    monkeypatch.setitem(__import__("sys").modules, "rapidfuzz", _types.SimpleNamespace(process=_Process, fuzz=_Fuzz))

    suggestions = strat.suggest("helo world", limit=3)
    assert suggestions and suggestions[0][0] == "hello world" and suggestions[0][1] >= 0.6


def test_search_invokes_es_with_fuzzy_query():
    class _FakeES:
        def __init__(self) -> None:
            self.calls = []

        def search(self, index: str, **body):  # noqa: ANN001
            self.calls.append((index, body))
            return {"ok": True}

    strat = FuzzySearchStrategy()
    es = _FakeES()
    res = strat.search(es, index="documents", text="helo wrld", size=7)
    assert res["ok"] is True
    assert es.calls and es.calls[0][0] == "documents"
    body = es.calls[0][1]
    assert body["size"] == 7
    assert "fuzziness" in body["query"]["multi_match"]

