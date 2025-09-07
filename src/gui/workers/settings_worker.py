from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal

from src.core.config import ConfigurationManager
from src.core.models.configuration import ApplicationConfig


class SettingsWorker(QObject):
    config_loaded = pyqtSignal(ApplicationConfig)
    error = pyqtSignal(str)

    def __init__(self, manager: ConfigurationManager) -> None:
        super().__init__()
        self._manager = manager

    def load(self) -> None:
        try:
            cfg = self._manager.load()
            self.config_loaded.emit(cfg)
        except Exception as exc:  # pragma: no cover - defensive
            self.error.emit(str(exc))

    def save(self, config: ApplicationConfig) -> None:
        try:
            self._manager.save(config)
        except Exception as exc:  # pragma: no cover - defensive
            self.error.emit(str(exc))

