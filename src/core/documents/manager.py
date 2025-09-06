from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from src.core.documents.base import DocumentProcessor
from src.core.documents.models import DocumentContent
from src.core.exceptions.exceptions import DocumentProcessingError


class DocumentManager:
    """Registers processors and routes files to the appropriate one by suffix."""

    def __init__(self) -> None:
        self._processors: List[DocumentProcessor] = []
        self._suffix_map: Dict[str, DocumentProcessor] = {}

    def register(self, processor: DocumentProcessor) -> None:
        """Register a processor; first registration for a suffix wins (priority)."""
        self._processors.append(processor)
        for sfx in map(str.lower, processor.supported_suffixes):
            if not sfx.startswith("."):
                sfx = "." + sfx
            self._suffix_map.setdefault(sfx, processor)

    def get_processor_for(self, file_path: Path) -> Optional[DocumentProcessor]:
        suffix = file_path.suffix.lower()
        return self._suffix_map.get(suffix)

    def process(self, file_path: Path) -> DocumentContent:
        proc = self.get_processor_for(file_path)
        if proc is None:
            raise DocumentProcessingError(f"No processor registered for: {file_path.suffix}")
        try:
            return proc.process(file_path)
        except DocumentProcessingError:
            raise
        except Exception as exc:  # pragma: no cover - defensive path
            raise DocumentProcessingError(str(exc)) from exc

    @property
    def registered_suffixes(self) -> List[str]:
        return sorted(self._suffix_map.keys())

