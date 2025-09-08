from __future__ import annotations

from typing import Any

from PyQt6.QtWidgets import QApplication

from cross_ide_path_utils import PathResolver
from src.core.config import ConfigurationManager
from src.core.services import DockerServiceManager
from src.gui.search_window import SearchWindow
from src.gui.settings_window import SettingsWindow
from src.gui.file_manager_window import FileManagerWindow


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
    app = QApplication([])
    deps = bootstrap()

    # Wiring a simple search window using a no-op search function placeholder
    from src.core.search import SearchManager

    sm = SearchManager()
    win = SearchWindow(search_fn=lambda q, n, *_: sm.search(q, limit=n))
    win.show()

    # Expose settings and file manager windows for manual testing
    settings = SettingsWindow(deps["config_manager"])  # noqa: F841
    filemgr = FileManagerWindow(deps["config_manager"])  # noqa: F841

    app.exec()


if __name__ == "__main__":
    main()
