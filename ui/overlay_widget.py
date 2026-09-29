from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QFont, QPen


class ScreenOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.WindowTransparentForInput
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        self.severity = None
        self.message = ""
        self.is_active = False
        self.pulse_val = 200
        self.pulse_dir = -1
        self.clear_timer = QTimer()
        self.clear_timer.setSingleShot(True)
        self.clear_timer.timeout.connect(self.clear_overlay)
        self.pulse_timer = QTimer()
        self.pulse_timer.timeout.connect(self._pulse)

    def show_warning(
        self, severity: str, message: str, duration_ms: int = 5000
    ):
        self.severity = severity
        self.message = message
        self.is_active = True
        self.clear_timer.start(duration_ms)
        self.pulse_timer.start(50)
        self.show()
        self.update()

    def paintEvent(self, event):
        if not self.is_active:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        color_map = {
            "CRITICAL": QColor(255, 23, 68),
            "HIGH":     QColor(255, 109, 0),
            "MEDIUM":   QColor(255, 214, 0),
            "LOW":      QColor(41, 121, 255),
        }
        color = color_map.get(self.severity, QColor(255, 109, 0))
        color.setAlpha(self.pulse_val)
        bw = {"CRITICAL": 8, "HIGH": 6, "MEDIUM": 4, "LOW": 2}.get(
            self.severity, 4
        )
        painter.setPen(QPen(color, bw))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(
            bw // 2, bw // 2, self.width() - bw, self.height() - bw
        )
        banner = QColor(color)
        banner.setAlpha(180)
        painter.fillRect(0, 0, self.width(), 55, banner)
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        painter.drawText(15, 35, f"AI GUARDIAN ALERT -- {self.message}")
        painter.end()

    def clear_overlay(self):
        self.is_active = False
        self.clear_timer.stop()
        self.pulse_timer.stop()
        self.hide()

    def _pulse(self):
        self.pulse_val += 8 * self.pulse_dir
        if self.pulse_val >= 230 or self.pulse_val <= 80:
            self.pulse_dir *= -1
        self.update()
