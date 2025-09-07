from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable, Iterable, List, Optional, Sequence, Tuple

from src.core.models.configuration import ApplicationConfig
from src.core.models.search import MatchType, SearchResult


CandidateProvider = Callable[[str, int], Sequence[Tuple[str, str]]]
# Returns sequence of (document_id, text) candidates for fuzzy/semantic search


@dataclass(slots=True)
class SearchRankWeights:
    exact: float = 1.0
    fuzzy: float = 0.7
    semantic: float = 0.9


class SearchManager:
    """Combines exact (Elasticsearch), fuzzy (rapidfuzz), and semantic (embeddings).

    - Exact: uses Elasticsearch client if provided (lazy import otherwise).
    - Fuzzy: uses `rapidfuzz.fuzz.ratio` over candidate texts from provider.
    - Semantic: uses sentence-transformers embeddings and cosine similarity.
    """

    def __init__(
        self,
        config: Optional[ApplicationConfig] = None,
        es_client: Optional[Any] = None,
        candidate_provider: Optional[CandidateProvider] = None,
        weights: Optional[SearchRankWeights] = None,
        cache_ttl_seconds: float = 0.0,
    ) -> None:
        self._cfg = config or ApplicationConfig()
        self._es = es_client
        self._provider = candidate_provider or (lambda q, n: ())
        self._weights = weights or SearchRankWeights()
        self._model: Optional[Any] = None
        self._ttl = max(0.0, float(cache_ttl_seconds))
        self._cache: dict[tuple[str, int, Optional[str]], tuple[float, List[SearchResult]]] = {}

    # ---- Public API ----
    def search(self, query: str, limit: int = 10, topic_filter: Optional[str] = None) -> List[SearchResult]:
        key = (query, int(limit), topic_filter)
        now = time.time()
        if self._ttl > 0:
            hit = self._cache.get(key)
            if hit and now - hit[0] <= self._ttl:
                return hit[1]
        parts: List[SearchResult] = []

        # Exact via ES
        parts.extend(self._search_exact(query, limit, topic_filter=topic_filter))

        # Fuzzy
        if self._cfg.search_settings.enable_spelling_correction:
            parts.extend(self._search_fuzzy(query, limit))

        # Semantic
        if self._cfg.search_settings.enable_ai_search:
            parts.extend(self._search_semantic(query, limit))

        # Merge by (document_id, page) keeping highest score
        merged: dict[tuple[str, int], SearchResult] = {}
        for r in parts:
            key = (r.document_id, r.page_number)
            if key not in merged or r.relevance_score > merged[key].relevance_score:
                merged[key] = r

        # Sort by score desc and trim
        results = sorted(merged.values(), key=lambda r: r.relevance_score, reverse=True)
        results = results[:limit]
        if self._ttl > 0:
            self._cache[key] = (now, results)
        return results

    def suggest(self, prefix: str, limit: int = 5) -> List[str]:
        """Return simple auto-complete terms derived from provider texts."""
        if not prefix:
            return []
        prefix_low = prefix.lower()
        seen: dict[str, int] = {}
        for _doc, text in self._provider(prefix, limit * 10):
            for tok in text.split():
                if tok.lower().startswith(prefix_low):
                    seen[tok] = seen.get(tok, 0) + 1
        # sort by frequency desc, then lexicographically
        return [w for w, _ in sorted(seen.items(), key=lambda kv: (-kv[1], kv[0]))][:limit]

    # ---- Exact ----
    def _search_exact(self, query: str, limit: int, topic_filter: Optional[str] = None) -> List[SearchResult]:
        es = self._get_es()
        if es is None:
            return []
        try:
            q: dict[str, Any] = {"multi_match": {"query": query, "fields": ["title^2", "content"]}}
            if topic_filter:
                q = {"bool": {"must": [q], "filter": [{"term": {"metadata.topic_path.keyword": topic_filter}}]}}
            resp = es.search(  # type: ignore[attr-defined]
                index="documents",
                size=limit,
                query=q,
                highlight={"fields": {"content": {}}},
            )
        except Exception:
            return []

        out: List[SearchResult] = []
        for hit in resp.get("hits", {}).get("hits", []):
            src = hit.get("_source", {})
            title = src.get("title", "")
            doc_id = hit.get("_id", src.get("file_path", title))
            score = float(hit.get("_score", 0.0))
            highlight_list = hit.get("highlight", {}).get("content", [])
            snippet = highlight_list[0] if highlight_list else src.get("content", "")[:200]
            out.append(
                SearchResult(
                    document_id=str(doc_id),
                    document_title=title,
                    page_number=0,
                    snippet=snippet,
                    relevance_score=min(1.0, score / 10.0) * self._weights.exact,  # normalize
                    match_type=MatchType.EXACT,
                    highlighted_text=snippet,
                )
            )
        return out

    # ---- Fuzzy ----
    def _search_fuzzy(self, query: str, limit: int) -> List[SearchResult]:
        try:
            from rapidfuzz import fuzz  # type: ignore
        except Exception:
            return []

        results: List[SearchResult] = []
        for doc_id, text in self._provider(query, limit * 3):
            score = float(fuzz.ratio(query, text)) / 100.0
            if score >= self._cfg.search_settings.fuzzy_accuracy_target:
                snippet = text[:200]
                results.append(
                    SearchResult(
                        document_id=str(doc_id),
                        document_title=str(doc_id),
                        page_number=0,
                        snippet=snippet,
                        relevance_score=score * self._weights.fuzzy,
                        match_type=MatchType.FUZZY,
                        highlighted_text=snippet,
                    )
                )
        return results[:limit]

    # ---- Semantic ----
    def _search_semantic(self, query: str, limit: int) -> List[SearchResult]:
        model = self._get_model()
        if model is None:
            return []
        # Encode query once
        q_vec = model.encode([query], normalize_embeddings=True)[0]
        q_vec = [float(x) for x in q_vec]

        results: List[SearchResult] = []
        for doc_id, text in self._provider(query, limit * 3):
            doc_vec = model.encode([text], normalize_embeddings=True)[0]
            doc_vec = [float(x) for x in doc_vec]
            sim = self._cosine(q_vec, doc_vec)
            if sim >= self._cfg.search_settings.semantic_similarity_threshold:
                snippet = text[:200]
                results.append(
                    SearchResult(
                        document_id=str(doc_id),
                        document_title=str(doc_id),
                        page_number=0,
                        snippet=snippet,
                        relevance_score=sim * self._weights.semantic,
                        match_type=MatchType.SEMANTIC,
                        highlighted_text=snippet,
                    )
                )
        return results[:limit]

    @staticmethod
    def _cosine(a: Sequence[float], b: Sequence[float]) -> float:
        import math

        num = sum(x * y for x, y in zip(a, b))
        da = math.sqrt(sum(x * x for x in a))
        db = math.sqrt(sum(y * y for y in b))
        if da == 0 or db == 0:
            return 0.0
        return float(num / (da * db))

    # ---- Lazy deps ----
    def _get_es(self) -> Optional[Any]:
        if self._es is not None:
            return self._es
        try:
            from elasticsearch import Elasticsearch  # type: ignore

            self._es = Elasticsearch("http://localhost:9200")  # type: ignore[call-arg]
            return self._es
        except Exception:
            return None

    def _get_model(self) -> Optional[Any]:
        if self._model is not None:
            return self._model
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore

            self._model = SentenceTransformer("all-MiniLM-L6-v2")
            return self._model
        except Exception:
            return None
