from __future__ import annotations

from typing import Optional

from PyQt6.QtWidgets import QMessageBox, QWidget


def show_error(parent: Optional[QWidget], title: str, message: str) -> None:
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Icon.Critical)
    box.setWindowTitle(title)
    box.setText(message)
    box.exec()

