from __future__ import annotations

from typing import Any

from cross_ide_path_utils import PathResolver
from src.core.config import ConfigurationManager
from src.core.services import DockerServiceManager


def bootstrap() -> dict[str, Any]:
    resolver = PathResolver()
    cfg_mgr = ConfigurationManager(resolver=resolver)
    cfg = cfg_mgr.load()
    # Optionally start services
    if cfg.docker_services.auto_start_services:
        try:
            DockerServiceManager(resolver).ensure_services(cfg)
        except Exception:
            pass
    return {"resolver": resolver, "config_manager": cfg_mgr}


def main() -> None:
    """Backend/bootstrap entrypoint (GUI removed)."""
    import time

    deps = bootstrap()
    print("GlobalSearch backend initialized.")
    print("Elasticsearch:", deps["config_manager"].load().elasticsearch_url)
    print("Run API with: docker compose up -d api (port 8000)")
    print("This process idles for container dev; press Ctrl+C to exit.")
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("Shutting down...")


if __name__ == "__main__":
    main()
