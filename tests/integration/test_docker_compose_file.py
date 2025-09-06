from __future__ import annotations

from pathlib import Path


def test_docker_compose_services_present() -> None:
    compose = Path("docker-compose.yml")
    assert compose.exists(), "docker-compose.yml must exist at repo root"
    text = compose.read_text(encoding="utf-8")
    for svc in ["elasticsearch:", "postgresql:", "redis:"]:
        assert svc in text, f"Missing service '{svc.rstrip(':')}' in docker-compose.yml"

