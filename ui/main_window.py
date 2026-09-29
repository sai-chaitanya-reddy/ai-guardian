from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStatusBar, QFrame, QApplication, QTextEdit,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot, QObject, pyqtSignal
from PyQt6.QtGui import QFont, QCloseEvent
from loguru import logger

from ui.dashboard        import SecurityDashboard
from ui.settings_panel   import SettingsPanel
from ui.alert_popup      import AlertPopup
from ui.overlay_widget   import ScreenOverlay
from ui.system_tray      import SystemTrayManager
from core.screen_capture      import ScreenCaptureEngine
from core.sensitive_detector  import SensitiveDetector, DetectionEvent
from core.npu_accelerator     import NPUAccelerator
from security.event_logger    import SecurityEventLogger
from security.redactor        import ScreenRedactor
from security.screenshot_guard import ScreenshotGuard


class _Bridge(QObject):
    sig = pyqtSignal(object)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.npu             = NPUAccelerator()
        self.event_logger    = SecurityEventLogger()
        self.redactor        = ScreenRedactor()
        self.screenshot_guard = ScreenshotGuard(
            on_screenshot_attempt=self._on_screenshot
        )
        self._bridge = _Bridge()
        self._bridge.sig.connect(self._handle_detection)
        self.detector = SensitiveDetector(
            on_detection_callback=self._bridge.sig.emit
        )
        self.capture_engine = ScreenCaptureEngine(
            on_frame_callback=self._on_frame
        )
        self.alert_popup    = AlertPopup()
        self.screen_overlay = ScreenOverlay()
        self.tray_manager   = None
        self.is_monitoring  = False
        self.detection_count = 0
        self._build_ui()
        self._build_tray()
        self._apply_theme()
        self._start()

    # ── UI BUILD ──────────────────────────────────────────────

    def _build_ui(self):
        self.setWindowTitle("AI Guardian -- Privacy & Screen Safety")
        self.setMinimumSize(900, 620)
        self.resize(1200, 750)

        central = QWidget()
        self.setCentralWidget(central)
        ml = QVBoxLayout(central)
        ml.setContentsMargins(0, 0, 0, 0)
        ml.setSpacing(0)
        ml.addWidget(self._header())

        self.tabs = QTabWidget()
        self.dashboard      = SecurityDashboard(self.event_logger, self.npu)
        self.settings_panel = SettingsPanel()

        self.tabs.addTab(self.dashboard,       "  Dashboard  ")
        self.tabs.addTab(self._live_tab(),     "  Live Monitor  ")
        self.tabs.addTab(self.settings_panel,  "  Settings  ")
        self.tabs.addTab(self._about_tab(),    "  About  ")
        ml.addWidget(self.tabs)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self._update_status()

    def _header(self):
        f = QFrame()
        f.setFixedHeight(60)
        f.setStyleSheet(
            "background:#161B22;border-bottom:1px solid #30363D;"
        )
        lay = QHBoxLayout(f)
        lay.setContentsMargins(20, 0, 20, 0)

        logo = QLabel("AI Guardian")
        logo.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        logo.setStyleSheet("color:#58A6FF;")

        sub = QLabel("On-Device Privacy & Screen Safety")
        sub.setStyleSheet("color:#8B949E;font-size:12px;")

        self.mon_btn = QPushButton("Pause")
        self.mon_btn.clicked.connect(self._toggle_monitoring)

        scan_btn = QPushButton("Scan Now")
        scan_btn.clicked.connect(self._manual_scan)

        npu = self.npu.get_status_info()
        npu_color = "#238636" if npu["available"] else "#8B949E"
        npu_lbl = QLabel(npu["status"])
        npu_lbl.setStyleSheet(
            "background:{};color:#fff;"
            "border-radius:4px;padding:4px 10px;"
            "font-size:11px;font-weight:bold;".format(npu_color)
        )

        lay.addWidget(logo)
        lay.addWidget(sub)
        lay.addStretch()
        lay.addWidget(self.mon_btn)
        lay.addWidget(scan_btn)
        lay.addWidget(npu_lbl)
        return f

    def _live_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(16, 16, 16, 16)

        sf = QFrame()
        sf.setStyleSheet(
            "background:#161B22;border:1px solid #30363D;border-radius:8px;"
        )
        sfl = QVBoxLayout(sf)

        self.live_status = QLabel("Monitoring Active")
        self.live_status.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.live_status.setStyleSheet("color:#238636;")
        self.live_status.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.frames_lbl = QLabel("Frames analyzed: 0")
        self.frames_lbl.setStyleSheet("color:#8B949E;")
        self.frames_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.detect_lbl = QLabel("Detections: 0")
        self.detect_lbl.setStyleSheet("color:#C9D1D9;")
        self.detect_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sfl.addWidget(self.live_status)
        sfl.addWidget(self.frames_lbl)
        sfl.addWidget(self.detect_lbl)
        lay.addWidget(sf)

        log_lbl = QLabel("Recent Detections:")
        log_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        log_lbl.setStyleSheet("color:#C9D1D9;margin-top:12px;")
        lay.addWidget(log_lbl)

        self.live_log = QTextEdit()
        self.live_log.setReadOnly(True)
        self.live_log.setMaximumHeight(300)
        self.live_log.setStyleSheet(
            "background:#161B22;color:#C9D1D9;"
            "border:1px solid #30363D;border-radius:6px;"
            "font-family:Consolas,monospace;font-size:12px;"
        )
        lay.addWidget(self.live_log)
        lay.addStretch()

        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self._update_live_stats)
        self.stats_timer.start(2000)
        return w

    def _about_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(30, 30, 30, 30)
        lbl = QLabel(
            "<h2 style='color:#58A6FF;'>AI Guardian v1.0</h2>"
            "<p style='color:#C9D1D9;'>On-Device Privacy and Screen Safety Agent</p><br>"
            "<p style='color:#8B949E;'>"
            "Built for the <b style='color:#58A6FF;'>"
            "Qualcomm Snapdragon X Developer Challenge</b><br><br>"
            "<b style='color:#C9D1D9;'>Detects:</b><br>"
            "API Keys (AWS, OpenAI, GitHub, Google, Stripe)<br>"
            "Passwords in terminals and env files<br>"
            "Credit card numbers on screen<br>"
            "Private SSH and SSL keys<br>"
            "JWT tokens and database connection strings<br><br>"
            "<b style='color:#C9D1D9;'>Snapdragon NPU:</b><br>"
            "Uses QNNExecutionProvider in ONNX Runtime<br>"
            "Always-on with low power consumption<br>"
            "100% local -- nothing leaves your device<br>"
            "</p>"
        )
        lbl.setWordWrap(True)
        lbl.setTextFormat(Qt.TextFormat.RichText)
        lay.addWidget(lbl)
        lay.addStretch()
        return w

    def _build_tray(self):
        self.tray_manager = SystemTrayManager()
        self.tray_manager.open_dashboard.connect(self.show)
        self.tray_manager.scan_now.connect(self._manual_scan)
        self.tray_manager.quit_app.connect(self._quit)

    def _apply_theme(self):
        from pathlib import Path
        p = Path("assets/styles/dark_theme.qss")
        if p.exists():
            self.setStyleSheet(p.read_text())

    # ── DETECTION ─────────────────────────────────────────────

    def _on_frame(self, frame, timestamp):
        self.detector.analyze_frame(frame, timestamp)

    @pyqtSlot(object)
    def _handle_detection(self, event: DetectionEvent):
        self.detection_count += 1
        self.event_logger.log_event(event)

        self.screenshot_guard.set_sensitive_mode(True)
        QTimer.singleShot(
            30000,
            lambda: self.screenshot_guard.set_sensitive_mode(False)
        )

        self.alert_popup.show_alert(event)
        self.screen_overlay.show_warning(event.severity, event.alert_message)

        if event.severity in ("CRITICAL", "HIGH") and self.tray_manager:
            self.tray_manager.show_notification(
                "AI Guardian -- Sensitive Content Detected",
                event.alert_message,
                event.severity,
            )
            self.tray_manager.update_status(True, alert=True)
            QTimer.singleShot(
                5000,
                lambda: self.tray_manager.update_status(True)
            )

        ts = datetime.now().strftime("%H:%M:%S")
        self.live_log.append(
            '<span style="color:#8B949E;">[{}]</span> '
            '<span style="color:#FF1744;font-weight:bold;">'
            '{}</span> -- '
            '<span style="color:#C9D1D9;">{}</span>'.format(
                ts, event.severity, event.alert_message
            )
        )

        self.dashboard.refresh_data()
        self._update_status()

    def _on_screenshot(self, method, message):
        if self.tray_manager:
            self.tray_manager.show_notification(
                "Screenshot Blocked", message, "HIGH"
            )

    # ── CONTROLS ──────────────────────────────────────────────

    def _start(self):
        self.capture_engine.start()
        self.is_monitoring = True
        self.screenshot_guard.activate()
        self._update_status()
        logger.info("AI Guardian monitoring started")

    def _stop(self):
        self.capture_engine.stop()
        self.is_monitoring = False
        self.screenshot_guard.deactivate()
        self._update_status()

    def _toggle_monitoring(self):
        if self.is_monitoring:
            self._stop()
            self.mon_btn.setText("Resume")
            self.live_status.setText("Monitoring Paused")
            self.live_status.setStyleSheet("color:#8B949E;")
        else:
            self._start()
            self.mon_btn.setText("Pause")
            self.live_status.setText("Monitoring Active")
            self.live_status.setStyleSheet("color:#238636;")

    def _manual_scan(self):
        frame = self.capture_engine.capture_single_frame()
        if frame is not None:
            self.detector.analyze_frame(frame, datetime.now())

    def _update_live_stats(self):
        s = self.detector.get_stats()
        self.frames_lbl.setText(
            "Frames analyzed: {}".format(s["frames_analyzed"])
        )
        self.detect_lbl.setText(
            "Detections: {}".format(s["detections"])
        )
        safe = s["frames_analyzed"] - s["detections"]
        if hasattr(self.dashboard, "update_safe_count"):
            self.dashboard.update_safe_count(max(0, safe))

    def _update_status(self):
        s   = "Monitoring" if self.is_monitoring else "Paused"
        npu = self.npu.get_status_info()["status"]
        self.status_bar.showMessage(
            "{}  |  {}  |  Detections: {}  |  100% Local & Private".format(
                s, npu, self.detection_count
            )
        )

    # ── WINDOW EVENTS ─────────────────────────────────────────

    def closeEvent(self, event: QCloseEvent):
        event.ignore()
        self.hide()
        if self.tray_manager:
            self.tray_manager.show_notification(
                "AI Guardian",
                "Still running in system tray. Right-click to exit.",
            )

    def _quit(self):
        self._stop()
        self.event_logger.close()
        QApplication.quit()
