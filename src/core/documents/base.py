from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable

from src.core.documents.models import DocumentContent


class DocumentProcessor(ABC):
    """Abstract base for document processors.

    Implementations must be pure-core (no PyQt6) and use pathlib.Path for IO.
    """

    @property
    @abstractmethod
    def name(self) -> str:  # pragma: no cover - simple property contract
        """Human-readable name for the processor."""

    @property
    @abstractmethod
    def supported_suffixes(self) -> Iterable[str]:  # e.g., (".pdf",)
        """Return iterable of supported lowercase file suffixes including dot."""

    @abstractmethod
    def process(self, file_path: Path) -> DocumentContent:
        """Process a document and return unified content representation."""

