from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass(slots=True)
class TopicNode:
    name: str
    path: str  # e.g., "algorithms/trees/binary_trees"
    children: List['TopicNode'] = field(default_factory=list)
    document_count: int = 0
    relevance_score: float = 0.0

    def __post_init__(self) -> None:
        if self.document_count < 0:
            raise ValueError("document_count must be >= 0")
        if not (0.0 <= self.relevance_score <= 1.0):
            raise ValueError("relevance_score must be in [0.0, 1.0]")
        self._validate_path(self.path)
        for child in self.children:
            if not child.path.startswith(self.path):
                # Allow direct descendant or deeper (prefix match)
                raise ValueError("child path must be under parent path")

    @staticmethod
    def _validate_path(path: str) -> None:
        if not path or path.strip("/") != path:
            raise ValueError("path must not have leading or trailing slashes")
        parts = [p for p in path.split("/") if p]
        if not parts:
            raise ValueError("path must contain segments")


@dataclass(slots=True)
class TopicTree:
    root_nodes: List[TopicNode]
    total_topics: int
    generation_timestamp: datetime

    def __post_init__(self) -> None:
        computed = self._count_nodes(self.root_nodes)
        if self.total_topics != computed:
            raise ValueError(f"total_topics mismatch: expected {computed}, got {self.total_topics}")

    @staticmethod
    def _count_nodes(nodes: List[TopicNode]) -> int:
        return sum(1 + TopicTree._count_nodes(n.children) for n in nodes)

