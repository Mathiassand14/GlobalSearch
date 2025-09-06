from __future__ import annotations

import json
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple
from urllib.error import URLError
from urllib.request import Request, urlopen

from cross_ide_path_utils import PathResolver
from src.core.models.configuration import ApplicationConfig
from src.core.models.service import ServiceStatus


@dataclass(slots=True)
class ComposeBinary:
    command: List[str]
    name: str


class DockerServiceManager:
    """Manages docker compose services per ApplicationConfig (req 6.1, 6.3, 6.4)."""

    def __init__(self, resolver: Optional[PathResolver] = None) -> None:
        self._resolver = resolver or PathResolver()
        self._compose_bin: Optional[ComposeBinary] = None

    # ---- Public API ----
    def ensure_services(self, cfg: ApplicationConfig) -> Dict[str, ServiceStatus]:
        """Start required services and verify health within timeout.

        Returns a mapping of service name -> ServiceStatus.
        """
        required = list(cfg.docker_services.required_services)
        statuses = {name: ServiceStatus(service_name=name, is_running=False, health_status="unknown") for name in required}

        if not required:
            return statuses

        compose = self._resolve_compose()
        compose_file = self._resolver.resolve_path("docker-compose.yml")

        # Start required services
        self._compose_up(compose, compose_file, required)

        # Health checks with timeout
        deadline = time.time() + max(5, cfg.docker_services.health_check_timeout)
        while time.time() < deadline:
            all_healthy = True
            for name in required:
                ok, health = self._check_health(name, cfg)
                is_running = ok and health in ("green", "healthy", "ok")
                statuses[name] = ServiceStatus(service_name=name, is_running=is_running, health_status=health)
                if not is_running:
                    all_healthy = False
            if all_healthy:
                break
            time.sleep(1.0)

        return statuses

    # ---- Health Helpers ----
    def _check_health(self, service_name: str, cfg: ApplicationConfig) -> Tuple[bool, str]:
        if service_name == "elasticsearch":
            return self._check_elasticsearch(cfg.elasticsearch_url)
        # Simplified health checks for other services; extend as needed
        return True, "ok"

    @staticmethod
    def _check_elasticsearch(url: str) -> Tuple[bool, str]:
        try:
            req = Request(url.rstrip("/") + "/_cluster/health", headers={"Accept": "application/json"})
            with urlopen(req, timeout=2) as resp:  # nosec - local docker health check
                data = json.loads(resp.read().decode("utf-8"))
                status = str(data.get("status", "unknown"))
                return True, status
        except URLError:
            return False, "unreachable"
        except Exception:
            return False, "error"

    # ---- Docker Compose Helpers ----
    def _resolve_compose(self) -> ComposeBinary:
        if self._compose_bin is not None:
            return self._compose_bin
        # Prefer modern docker compose (plugin)
        if self._which(["docker", "compose", "version"]):
            self._compose_bin = ComposeBinary(command=["docker", "compose"], name="docker compose")
            return self._compose_bin
        # Fallback to legacy docker-compose
        if self._which(["docker-compose", "--version"]):
            self._compose_bin = ComposeBinary(command=["docker-compose"], name="docker-compose")
            return self._compose_bin
        raise RuntimeError("docker compose not found; install Docker Compose v2 or docker-compose")

    @staticmethod
    def _which(cmd: List[str]) -> bool:
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            return True
        except Exception:
            return False

    @staticmethod
    def _compose_up(compose: ComposeBinary, compose_file: Path, services: Iterable[str]) -> None:
        args = compose.command + ["-f", str(compose_file), "up", "-d", *services]
        subprocess.run(args, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # best-effort

