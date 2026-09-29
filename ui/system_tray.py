from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtGui import QIcon, QPixmap, QColor, QPainter, QFont, QPolygon
from PyQt6.QtCore import QPoint
from loguru import logger


class SystemTrayManager(QObject):
    open_dashboard    = pyqtSignal()
    scan_now          = pyqtSignal()
    toggle_monitoring = pyqtSignal(bool)
    quit_app          = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tray = None
        self.is_monitoring = True
        self.pause_action  = None
        self._build()

    def _build(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            logger.warning("System tray not available")
            return
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(self._icon("#2979FF"))
        self.tray.setToolTip("AI Guardian -- Privacy & Screen Safety")
        menu = QMenu()
        t = menu.addAction("AI Guardian")
        t.setEnabled(False)
        menu.addSeparator()
        menu.addAction("Open Dashboard").triggered.connect(self.open_dashboard)
        menu.addAction("Scan Now").triggered.connect(self.scan_now)
        menu.addSeparator()
        self.pause_action = menu.addAction("Pause Monitoring")
        self.pause_action.triggered.connect(self._toggle)
        menu.addSeparator()
        menu.addAction("Exit").triggered.connect(self.quit_app)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(
            lambda r: self.open_dashboard.emit()
            if r == QSystemTrayIcon.ActivationReason.DoubleClick
            else None
        )
        self.tray.show()

    def _icon(self, color: str) -> QIcon:
        pix = QPixmap(64, 64)
        pix.fill(QColor(0, 0, 0, 0))
        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QColor(color))
        p.setPen(QColor("#FFFFFF"))
        shield = QPolygon(
            [
                QPoint(32, 4),
                QPoint(60, 16),
                QPoint(60, 36),
                QPoint(32, 60),
                QPoint(4, 36),
                QPoint(4, 16),
            ]
        )
        p.drawPolygon(shield)
        p.setPen(QColor("#FFFFFF"))
        p.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        p.drawText(pix.rect(), 0x0004 | 0x0080, "G")
        p.end()
        return QIcon(pix)

    def _toggle(self):
        self.is_monitoring = not self.is_monitoring
        if self.pause_action:
            self.pause_action.setText(
                "Resume Monitoring"
                if not self.is_monitoring
                else "Pause Monitoring"
            )
        self.tray.setIcon(
            self._icon("#2979FF" if self.is_monitoring else "#8B949E")
        )
        self.toggle_monitoring.emit(self.is_monitoring)

    def show_notification(
        self, title: str, message: str, severity: str = "LOW"
    ):
        if not self.tray:
            return
        icon_map = {
            "CRITICAL": QSystemTrayIcon.MessageIcon.Critical,
            "HIGH":     QSystemTrayIcon.MessageIcon.Warning,
        }
        self.tray.showMessage(
            title,
            message,
            icon_map.get(severity, QSystemTrayIcon.MessageIcon.Information),
            5000,
        )

    def update_status(self, active: bool, alert: bool = False):
        if not self.tray:
            return
        color = "#FF1744" if alert else ("#2979FF" if active else "#8B949E")
        self.tray.setIcon(self._icon(color))
