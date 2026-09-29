from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame, QGridLayout,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import QApplication


CATEGORY_META = {
    "aws_access_key":     ("AWS Access Key",          "Cloud Credential"),
    "github_token":       ("GitHub Token",             "Source Control Credential"),
    "openai_key":         ("OpenAI API Key",           "AI Service Credential"),
    "google_api_key":     ("Google API Key",           "Cloud Credential"),
    "stripe_key":         ("Stripe Secret Key",        "Payment Credential"),
    "slack_token":        ("Slack Token",              "Communication Credential"),
    "generic_api_key":    ("API Key",                  "Service Credential"),
    "password_in_text":   ("Password",                 "Authentication Secret"),
    "private_key_header": ("Private Key",              "Cryptographic Secret"),
    "jwt_token":          ("JWT Token",                "Authentication Token"),
    "database_url":       ("Database Connection",      "Infrastructure Secret"),
    "credit_card_visa":   ("Visa Card Number",         "Financial Data"),
    "credit_card_mastercard": ("Mastercard Number",    "Financial Data"),
    "credit_card_amex":   ("Amex Card Number",         "Financial Data"),
    "ssn":                ("Social Security Number",   "Personal Identity Data"),
    "phone_number":       ("Phone Number",             "Personal Data"),
}


class AlertPopup(QWidget):
    dismissed = pyqtSignal()

    SEVERITY_STYLE = {
        "CRITICAL": {
            "bg":     "#1a0000",
            "border": "#FF1744",
            "header": "#FF1744",
            "text":   "#FFFFFF",
            "badge":  "#FF1744",
            "label":  "CRITICAL PRIVACY ALERT",
        },
        "HIGH": {
            "bg":     "#1a0a00",
            "border": "#FF6D00",
            "header": "#FF6D00",
            "text":   "#FFFFFF",
            "badge":  "#FF6D00",
            "label":  "HIGH RISK ALERT",
        },
        "MEDIUM": {
            "bg":     "#1a1500",
            "border": "#FFD600",
            "header": "#FFD600",
            "text":   "#FFFFFF",
            "badge":  "#FFD600",
            "label":  "PRIVACY WARNING",
        },
        "LOW": {
            "bg":     "#000d1a",
            "border": "#2979FF",
            "header": "#2979FF",
            "text":   "#FFFFFF",
            "badge":  "#2979FF",
            "label":  "PRIVACY NOTICE",
        },
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setFixedWidth(460)
        self._build_ui()
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.dismiss)

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        self.frame = QFrame()
        self.frame.setObjectName("alertFrame")
        outer.addWidget(self.frame)

        layout = QVBoxLayout(self.frame)
        layout.setContentsMargins(0, 0, 0, 16)
        layout.setSpacing(0)

        # ── Header bar ────────────────────────────────────────
        self.header_bar = QFrame()
        self.header_bar.setFixedHeight(44)
        header_layout = QHBoxLayout(self.header_bar)
        header_layout.setContentsMargins(16, 0, 12, 0)

        self.header_lbl = QLabel("CRITICAL PRIVACY ALERT")
        self.header_lbl.setFont(
            QFont("Segoe UI", 11, QFont.Weight.Bold)
        )
        self.header_lbl.setStyleSheet("color:#FFFFFF;")

        close_btn = QPushButton("X")
        close_btn.setFixedSize(26, 26)
        close_btn.setStyleSheet(
            "QPushButton{background:rgba(255,255,255,0.15);"
            "border:none;border-radius:13px;"
            "color:white;font-size:12px;font-weight:bold;}"
            "QPushButton:hover{background:rgba(255,255,255,0.3);}"
        )
        close_btn.clicked.connect(self.dismiss)

        header_layout.addWidget(self.header_lbl)
        header_layout.addStretch()
        header_layout.addWidget(close_btn)
        layout.addWidget(self.header_bar)

        # ── Detected name ─────────────────────────────────────
        body = QVBoxLayout()
        body.setContentsMargins(16, 12, 16, 0)
        body.setSpacing(12)

        self.detected_lbl = QLabel("AWS Access Key Detected")
        self.detected_lbl.setFont(
            QFont("Segoe UI", 15, QFont.Weight.Bold)
        )
        self.detected_lbl.setStyleSheet("color:#FFFFFF;")
        self.detected_lbl.setWordWrap(True)
        body.addWidget(self.detected_lbl)

        # ── Details grid ──────────────────────────────────────
        grid_frame = QFrame()
        grid_frame.setStyleSheet(
            "background:rgba(255,255,255,0.05);"
            "border-radius:8px;"
        )
        grid = QGridLayout(grid_frame)
        grid.setContentsMargins(12, 10, 12, 10)
        grid.setSpacing(8)

        self._detail_rows = {}
        fields = [
            ("Category",   "category"),
            ("Confidence", "confidence"),
            ("Source",     "source"),
            ("Action",     "action"),
            ("Processing", "processing"),
        ]

        for row, (label, key) in enumerate(fields):
            lbl = QLabel(label)
            lbl.setStyleSheet(
                "color:#8B949E;font-size:11px;font-weight:bold;"
            )
            lbl.setFont(QFont("Segoe UI", 10))

            val = QLabel("—")
            val.setStyleSheet(
                "color:#FFFFFF;font-size:11px;"
            )
            val.setFont(QFont("Segoe UI", 10))
            val.setWordWrap(True)

            grid.addWidget(lbl, row, 0)
            grid.addWidget(val, row, 1)
            self._detail_rows[key] = val

        body.addWidget(grid_frame)

        # ── Dismiss button ────────────────────────────────────
        btn_row = QHBoxLayout()
        self.dismiss_btn = QPushButton("Dismiss")
        self.dismiss_btn.setFixedHeight(34)
        self.dismiss_btn.setStyleSheet(
            "QPushButton{background:rgba(255,255,255,0.1);"
            "border:1px solid rgba(255,255,255,0.2);"
            "border-radius:6px;color:#FFFFFF;"
            "font-size:12px;padding:0 20px;}"
            "QPushButton:hover{background:rgba(255,255,255,0.2);}"
        )
        self.dismiss_btn.clicked.connect(self.dismiss)
        btn_row.addStretch()
        btn_row.addWidget(self.dismiss_btn)
        body.addLayout(btn_row)

        layout.addLayout(body)

    def show_alert(self, event, duration_ms: int = 10000):
        sev   = getattr(event, "severity", "HIGH")
        style = self.SEVERITY_STYLE.get(sev, self.SEVERITY_STYLE["HIGH"])

        # Get primary category metadata
        cats     = event.categories if event.categories else []
        primary  = cats[0] if cats else "unknown"
        meta     = CATEGORY_META.get(primary, (
            primary.replace("_", " ").title(), "Sensitive Data"
        ))
        name, category_type = meta

        # Confidence from matched patterns
        confidence = 0.0
        if hasattr(event, "matched_patterns") and event.matched_patterns:
            confidence = max(
                m.confidence for m in event.matched_patterns
            )
        elif hasattr(event, "confidence"):
            confidence = event.confidence

        conf_str = "{:.1f}%".format(confidence * 100) if confidence > 0 \
                   else "High"

        # Determine action taken
        action = "Screenshot Blocked + User Warned"
        if sev == "MEDIUM":
            action = "User Warned"
        elif sev == "LOW":
            action = "Logged"

        # Update UI
        self.header_lbl.setText(style["label"])
        self.detected_lbl.setText("{} Detected".format(name))

        self._detail_rows["category"].setText(category_type)
        self._detail_rows["confidence"].setText(conf_str)
        self._detail_rows["source"].setText("Screen Capture (Local)")
        self._detail_rows["action"].setText(action)
        self._detail_rows["processing"].setText("100% On-Device")

        # Action value color
        action_color = "#FF1744" if "Blocked" in action else "#FFD600"
        self._detail_rows["action"].setStyleSheet(
            "color:{};font-size:11px;font-weight:bold;".format(
                action_color
            )
        )

        # Apply style
        self.frame.setStyleSheet(
            "QFrame#alertFrame{{"
            "background-color:{bg};"
            "border:2px solid {border};"
            "border-radius:12px;}}"
            "QLabel{{background:transparent;}}".format(**style)
        )
        self.header_bar.setStyleSheet(
            "background:{header};border-radius:10px 10px 0 0;".format(
                **style
            )
        )

        # Position top-right
        screen = QApplication.primaryScreen().availableGeometry()
        self.adjustSize()
        self.move(
            screen.right() - self.width() - 20,
            screen.top() + 20
        )

        self._timer.start(duration_ms)
        self.show()
        self.raise_()

    def dismiss(self):
        self._timer.stop()
        self.hide()
        self.dismissed.emit()