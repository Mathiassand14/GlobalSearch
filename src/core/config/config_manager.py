from __future__ import annotations

import json
import threading
import time
from dataclasses import asdict
import os
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from cross_ide_path_utils import PathResolver
from src.core.models.configuration import ApplicationConfig, DockerServiceConfig, PerformanceSettings, SearchSettings


class ConfigurationManager:
    """
    Loads, validates, saves, and optionally hot‑reloads `config/settings.json`.

    - Paths are resolved via `PathResolver` per repo guidelines.
    - Validation converts raw JSON into `ApplicationConfig` and nested dataclasses.
    - Hot-reload uses a lightweight polling thread that invokes a callback with the
      updated `ApplicationConfig` when file mtime changes.
    """

    def __init__(
        self,
        resolver: Optional[PathResolver] = None,
        config_path: Optional[Path] = None,
    ) -> None:
        self._resolver = resolver or PathResolver()
        self._config_path: Path = config_path or self._resolver.get_config_path("settings.json")
        self._hot_reload_thread: Optional[threading.Thread] = None
        self._hot_reload_stop = threading.Event()
        self._last_mtime: Optional[float] = None

    # -------- Persistence --------
    def load(self) -> ApplicationConfig:
        """Load config from disk; create defaults if missing."""
        self._ensure_parent_dir()
        if not self._config_path.exists():
            default = ApplicationConfig()
            self.save(default)
            return default
        with self._config_path.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        cfg = self._validate_and_build(raw)
        self._last_mtime = self._config_path.stat().st_mtime
        return cfg

    def save(self, config: ApplicationConfig) -> None:
        """Persist config to disk as pretty-printed JSON."""
        self._ensure_parent_dir()
        data = self._to_dict(config)
        with self._config_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        # Force mtime update to ensure watcher detects rapid changes
        now = time.time()
        os.utime(self._config_path, (now, now))

    # -------- Validation / Conversion --------
    def _validate_and_build(self, data: Dict[str, Any]) -> ApplicationConfig:
        # Search settings
        ss_data: Dict[str, Any] = data.get("search_settings", {}) or {}
        search_settings = SearchSettings(**{k: v for k, v in ss_data.items() if k in SearchSettings.__annotations__})

        # Performance settings
        ps_data: Dict[str, Any] = data.get("performance_settings", {}) or {}
        performance_settings = PerformanceSettings(
            **{k: v for k, v in ps_data.items() if k in PerformanceSettings.__annotations__}
        )

        # Docker services
        ds_data: Dict[str, Any] = data.get("docker_services", {}) or {}
        docker_services = DockerServiceConfig(
            **{k: v for k, v in ds_data.items() if k in DockerServiceConfig.__annotations__}
        )

        # Top-level config
        elasticsearch_url = str(data.get("elasticsearch_url", ApplicationConfig.elasticsearch_url))
        document_directories = data.get("document_directories", []) or []
        # Normalize directories to strings but ensure they are valid path-like values
        document_directories = [str(Path(p)) for p in document_directories]

        supported_file_types = data.get("supported_file_types")
        if not isinstance(supported_file_types, list):
            supported_file_types = [".pdf", ".docx", ".txt", ".md"]

        ui_settings = data.get("ui_settings", {}) or {}

        cfg = ApplicationConfig(
            elasticsearch_url=elasticsearch_url,
            document_directories=document_directories,
            supported_file_types=supported_file_types,
            search_settings=search_settings,
            ui_settings=ui_settings,
            performance_settings=performance_settings,
            docker_services=docker_services,
        )
        return cfg

    def _to_dict(self, cfg: ApplicationConfig) -> Dict[str, Any]:
        data = asdict(cfg)
        # Ensure paths serialized as strings
        data["document_directories"] = [str(Path(p)) for p in cfg.document_directories]
        return data

    def _ensure_parent_dir(self) -> None:
        self._resolver.ensure_directory_exists(self._config_path.parent)

    # -------- Hot Reload --------
    def start_hot_reload(self, callback: Callable[[ApplicationConfig], None], interval_sec: float = 1.0) -> None:
        """
        Start a daemon thread that monitors config file mtime and invokes callback
        with a freshly loaded `ApplicationConfig` when it changes.
        """
        if self._hot_reload_thread and self._hot_reload_thread.is_alive():
            return
        self._hot_reload_stop.clear()

        def _watch() -> None:
            while not self._hot_reload_stop.is_set():
                try:
                    if self._config_path.exists():
                        mtime = self._config_path.stat().st_mtime
                        if self._last_mtime is None:
                            self._last_mtime = mtime
                        elif mtime > self._last_mtime:
                            self._last_mtime = mtime
                            cfg = self.load()
                            callback(cfg)
                except Exception:
                    # Fail-safe: never raise from watcher
                    pass
                time.sleep(max(0.1, float(interval_sec)))

        self._hot_reload_thread = threading.Thread(target=_watch, name="config-hot-reload", daemon=True)
        self._hot_reload_thread.start()

    def stop_hot_reload(self) -> None:
        self._hot_reload_stop.set()
        if self._hot_reload_thread is not None:
            self._hot_reload_thread.join(timeout=2.0)
            self._hot_reload_thread = None
