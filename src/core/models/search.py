from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class MatchType(str, Enum):
    EXACT = "EXACT"
    FUZZY = "FUZZY"
    SEMANTIC = "SEMANTIC"


@dataclass(slots=True)
class SearchResult:
    document_id: str
    document_title: str
    page_number: int
    snippet: str
    relevance_score: float
    match_type: MatchType
    highlighted_text: str
    topic_path: Optional[str] = None  # e.g., "algorithms/trees/binary_trees"

    def __post_init__(self) -> None:
        if self.page_number < 0:
            raise ValueError("page_number must be >= 0")
        if not (0.0 <= self.relevance_score <= 1.0):
            raise ValueError("relevance_score must be in [0.0, 1.0]")
        if self.topic_path is not None:
            self._validate_topic_path(self.topic_path)

    @staticmethod
    def _validate_topic_path(path: str) -> None:
        # Topic path is a slash-delimited, non-empty segments string; no leading/trailing slash
        if not path or path.strip("/") != path:
            raise ValueError("topic_path must not have leading or trailing slashes")
        segments = [seg for seg in path.split("/") if seg]
        if not segments:
            raise ValueError("topic_path must contain at least one segment")

