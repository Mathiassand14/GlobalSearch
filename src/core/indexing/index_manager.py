from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import os
from cross_ide_path_utils import PathResolver
from src.core.documents.models import DocumentContent
from src.core.models.configuration import ApplicationConfig


@dataclass(slots=True)
class IndexSettings:
    index_name: str = "documents"
    embedding_dim: int = 384  # all-MiniLM-L6-v2


class IndexManager:
    """Elasticsearch indexing manager with semantic embeddings.

    - Lazily imports heavy deps (elasticsearch, sentence_transformers, joblib).
    - Provides index creation with dense_vector mapping and bulk indexing.
    """

    def __init__(
        self,
        resolver: Optional[PathResolver] = None,
        es_client: Optional[Any] = None,
        settings: Optional[IndexSettings] = None,
        config: Optional[ApplicationConfig] = None,
    ) -> None:
        self._resolver = resolver or PathResolver()
        self._es = es_client  # Can be provided/mocked for tests
        self._settings = settings or IndexSettings()
        self._model: Optional[Any] = None
        self._config = config

    # ---- Public API ----
    def ensure_index(self) -> None:
        es = self._get_es()
        idx = self._settings.index_name
        if not es.indices.exists(index=idx):  # type: ignore[attr-defined]
            es.indices.create(index=idx, body=self._index_schema())  # type: ignore[attr-defined]

    def index_document(self, doc: DocumentContent) -> Dict[str, Any]:
        es = self._get_es()
        payload = self._to_document_payload(doc)
        es.index(index=self._settings.index_name, document=payload)  # type: ignore[attr-defined]
        return payload

    def bulk_index(self, docs: Sequence[DocumentContent], parallel: bool = False, n_jobs: int = 2) -> List[Dict[str, Any]]:
        if not docs:
            return []
        if parallel:
            jobs = self._get_joblib()
            processed: List[Dict[str, Any]] = jobs["Parallel"](n_jobs=n_jobs)(
                jobs["delayed"](self.index_document)(d) for d in docs
            )
            return list(processed)
        return [self.index_document(d) for d in docs]

    # ---- Helpers ----
    def _to_document_payload(self, doc: DocumentContent) -> Dict[str, Any]:
        text = "\n".join(p.text for p in doc.pages)
        embedding = self._embed([text])[0]
        return {
            "title": doc.title,
            "file_path": str(doc.file_path),
            "page_count": len(doc.pages),
            "content": text,
            "metadata": doc.metadata,
            "embedding": embedding,
        }

    def _index_schema(self) -> Dict[str, Any]:
        return {
            "mappings": {
                "properties": {
                    "title": {"type": "text"},
                    "file_path": {"type": "keyword"},
                    "page_count": {"type": "integer"},
                    "content": {"type": "text"},
                    "metadata": {"type": "object", "enabled": True},
                    "embedding": {
                        "type": "dense_vector",
                        "dims": int(self._settings.embedding_dim),
                        "similarity": "cosine",
                    },
                }
            }
        }

    # ---- Embeddings ----
    def _embed(self, texts: Sequence[str]) -> List[List[float]]:
        model = self._get_model()
        # normalize_embeddings yields unit vectors suitable for cosine similarity
        vecs = model.encode(list(texts), normalize_embeddings=True)
        return [list(map(float, v)) for v in vecs]

    # ---- Lazy deps ----
    def _get_es(self) -> Any:
        if self._es is not None:
            return self._es
        from elasticsearch import Elasticsearch  # type: ignore

        # Prefer ApplicationConfig URL if provided, then environment, then localhost (req 6.2)
        url: str
        if self._config is not None and getattr(self._config, "elasticsearch_url", None):
            url = str(self._config.elasticsearch_url)
        else:
            url = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
        self._es = Elasticsearch(url)  # type: ignore[call-arg]
        return self._es

    def _get_model(self) -> Any:
        if self._model is not None:
            return self._model
        from sentence_transformers import SentenceTransformer  # type: ignore

        # Mandatory model name per requirements
        self._model = SentenceTransformer("all-MiniLM-L6-v2")
        return self._model

    @staticmethod
    def _get_joblib() -> Dict[str, Any]:
        from joblib import Parallel, delayed  # type: ignore

        return {"Parallel": Parallel, "delayed": delayed}
