from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QCheckBox, QSlider, QSpinBox,
    QGroupBox, QPushButton, QFormLayout, QScrollArea, QFrame, QHBoxLayout,
)
from PyQt6.QtCore import Qt, pyqtSignal
from config.settings import SETTINGS


class SettingsPanel(QWidget):
    settings_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        layout  = QVBoxLayout(content)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.addWidget(self._detection_grp())
        layout.addWidget(self._alert_grp())
        layout.addWidget(self._protection_grp())
        layout.addWidget(self._performance_grp())
        brow = QHBoxLayout()
        save_btn = QPushButton("Save Settings")
        save_btn.setObjectName("primaryButton")
        save_btn.clicked.connect(self._save)
        reset_btn = QPushButton("Reset Defaults")
        reset_btn.clicked.connect(self._reset)
        brow.addStretch()
        brow.addWidget(save_btn)
        brow.addWidget(reset_btn)
        layout.addLayout(brow)
        layout.addStretch()
        scroll.setWidget(content)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _detection_grp(self):
        g = QGroupBox("Detection Settings")
        f = QFormLayout(g)
        self.sensitivity = QSlider(Qt.Orientation.Horizontal)
        self.sensitivity.setRange(1, 10)
        self.sensitivity.setValue(7)
        f.addRow("Sensitivity:", self.sensitivity)
        self.cooldown = QSpinBox()
        self.cooldown.setRange(1, 300)
        self.cooldown.setValue(SETTINGS["ALERT_COOLDOWN_SECONDS"])
        self.cooldown.setSuffix(" seconds")
        f.addRow("Alert Cooldown:", self.cooldown)
        return g

    def _alert_grp(self):
        g = QGroupBox("Alert Settings")
        f = QFormLayout(g)
        self.popup_chk   = QCheckBox("Enable popup alerts")
        self.popup_chk.setChecked(True)
        self.overlay_chk = QCheckBox("Enable screen overlay (red border)")
        self.overlay_chk.setChecked(True)
        self.tray_chk    = QCheckBox("Show tray notifications")
        self.tray_chk.setChecked(True)
        f.addRow(self.popup_chk)
        f.addRow(self.overlay_chk)
        f.addRow(self.tray_chk)
        return g

    def _protection_grp(self):
        g = QGroupBox("Protection Settings")
        f = QFormLayout(g)
        self.blur_chk = QCheckBox("Auto-blur sensitive regions")
        self.blur_chk.setChecked(SETTINGS["AUTO_BLUR_ENABLED"])
        self.screenshot_chk = QCheckBox("Screenshot guard")
        self.screenshot_chk.setChecked(SETTINGS["SCREENSHOT_GUARD_ENABLED"])
        f.addRow(self.blur_chk)
        f.addRow(self.screenshot_chk)
        return g

    def _performance_grp(self):
        g = QGroupBox("Performance Settings")
        f = QFormLayout(g)
        self.npu_chk = QCheckBox("Use NPU acceleration (Snapdragon X)")
        self.npu_chk.setChecked(SETTINGS["USE_NPU_ACCELERATION"])
        self.interval = QSpinBox()
        self.interval.setRange(100, 5000)
        self.interval.setValue(SETTINGS["CAPTURE_INTERVAL_MS"])
        self.interval.setSuffix(" ms")
        f.addRow(self.npu_chk)
        f.addRow("Capture Interval:", self.interval)
        return g

    def _save(self):
        SETTINGS["ALERT_COOLDOWN_SECONDS"]   = self.cooldown.value()
        SETTINGS["AUTO_BLUR_ENABLED"]         = self.blur_chk.isChecked()
        SETTINGS["SCREENSHOT_GUARD_ENABLED"]  = self.screenshot_chk.isChecked()
        SETTINGS["USE_NPU_ACCELERATION"]      = self.npu_chk.isChecked()
        SETTINGS["CAPTURE_INTERVAL_MS"]       = self.interval.value()
        self.settings_changed.emit(SETTINGS)

    def _reset(self):
        self.cooldown.setValue(10)
        self.blur_chk.setChecked(True)
        self.screenshot_chk.setChecked(True)
        self.npu_chk.setChecked(True)
        self.interval.setValue(500)
        self.sensitivity.setValue(7)
