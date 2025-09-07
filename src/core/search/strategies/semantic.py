from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Callable, Iterable, List, Optional, Sequence, Tuple

from src.core.models.configuration import ApplicationConfig, SearchSettings
from src.core.performance.numba_ops import cosine_similarity_numba


CandidateProvider = Callable[[str, int], Sequence[Tuple[str, str]]]


@dataclass(slots=True)
class SemanticConfig:
    model_name: str = "all-MiniLM-L6-v2"
    threshold: float = 0.7
    cache_size: int = 1000


class EmbeddingCache:
    def __init__(self, max_size: int = 1000) -> None:
        self._max = max(1, int(max_size))
        self._store: "OrderedDict[str, List[float]]" = OrderedDict()

    def get(self, key: str) -> Optional[List[float]]:
        vec = self._store.get(key)
        if vec is not None:
            self._store.move_to_end(key)
        return vec

    def put(self, key: str, vec: List[float]) -> None:
        if key in self._store:
            self._store.move_to_end(key)
        self._store[key] = vec
        if len(self._store) > self._max:
            self._store.popitem(last=False)


class SemanticSearchStrategy:
    """Semantic search using sentence-transformers with GPU/CPU fallback and caching (req 1.2, 4.1)."""

    def __init__(
        self,
        app_config: Optional[ApplicationConfig] = None,
        candidate_provider: Optional[CandidateProvider] = None,
        sem_config: Optional[SemanticConfig] = None,
        embedding_cache: Optional[EmbeddingCache] = None,
        model: Optional[Any] = None,
    ) -> None:
        self._settings: SearchSettings = (app_config.search_settings if app_config else SearchSettings())
        self._conf = sem_config or SemanticConfig(threshold=self._settings.semantic_similarity_threshold)
        self._provider = candidate_provider or (lambda q, n: ())
        self._cache = embedding_cache or EmbeddingCache(self._conf.cache_size)
        self._model = model  # allow injection for tests
        self._device = self._detect_device()

    # ---------- Public API ----------
    def search(self, query: str, limit: int = 10) -> List[Tuple[str, float, str]]:
        if not self._settings.enable_ai_search:
            return []
        cands = list(self._provider(query, limit * 3))
        if not cands:
            return []
        # If configured to use only pre-encoded, we cannot process raw text here
        if self._settings.fallback_to_preencoded_only:
            return []

        q_vec = self._embed_text(query)
        out: List[Tuple[str, float, str]] = []
        for doc_id, text in cands:
            d_vec = self._embed_text(text)
            sim = float(cosine_similarity_numba(q_vec, d_vec))
            if sim >= self._conf.threshold:
                out.append((doc_id, sim, text))
        out.sort(key=lambda x: x[1], reverse=True)
        return out[:limit]

    def encode_texts(self, texts: Sequence[str]) -> List[List[float]]:
        model = self._get_model()
        vecs = model.encode(list(texts), normalize_embeddings=True, device=self._device)
        return [list(map(float, v)) for v in vecs]

    # ---------- Embedding helpers ----------
    def _embed_text(self, text: str) -> List[float]:
        cached = self._cache.get(text)
        if cached is not None:
            return cached
        vec = self.encode_texts([text])[0]
        self._cache.put(text, vec)
        return vec

    # ---------- Device/model ----------
    @staticmethod
    def _detect_device() -> str:
        try:
            import torch  # type: ignore

            return "cuda" if getattr(torch.cuda, "is_available", lambda: False)() else "cpu"
        except Exception:
            return "cpu"

    def _get_model(self) -> Any:
        if self._model is not None:
            return self._model
        from sentence_transformers import SentenceTransformer  # type: ignore

        self._model = SentenceTransformer(self._conf.model_name)
        return self._model

