from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List


@dataclass(slots=True)
class PageContent:
    page_number: int
    text: str

    def __post_init__(self) -> None:
        if self.page_number < 0:
            raise ValueError("page_number must be >= 0")


@dataclass(slots=True)
class DocumentContent:
    file_path: Path
    title: str
    pages: List[PageContent] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.file_path, Path):
            self.file_path = Path(self.file_path)
        # normalize without IO
        self.file_path = Path(str(self.file_path))

    @classmethod
    def from_text(cls, file_path: Path, title: str, text: str) -> "DocumentContent":
        return cls(file_path=file_path, title=title, pages=[PageContent(page_number=0, text=text)])

