from __future__ import annotations

from typing import Any, List, Sequence, Tuple

from src.core.models.configuration import ApplicationConfig, SearchSettings
from src.core.models.search import MatchType
from src.core.search import SearchManager


def _provider_from_texts(items: Sequence[Tuple[str, str]]):
    def _prov(query: str, limit: int):  # noqa: ANN001
        return items[:limit]

    return _prov


class _FakeES:
    def search(self, index: str, size: int, query: dict, highlight: dict) -> dict:  # noqa: ANN001
        return {
            "hits": {
                "hits": [
                    {
                        "_id": "1",
                        "_score": 2.0,
                        "_source": {"title": "Doc ES", "content": "lorem ipsum"},
                        "highlight": {"content": ["<em>lorem</em> ipsum"]},
                    }
                ]
            }
        }


class _FakeModel:
    def encode(self, texts: list[str], normalize_embeddings: bool = True):  # noqa: ANN001
        # Simple deterministic vectors: len(text) repeated
        return [[float(len(texts[0]))] * 4]


def test_exact_search_via_es():
    sm = SearchManager(config=ApplicationConfig(), es_client=_FakeES(), candidate_provider=_provider_from_texts([]))
    out = sm.search("lorem", limit=5)
    assert out and out[0].match_type == MatchType.EXACT
    assert "<em>lorem</em>" in out[0].highlighted_text


def test_fuzzy_search_filters_by_threshold(monkeypatch):
    cfg = ApplicationConfig(search_settings=SearchSettings(fuzzy_accuracy_target=0.5))
    items = [("D1", "helo world"), ("D2", "unrelated text")]
    sm = SearchManager(config=cfg, candidate_provider=_provider_from_texts(items))
    # Provide a fake rapidfuzz implementation
    class _Fuzz:
        @staticmethod
        def ratio(a: str, b: str) -> int:
            return 90 if "helo world" in b else 10

    import types as _types

    monkeypatch.setitem(__import__("sys").modules, "rapidfuzz", _types.SimpleNamespace(fuzz=_Fuzz))
    out = sm.search("hello world", limit=5)
    assert any(r.match_type == MatchType.FUZZY and r.document_id == "D1" for r in out)


def test_semantic_search_uses_model(monkeypatch):
    cfg = ApplicationConfig(search_settings=SearchSettings(semantic_similarity_threshold=0.0))
    sm = SearchManager(config=cfg, candidate_provider=_provider_from_texts([("D3", "semantic candidate")]))
    sm._model = _FakeModel()  # type: ignore[attr-defined]
    out = sm.search("x", limit=5)
    assert any(r.match_type == MatchType.SEMANTIC and r.document_id == "D3" for r in out)
