from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Dict, List

from src.core.documents.models import DocumentContent, PageContent
from src.core.indexing import IndexManager, IndexSettings


class _FakeIndices:
    def __init__(self) -> None:
        self.created: Dict[str, dict] = {}

    def exists(self, index: str) -> bool:  # noqa: A003 - ES API compat
        return index in self.created

    def create(self, index: str, body: dict) -> None:
        self.created[index] = body


class _FakeES:
    def __init__(self) -> None:
        self.indices = _FakeIndices()
        self.indexed: List[dict] = []

    def index(self, index: str, document: dict) -> None:  # noqa: A003
        self.indexed.append({"index": index, "document": document})


class _FakeModel:
    def __init__(self, dim: int) -> None:
        self._dim = dim

    def encode(self, texts: list[str], normalize_embeddings: bool = True):  # noqa: ANN001
        return [[0.0] * self._dim for _ in texts]


def test_create_index_schema_and_index_document(monkeypatch) -> None:
    es = _FakeES()
    settings = IndexSettings(index_name="docs", embedding_dim=384)
    mgr = IndexManager(es_client=es, settings=settings)

    # Inject fake model to avoid heavy downloads
    mgr._model = _FakeModel(settings.embedding_dim)  # type: ignore[attr-defined]

    # Ensure index creation
    mgr.ensure_index()
    assert "docs" in es.indices.created
    mapping = es.indices.created["docs"]
    assert mapping["mappings"]["properties"]["embedding"]["dims"] == 384

    # Index a document
    doc = DocumentContent(file_path="/tmp/f.txt", title="f", pages=[PageContent(0, "hello")])
    payload = mgr.index_document(doc)
    assert payload["title"] == "f"
    assert len(payload["embedding"]) == 384
    assert es.indexed and es.indexed[0]["index"] == "docs"


def test_bulk_index_parallel(monkeypatch) -> None:
    es = _FakeES()
    settings = IndexSettings(index_name="docs", embedding_dim=8)
    mgr = IndexManager(es_client=es, settings=settings)
    mgr._model = _FakeModel(settings.embedding_dim)  # type: ignore[attr-defined]

    # Monkeypatch joblib to run synchronously for speed
    def _Parallel(n_jobs=2):  # noqa: ANN001
        def runner(tasks):
            return [t() for t in tasks]

        return runner

    def _delayed(fn):  # noqa: ANN001
        return lambda *a, **k: (lambda: fn(*a, **k))

    monkeypatch.setattr("src.core.indexing.index_manager.IndexManager._get_joblib", staticmethod(lambda: {"Parallel": _Parallel, "delayed": _delayed}))

    docs = [
        DocumentContent(file_path=f"/tmp/{i}.txt", title=str(i), pages=[PageContent(0, "x")])
        for i in range(3)
    ]
    out = mgr.bulk_index(docs, parallel=True, n_jobs=2)
    assert len(out) == 3
    assert len(es.indexed) == 3

