from __future__ import annotations

from fastapi.testclient import TestClient

from src.api.main import app
from cross_ide_path_utils import PathResolver
from pathlib import Path


def test_health() -> None:
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_config_roundtrip() -> None:
    client = TestClient(app)
    r = client.get("/api/config")
    assert r.status_code == 200
    data = r.json()
    # Update semantic threshold
    data["search_settings"]["semantic_similarity_threshold"] = 0.66
    u = client.put("/api/config", json=data)
    assert u.status_code == 200
    assert u.json()["search_settings"]["semantic_similarity_threshold"] == 0.66


def test_search_returns_list() -> None:
    client = TestClient(app)
    r = client.post("/api/search", json={"query": "test", "limit": 2})
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_suggest_endpoint() -> None:
    client = TestClient(app)
    r = client.get("/api/search/suggest", params={"q": "te", "limit": 3})
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_upload_list_delete_document(tmp_path) -> None:
    client = TestClient(app)

    # Monkeypatch documents dir to temp
    orig = PathResolver.get_document_path
    PathResolver.get_document_path = staticmethod(lambda: tmp_path)  # type: ignore
    try:
        # Upload a small file
        payload = {"file": ("hello.txt", b"hello", "text/plain")}
        r = client.post("/api/documents/upload", files=payload)
        assert r.status_code == 200
        name = r.json()["name"]

        # List and confirm presence
        r2 = client.get("/api/documents")
        data = r2.json()
        assert any(it["name"] == name for it in data["items"]) and data["total"] >= 1

        # Get content
        r3 = client.get(f"/api/documents/{name}/content")
        assert r3.status_code == 200 and r3.content == b"hello"

        # Delete
        r4 = client.delete(f"/api/documents/{name}")
        assert r4.status_code == 200
        assert not (tmp_path / name).exists()
    finally:
        PathResolver.get_document_path = orig  # type: ignore
