from __future__ import annotations

import json
import time
from pathlib import Path
from typing import List

from src.core.config import ConfigurationManager
from src.core.models.configuration import ApplicationConfig


def test_load_creates_defaults_and_roundtrip(tmp_path: Path) -> None:
    cfg_path = tmp_path / "settings.json"
    mgr = ConfigurationManager(config_path=cfg_path)

    # First load should create defaults
    cfg = mgr.load()
    assert isinstance(cfg, ApplicationConfig)
    assert cfg.elasticsearch_url.startswith("http://")
    assert cfg_path.exists()

    # Modify and save
    cfg.elasticsearch_url = "http://localhost:9201"
    cfg.document_directories = [str(tmp_path / "docs"), str(tmp_path / "more" / "docs")] 
    mgr.save(cfg)

    # Reload from disk and verify
    cfg2 = mgr.load()
    assert cfg2.elasticsearch_url == "http://localhost:9201"
    assert [Path(p).name for p in cfg2.document_directories] == ["docs", "docs"]


def test_validation_applies_defaults(tmp_path: Path) -> None:
    cfg_path = tmp_path / "settings.json"
    raw = {
        # Missing many fields on purpose
        "elasticsearch_url": "http://example:9200",
        "document_directories": [str(tmp_path / "d1")],
        "search_settings": {"fuzzy_edit_distance": 3},
    }
    cfg_path.write_text(json.dumps(raw), encoding="utf-8")

    mgr = ConfigurationManager(config_path=cfg_path)
    cfg = mgr.load()
    assert cfg.search_settings.fuzzy_edit_distance == 3
    # Defaults applied
    assert cfg.performance_settings.indexing_batch_size > 0
    assert ".pdf" in cfg.supported_file_types


def test_hot_reload_triggers_on_change(tmp_path: Path) -> None:
    cfg_path = tmp_path / "settings.json"
    mgr = ConfigurationManager(config_path=cfg_path)
    cfg = mgr.load()
    assert cfg.elasticsearch_url

    seen: List[str] = []

    def on_change(new_cfg: ApplicationConfig) -> None:
        seen.append(new_cfg.elasticsearch_url)

    mgr.start_hot_reload(on_change, interval_sec=0.1)

    # Change file on disk
    cfg.elasticsearch_url = "http://changed:9200"
    mgr.save(cfg)

    # Allow watcher to detect
    timeout = time.time() + 3
    while not seen and time.time() < timeout:
        time.sleep(0.05)

    mgr.stop_hot_reload()
    assert seen and seen[-1] == "http://changed:9200"

