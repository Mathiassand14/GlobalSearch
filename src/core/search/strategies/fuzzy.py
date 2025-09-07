from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable, List, Sequence, Tuple

from src.core.models.configuration import ApplicationConfig, SearchSettings


CorpusProvider = Callable[[], Sequence[str]]


@dataclass(slots=True)
class FuzzyConfig:
    fields: Tuple[str, ...] = ("title^2", "content")
    fuzziness: str | int = "AUTO"
    prefix_length: int = 0


class FuzzySearchStrategy:
    """Elasticsearch fuzzy search with rapidfuzz-based spelling suggestions (req 1.1, 1.4, 1.5)."""

    def __init__(
        self,
        app_config: ApplicationConfig | None = None,
        corpus_provider: CorpusProvider | None = None,
        fuzzy_config: FuzzyConfig | None = None,
    ) -> None:
        self._cfg = app_config.search_settings if app_config else SearchSettings()
        self._fuzzy = fuzzy_config or FuzzyConfig()
        self._corpus_provider = corpus_provider or (lambda: ())

    # ---------- ES query ----------
    def build_query(self, text: str) -> dict:
        return {
            "multi_match": {
                "query": text,
                "fields": list(self._fuzzy.fields),
                "fuzziness": self._fuzzy.fuzziness if self._fuzzy.fuzziness != "AUTO" else "AUTO",
                "prefix_length": int(self._fuzzy.prefix_length),
            }
        }

    def search(self, es_client: Any, index: str, text: str, size: int = 10) -> dict:
        body = {
            "size": int(size),
            "query": self.build_query(text),
            "highlight": {"fields": {"content": {}}},
        }
        return es_client.search(index=index, **body)

    # ---------- Suggestions ----------
    def suggest(self, text: str, limit: int = 5) -> List[Tuple[str, float]]:
        try:
            from rapidfuzz import process, fuzz  # type: ignore
        except Exception:
            return []

        corpus = list(self._corpus_provider())
        if not corpus:
            return []
        candidates = process.extract(text, corpus, scorer=fuzz.ratio, limit=limit)
        out: List[Tuple[str, float]] = []
        for cand, score, _idx in candidates:
            conf = float(score) / 100.0
            if conf >= float(self._cfg.fuzzy_accuracy_target):
                out.append((cand, conf))
        return out

    def confidence(self, a: str, b: str) -> float:
        try:
            from rapidfuzz import fuzz  # type: ignore

            return float(fuzz.ratio(a, b)) / 100.0
        except Exception:
            return 0.0

