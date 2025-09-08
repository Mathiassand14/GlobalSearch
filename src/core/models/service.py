from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class ServiceStatus:
    service_name: str
    is_running: bool
    health_status: str
    error_message: Optional[str] = None


@dataclass(slots=True)
class IndexingStatus:
    total_documents: int
    processed_documents: int
    failed_documents: int
    is_complete: bool
    current_file: Optional[str] = None


@dataclass(slots=True)
class ReEncodingResult:
    total_documents: int
    re_encoded_documents: int
    failed_documents: int
    old_model: str
    new_model: str
    is_complete: bool
    estimated_time_remaining: Optional[int] = None  # seconds

    def __post_init__(self) -> None:
        if self.total_documents < 0 or self.re_encoded_documents < 0 or self.failed_documents < 0:
            raise ValueError("document counts must be >= 0")
        if self.re_encoded_documents + self.failed_documents > self.total_documents:
            raise ValueError("re_encoded + failed cannot exceed total_documents")
