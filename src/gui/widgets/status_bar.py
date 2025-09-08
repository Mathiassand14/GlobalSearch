from __future__ import annotations

from typing import Optional

from PyQt6.QtWidgets import QLabel


class StatusLabel(QLabel):
    def __init__(self, text: str = "", parent: Optional[object] = None) -> None:
        super().__init__(text, parent)
        self.setStyleSheet("color: gray;")

    def set_ok(self, text: str) -> None:
        self.setStyleSheet("color: green;")
        self.setText(text)

    def set_warn(self, text: str) -> None:
        self.setStyleSheet("color: orange;")
        self.setText(text)

    def set_error(self, text: str) -> None:
        self.setStyleSheet("color: red;")
        self.setText(text)

