from __future__ import annotations

from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.core.config import ConfigurationManager


class FileManagerWindow(QWidget):
    """Manage configured document directories; supports adding/removing via QFileDialog (req 6.2)."""

    def __init__(self, manager: ConfigurationManager, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Document Directories")
        self._manager = manager
        self._cfg = manager.load()
        self._build_ui()
        self._refresh_list()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        self.list = QListWidget(self)
        layout.addWidget(self.list)
        btns = QHBoxLayout()
        self.btn_add = QPushButton("Add Directory…", self)
        self.btn_remove = QPushButton("Remove Selected", self)
        btns.addWidget(self.btn_add)
        btns.addWidget(self.btn_remove)
        layout.addLayout(btns)
        self.btn_add.clicked.connect(self._on_add)
        self.btn_remove.clicked.connect(self._on_remove)

    def _refresh_list(self) -> None:
        self.list.clear()
        for d in self._cfg.document_directories:
            self.list.addItem(QListWidgetItem(str(d)))

    def _on_add(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            p = str(Path(directory))
            if p not in self._cfg.document_directories:
                self._cfg.document_directories.append(p)
                self._manager.save(self._cfg)
                self._refresh_list()

    def _on_remove(self) -> None:
        row = self.list.currentRow()
        if row < 0:
            return
        item = self.list.item(row)
        path = item.text()
        try:
            self._cfg.document_directories.remove(path)
        except ValueError:
            pass
        self._manager.save(self._cfg)
        self._refresh_list()

