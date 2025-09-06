from __future__ import annotations

import json
from typing import Any, Dict

from cross_ide_path_utils import PathResolver


def load_or_init_settings(resolver: PathResolver) -> Dict[str, Any]:
    """Load settings from config/settings.json or create defaults.

    Uses PathResolver for all path handling to satisfy cross‑IDE behavior.
    """
    config_path = resolver.get_config_path("settings.json")
    resolver.ensure_directory_exists(config_path.parent)

    if config_path.exists():
        with config_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    default_settings: Dict[str, Any] = {
        "elasticsearch_url": "http://localhost:9200",
        "document_directories": [],
        "supported_file_types": [".pdf", ".docx", ".txt", ".md"],
        "search_settings": {},
        "ui_settings": {},
        "performance_settings": {},
        "docker_services": {},
    }

    with config_path.open("w", encoding="utf-8") as f:
        json.dump(default_settings, f, indent=2)

    return default_settings


def main() -> None:
    """Application entry point (non‑GUI bootstrap)."""
    resolver = PathResolver()
    settings = load_or_init_settings(resolver)
    # Simple startup log; GUI wiring will come later per MVC.
    print(
        f"GlobalSearch starting — config: {resolver.get_config_path('settings.json')} | "
        f"ES: {settings.get('elasticsearch_url')}"
    )


if __name__ == "__main__":
    main()

