from __future__ import annotations

from typing import Any, Dict, List, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.core.config import ConfigurationManager
from src.core.models.configuration import ApplicationConfig
from src.core.search import SearchManager
from cross_ide_path_utils import PathResolver


app = FastAPI(title="GlobalSearch API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
cfg_manager = ConfigurationManager()
# Initialize SearchManager with loaded config (req 6.2)
search_manager = SearchManager(config=cfg_manager.load())
_ws_upload_clients: Dict[str, List[WebSocket]] = {}


class SearchRequest(BaseModel):
    query: str
    limit: int = 10
    topic: Optional[str] = None


class SuggestResponse(BaseModel):
    term: str
    confidence: float


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/api/search")
def api_search(req: SearchRequest) -> List[Dict[str, Any]]:
    if not req.query:
        raise HTTPException(status_code=400, detail="query must not be empty")
    res = search_manager.search(req.query, limit=req.limit, topic_filter=req.topic)
    out: List[Dict[str, Any]] = []
    for r in res:
        out.append(
            {
                "document_id": r.document_id,
                "document_title": r.document_title,
                "page_number": r.page_number,
                "snippet": r.snippet,
                "relevance_score": r.relevance_score,
                "match_type": r.match_type.value,
                "highlighted_text": r.highlighted_text,
                "topic_path": r.topic_path,
            }
        )
    return out


@app.get("/api/search/suggest")
def api_suggest(q: str, limit: int = 5) -> List[SuggestResponse]:
    if not q:
        return []
    # Use SearchManager.suggest which leverages provider; fallback to []
    try:
        suggestions = search_manager.suggest(q, limit=limit)
    except Exception:
        suggestions = []
    return [SuggestResponse(term=s, confidence=0.0) for s in suggestions]


# ---------- Advanced search (pagination/sorting) ----------
class AdvancedSearchRequest(BaseModel):
    query: str
    page: int = 1
    size: int = 10
    sort: str = "score"  # or 'name'
    topic: Optional[str] = None


@app.post("/api/search/advanced")
def api_search_advanced(req: AdvancedSearchRequest) -> Dict[str, Any]:
    if not req.query:
        raise HTTPException(status_code=400, detail="query must not be empty")
    size = max(1, min(100, int(req.size)))
    page = max(1, int(req.page))
    # Get a superset of results, then slice
    sup = search_manager.search(req.query, limit=page * size, topic_filter=req.topic)
    if req.sort == "name":
        sup.sort(key=lambda r: (r.document_title or ""))
    else:
        sup.sort(key=lambda r: r.relevance_score, reverse=True)
    start = (page - 1) * size
    items = sup[start:start + size]
    total = len(sup)
    data = [
        {
            "document_id": r.document_id,
            "document_title": r.document_title,
            "page_number": r.page_number,
            "snippet": r.snippet,
            "relevance_score": r.relevance_score,
            "match_type": r.match_type.value,
            "highlighted_text": r.highlighted_text,
            "topic_path": r.topic_path,
        }
        for r in items
    ]
    return {"total": total, "page": page, "size": size, "items": data}


# ---------- Document management ----------
def _docs_dir() -> Path:
    d = PathResolver().get_document_path()
    d.mkdir(parents=True, exist_ok=True)
    return d


def _unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem, suf = path.stem, path.suffix
    i = 1
    while True:
        c = path.parent / f"{stem} ({i}){suf}"
        if not c.exists():
            return c
        i += 1


@app.get("/api/documents")
def list_documents(page: int = 1, size: int = 20, q: Optional[str] = None) -> Dict[str, Any]:
    size = max(1, min(200, int(size)))
    page = max(1, int(page))
    files = [p for p in _docs_dir().iterdir() if p.is_file()]
    if q:
        files = [p for p in files if q.lower() in p.name.lower()]
    files.sort(key=lambda p: p.name.lower())
    total = len(files)
    start = (page - 1) * size
    items = files[start:start + size]
    out_items: List[Dict[str, Any]] = []
    for p in items:
        st = p.stat()
        out_items.append({
            "name": p.name,
            "size": st.st_size,
            "modified": st.st_mtime,
        })
    return {"total": total, "page": page, "size": size, "items": out_items}


@app.post("/api/documents/upload")
async def upload_document(file: UploadFile = File(...), upload_id: Optional[str] = None) -> Dict[str, Any]:
    if not file.filename:
        raise HTTPException(status_code=400, detail="filename missing")
    dest = _unique_path(_docs_dir() / Path(file.filename).name)
    try:
        # Stream copy
        sent = 0
        clients = _ws_upload_clients.get(upload_id or "", [])
        with open(dest, "wb") as f:
            while True:
                chunk = await file.read(8192)
                if not chunk:
                    break
                f.write(chunk)
                sent += len(chunk)
                for c in list(clients):
                    try:
                        await c.send_json({"upload_id": upload_id, "bytes": sent})
                    except Exception:
                        pass
    finally:
        await file.close()
    st = dest.stat()
    return {"name": dest.name, "size": st.st_size}


@app.delete("/api/documents/{name}")
def delete_document(name: str) -> Dict[str, Any]:
    p = (_docs_dir() / name)
    if not p.exists() or not p.is_file():
        raise HTTPException(status_code=404, detail="not found")
    p.unlink()
    return {"deleted": name}


@app.get("/api/documents/{name}/content")
def get_document_content(name: str, request: Request):  # type: ignore[override]
    p = (_docs_dir() / name)
    if not p.exists() or not p.is_file():
        raise HTTPException(status_code=404, detail="not found")
    # Range support
    range_header = request.headers.get("range") or request.headers.get("Range")
    if not range_header:
        return FileResponse(str(p), filename=p.name)
    try:
        _, rng = range_header.split("=", 1)
        start_s, end_s = (rng.split("-", 1) + [""])[:2]
        file_size = p.stat().st_size
        start = int(start_s) if start_s else 0
        end = int(end_s) if end_s else file_size - 1
        start = max(0, start)
        end = min(file_size - 1, end)
        if start > end:
            start, end = 0, file_size - 1
        length = end - start + 1
        def iter_file(path: Path, start: int, length: int):
            with open(path, 'rb') as f:
                f.seek(start)
                remaining = length
                chunk = 8192
                while remaining > 0:
                    data = f.read(min(chunk, remaining))
                    if not data:
                        break
                    remaining -= len(data)
                    yield data
        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(length),
        }
        return StreamingResponse(iter_file(p, start, length), status_code=206, headers=headers)
    except Exception:
        return FileResponse(str(p), filename=p.name)


@app.websocket("/ws/upload-progress")
async def ws_upload_progress(ws: WebSocket, upload_id: str):
    await ws.accept()
    clients = _ws_upload_clients.setdefault(upload_id, [])
    clients.append(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        try:
            clients.remove(ws)
            if not clients:
                _ws_upload_clients.pop(upload_id, None)
        except ValueError:
            pass


@app.get("/api/config")
def get_config() -> Dict[str, Any]:
    cfg = cfg_manager.load()
    # Pydantic cannot natively serialize dataclasses deeply; convert via asdict-like behavior
    from dataclasses import asdict

    data = asdict(cfg)
    return data


@app.put("/api/config")
def put_config(payload: Dict[str, Any]) -> Dict[str, Any]:
    # Accept partial payload; ConfigurationManager validates and fills defaults
    try:
        cfg = cfg_manager._validate_and_build(payload)  # type: ignore[attr-defined]
        cfg_manager.save(cfg)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    from dataclasses import asdict

    return asdict(cfg)
