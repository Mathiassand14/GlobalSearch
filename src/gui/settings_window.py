from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from src.core.config import ConfigurationManager
from src.core.models.configuration import ApplicationConfig, SearchSettings
from src.gui.workers.settings_worker import SettingsWorker


class SettingsWindow(QWidget):
    """Settings window with tabs for AI models, search, performance, and services (req 6.2, 6.5)."""

    def __init__(self, manager: ConfigurationManager, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self._manager = manager
        self._cfg: Optional[ApplicationConfig] = None

        self._build_ui()
        self._start_worker()

    # ---- UI ----
    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget(self)

        # AI Models tab
        self.tab_models = QWidget(self)
        fm = QFormLayout(self.tab_models)
        self.model_combo = QComboBox(self.tab_models)
        self.model_combo.addItems([
            "all-MiniLM-L6-v2",
            "all-mpnet-base-v2",
            "paraphrase-MiniLM-L6-v2",
        ])
        fm.addRow("Embedding model:", self.model_combo)
        layout_models = QVBoxLayout(self.tab_models)
        layout_models.addLayout(fm)
        self.tabs.addTab(self.tab_models, "AI Models")

        # Search tab
        self.tab_search = QWidget(self)
        fs = QFormLayout(self.tab_search)
        self.chk_semantic = QCheckBox("Enable AI semantic search")
        self.chk_fallback = QCheckBox("Fallback to pre-encoded only")
        self.spin_sem_thresh = QDoubleSpinBox(self.tab_search)
        self.spin_sem_thresh.setRange(0.0, 1.0)
        self.spin_sem_thresh.setSingleStep(0.05)
        self.spin_fuzzy_edit = QSpinBox(self.tab_search)
        self.spin_fuzzy_edit.setRange(0, 5)
        self.spin_fuzzy_acc = QDoubleSpinBox(self.tab_search)
        self.spin_fuzzy_acc.setRange(0.0, 1.0)
        self.spin_fuzzy_acc.setSingleStep(0.05)
        fs.addRow(self.chk_semantic)
        fs.addRow(self.chk_fallback)
        fs.addRow("Semantic threshold:", self.spin_sem_thresh)
        fs.addRow("Fuzzy edit distance:", self.spin_fuzzy_edit)
        fs.addRow("Fuzzy accuracy target:", self.spin_fuzzy_acc)
        layout_search = QVBoxLayout(self.tab_search)
        layout_search.addLayout(fs)
        self.tabs.addTab(self.tab_search, "Search")

        # Performance tab (basic)
        self.tab_perf = QWidget(self)
        fp = QFormLayout(self.tab_perf)
        self.spin_cache_docs = QSpinBox(self.tab_perf)
        self.spin_cache_docs.setRange(10, 10000)
        self.spin_debounce = QSpinBox(self.tab_perf)
        self.spin_debounce.setRange(50, 2000)
        fp.addRow("Max cached documents:", self.spin_cache_docs)
        fp.addRow("Search debounce (ms):", self.spin_debounce)
        layout_perf = QVBoxLayout(self.tab_perf)
        layout_perf.addLayout(fp)
        self.tabs.addTab(self.tab_perf, "Performance")

        # Services tab (basic toggle)
        self.tab_services = QWidget(self)
        fsrv = QFormLayout(self.tab_services)
        self.chk_auto_start = QCheckBox("Auto-start services")
        fsrv.addRow(self.chk_auto_start)
        layout_srv = QVBoxLayout(self.tab_services)
        layout_srv.addLayout(fsrv)
        self.tabs.addTab(self.tab_services, "Services")

        # Buttons
        btns = QHBoxLayout()
        self.btn_save = QPushButton("Save", self)
        self.btn_reload = QPushButton("Reload", self)
        btns.addStretch(1)
        btns.addWidget(self.btn_reload)
        btns.addWidget(self.btn_save)

        layout.addWidget(self.tabs)
        layout.addLayout(btns)

        self.btn_save.clicked.connect(self._on_save_clicked)
        self.btn_reload.clicked.connect(self._on_reload_clicked)

    # ---- Worker ----
    def _start_worker(self) -> None:
        self._thread = QThread(self)
        self._worker = SettingsWorker(self._manager)
        self._worker.moveToThread(self._thread)
        self._worker.config_loaded.connect(self._apply_config)
        self._thread.start()
        QThread.msleep(1)
        QThread.currentThread()
        # Load config asynchronously
        self._worker.load()

    # ---- Data binding ----
    def _apply_config(self, cfg: ApplicationConfig) -> None:
        self._cfg = cfg
        ss = cfg.search_settings
        # Models
        idx = self.model_combo.findText(ss.current_model_name)
        if idx != -1:
            self.model_combo.setCurrentIndex(idx)
        # Search
        self.chk_semantic.setChecked(bool(ss.enable_ai_search))
        self.chk_fallback.setChecked(bool(ss.fallback_to_preencoded_only))
        self.spin_sem_thresh.setValue(float(ss.semantic_similarity_threshold))
        self.spin_fuzzy_edit.setValue(int(ss.fuzzy_edit_distance))
        self.spin_fuzzy_acc.setValue(float(ss.fuzzy_accuracy_target))
        # Perf
        self.spin_cache_docs.setValue(int(cfg.performance_settings.max_cached_documents))
        self.spin_debounce.setValue(int(cfg.performance_settings.search_debounce_ms))
        # Services
        self.chk_auto_start.setChecked(bool(cfg.docker_services.auto_start_services))

    def _collect_config(self) -> ApplicationConfig:
        cfg = self._cfg or ApplicationConfig()
        ss: SearchSettings = cfg.search_settings
        ss.current_model_name = self.model_combo.currentText()
        ss.enable_ai_search = self.chk_semantic.isChecked()
        ss.fallback_to_preencoded_only = self.chk_fallback.isChecked()
        ss.semantic_similarity_threshold = float(self.spin_sem_thresh.value())
        ss.fuzzy_edit_distance = int(self.spin_fuzzy_edit.value())
        ss.fuzzy_accuracy_target = float(self.spin_fuzzy_acc.value())
        cfg.performance_settings.max_cached_documents = int(self.spin_cache_docs.value())
        cfg.performance_settings.search_debounce_ms = int(self.spin_debounce.value())
        cfg.docker_services.auto_start_services = self.chk_auto_start.isChecked()
        return cfg

    # ---- Actions ----
    def _on_save_clicked(self) -> None:
        cfg = self._collect_config()
        self._worker.save(cfg)

    def _on_reload_clicked(self) -> None:
        self._worker.load()

    def closeEvent(self, event) -> None:  # noqa: N802
        self._thread.quit()
        self._thread.wait(1000)
        super().closeEvent(event)

