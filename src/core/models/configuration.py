from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(slots=True)
class SearchSettings:
    fuzzy_edit_distance: int = 2
    fuzzy_accuracy_target: float = 0.8
    semantic_similarity_threshold: float = 0.7
    search_timeout_seconds: int = 2
    core_search_timeout_ms: int = 500
    enable_auto_complete: bool = True
    enable_spelling_correction: bool = True
    enable_boolean_operators: bool = True
    enable_ai_search: bool = True
    fallback_to_preencoded_only: bool = False
    current_model_name: str = "all-MiniLM-L6-v2"
    custom_model_path: Optional[str] = None
    enable_topic_hierarchy: bool = True
    topic_hierarchy_depth: int = 3


@dataclass(slots=True)
class PerformanceSettings:
    max_cached_documents: int = 50
    max_memory_usage_gb: float = 1.0
    indexing_batch_size: int = 100
    search_debounce_ms: int = 300
    page_preload_range: int = 10
    auto_cleanup_threshold: float = 0.8
    max_collection_size_fast_search: int = 1000


@dataclass(slots=True)
class DockerServiceConfig:
    auto_start_services: bool = True
    elasticsearch_port: int = 9200
    health_check_timeout: int = 30
    required_services: List[str] = field(default_factory=lambda: ["elasticsearch"])
    service_startup_verification: bool = True


@dataclass(slots=True)
class ApplicationConfig:
    elasticsearch_url: str = "http://localhost:9200"
    document_directories: List[str] = field(default_factory=list)
    supported_file_types: List[str] = field(default_factory=lambda: [".pdf", ".docx", ".txt", ".md"])
    search_settings: SearchSettings = field(default_factory=SearchSettings)
    ui_settings: dict = field(default_factory=dict)  # Placeholder for future UI settings dataclass
    performance_settings: PerformanceSettings = field(default_factory=PerformanceSettings)
    docker_services: DockerServiceConfig = field(default_factory=DockerServiceConfig)

    def __post_init__(self) -> None:
        # Basic sanity checks aligned with requirements
        if not (0.0 < self.performance_settings.max_memory_usage_gb):
            raise ValueError("max_memory_usage_gb must be positive")
        if self.search_settings.fuzzy_edit_distance < 0:
            raise ValueError("fuzzy_edit_distance must be >= 0")

