from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


class AppEvent:  # marker base class
    pass


@dataclass(slots=True)
class SearchResultSelected(AppEvent):
    document_id: str
    page_number: int
    query: str


@dataclass(slots=True)
class DocumentOpened(AppEvent):
    file_path: str
    source_window: Optional[str] = None


@dataclass(slots=True)
class WindowClosed(AppEvent):
    window_name: str


@dataclass(slots=True)
class IndexingProgress(AppEvent):
    total: int
    processed: int
    failed: int = 0

