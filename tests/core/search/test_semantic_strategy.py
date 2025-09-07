from __future__ import annotations

from typing import Sequence, Tuple

from src.core.models.configuration import ApplicationConfig, SearchSettings
from src.core.search.strategies.semantic import EmbeddingCache, SemanticSearchStrategy, SemanticConfig


def _prov():
    return [("D1", "alpha beta"), ("D2", "gamma delta"), ("D3", "alpha gamma")]


class _FakeModel:
    def __init__(self) -> None:
        self.calls = 0

    def encode(self, texts, normalize_embeddings=True, device="cpu"):  # noqa: ANN001
        self.calls += 1
        # deterministic vectors based on length
        return [[float(len(t))] * 4 for t in texts]


def test_semantic_search_scores_and_sorts(monkeypatch) -> None:
    cfg = ApplicationConfig(search_settings=SearchSettings(semantic_similarity_threshold=0.0))
    strat = SemanticSearchStrategy(app_config=cfg, candidate_provider=lambda q, n: _prov(), model=_FakeModel())
    out = strat.search("alpha", limit=2)
    ids = [doc_id for doc_id, _score, _text in out]
    assert ids and len(ids) == 2


def test_cache_avoids_recompute() -> None:
    cfg = ApplicationConfig(search_settings=SearchSettings(semantic_similarity_threshold=0.0))
    model = _FakeModel()
    strat = SemanticSearchStrategy(app_config=cfg, candidate_provider=lambda q, n: [("D1", "x")], model=model)
    # First call encodes twice (query + doc)
    strat.search("x", limit=1)
    calls_first = model.calls
    # Second call should hit cache for both
    strat.search("x", limit=1)
    assert model.calls == calls_first  # no extra encodes


def test_device_detection_cpu(monkeypatch) -> None:
    class _Cuda:
        @staticmethod
        def is_available():
            return False

    class _Torch:
        cuda = _Cuda()

    monkeypatch.setitem(__import__("sys").modules, "torch", _Torch())
    s = SemanticSearchStrategy()
    assert s._detect_device() == "cpu"

