from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.error import URLError

import pytest

from src.core.models.configuration import ApplicationConfig, DockerServiceConfig
from src.core.services import DockerServiceManager


def _cfg(required: list[str] = ["elasticsearch"]) -> ApplicationConfig:  # noqa: B006 - test default
    return ApplicationConfig(
        elasticsearch_url="http://localhost:9200",
        docker_services=DockerServiceConfig(required_services=required, health_check_timeout=1),
    )


def test_resolves_docker_compose_and_starts_services(monkeypatch, tmp_path: Path) -> None:
    mgr = DockerServiceManager()

    # Pretend docker compose exists
    def fake_run(cmd, stdout=None, stderr=None, check=False):  # noqa: ANN001
        return 0

    monkeypatch.setattr("subprocess.run", fake_run)

    # Avoid running real compose up; our fake_run swallows it
    statuses = mgr.ensure_services(_cfg(["elasticsearch"]))
    # Health will still be unreachable without urlopen mocking, but ensure keys exist
    assert "elasticsearch" in statuses


class _Resp:
    def __init__(self, payload: dict[str, Any]):
        self._data = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self._data

    def __enter__(self) -> "_Resp":
        return self

    def __exit__(self, exc_type, exc, tb):  # noqa: ANN001
        return None


def test_elasticsearch_health_ok(monkeypatch) -> None:
    def fake_urlopen(req, timeout=2):  # noqa: ANN001
        return _Resp({"status": "green"})

    monkeypatch.setattr("src.core.services.docker_manager.urlopen", fake_urlopen)
    ok, status = DockerServiceManager._check_elasticsearch("http://localhost:9200")
    assert ok and status == "green"


def test_elasticsearch_health_unreachable(monkeypatch) -> None:
    def fake_urlopen(req, timeout=2):  # noqa: ANN001
        raise URLError("connection refused")

    monkeypatch.setattr("src.core.services.docker_manager.urlopen", fake_urlopen)
    ok, status = DockerServiceManager._check_elasticsearch("http://localhost:9200")
    assert not ok and status == "unreachable"

