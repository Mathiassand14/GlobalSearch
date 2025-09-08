from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


@dataclass(slots=True)
class Document:
    id: str
    file_path: Path
    title: str
    content: str
    page_count: int
    file_size: int
    created_date: datetime
    modified_date: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.file_path, Path):
            self.file_path = Path(self.file_path)
        if self.page_count < 0:
            raise ValueError("page_count must be >= 0")
        if self.file_size < 0:
            raise ValueError("file_size must be >= 0")
        if self.modified_date < self.created_date:
            raise ValueError("modified_date cannot be earlier than created_date")
        # Ensure normalized path (no resolution performed to avoid I/O)
        self.file_path = Path(str(self.file_path))

