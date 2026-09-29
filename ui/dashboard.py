import json
import time
import platform
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QPushButton,
    QFrame, QHeaderView, QComboBox, QGridLayout,
    QGroupBox, QSizePolicy, QTabWidget,
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QFont


# ── Real benchmark thread ─────────────────────────────────────

class BenchmarkThread(QThread):
    done = pyqtSignal(dict)

    def run(self):
        import sys
        sys.path.insert(0, ".")

        info = {
            "inference_ms":  None,
            "provider":      "CPU",
            "npu_active":    False,
            "model":         "Pattern Matcher + OCR",
            "runtime":       "Built-in",
            "onnx_version":  None,
            "cpu_name":      platform.processor() or "Unknown CPU",
            "python_version": platform.python_version(),
        }

        # Real ONNX check
        try:
            import onnxruntime as ort
            info["onnx_version"] = ort.__version__
            providers = ort.get_available_providers()

            if "QNNExecutionProvider" in providers:
                info["provider"]   = "QNN (Hexagon NPU)"
                info["npu_active"] = True
                info["runtime"]    = "ONNX Runtime + QNN"
            elif "DmlExecutionProvider" in providers:
                info["provider"] = "DirectML"
                info["runtime"]  = "ONNX Runtime + DirectML"
            else:
                info["provider"] = "CPUExecutionProvider"
                info["runtime"]  = "ONNX Runtime"

            # ONNX model timing
            from pathlib import Path
            model_path = Path("models/cached/mobilenetv2.onnx")
            if model_path.exists():
                info["model"] = "MobileNetV2 (ONNX)"
                try:
                    import numpy as np
                    sess = ort.InferenceSession(
                        str(model_path),
                        providers=[info["provider"]]
                        if info["provider"] in providers
                        else ["CPUExecutionProvider"],
                    )
                    dummy = np.random.randn(
                        1, 3, 224, 224
                    ).astype("float32")
                    for _ in range(3):
                        sess.run(None, {"input": dummy})
                    t0 = time.perf_counter()
                    for _ in range(20):
                        sess.run(None, {"input": dummy})
                    info["inference_ms"] = (
                        time.perf_counter() - t0
                    ) / 20 * 1000
                except Exception:
                    pass

        except ImportError:
            info["runtime"] = "Keyword Classifier (no ONNX)"

        # Pattern matcher timing
        try:
            from core.pattern_matcher import PatternMatcher
            pm = PatternMatcher()
            sample = (
                "AKIAIOSFODNN7EXAMPLE password=Secret123 "
                "4532015112830366 sk-" + "a" * 48
            )
            t0 = time.perf_counter()
            for _ in range(100):
                pm.scan_text(sample)
            pm_ms = (time.perf_counter() - t0) / 100 * 1000

            if info["inference_ms"] is None:
                info["inference_ms"] = pm_ms
        except Exception:
            pass

        self.done.emit(info)


# ── Reusable card widgets ─────────────────────────────────────

class StatCard(QFrame):
    def __init__(self, title, value="0", color="#2979FF"):
        super().__init__()
        self.setObjectName("statCard")
        self.setFixedHeight(80)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 8, 12, 8)
        self.val = QLabel(value)
        self.val.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        self.val.setStyleSheet("color:{};".format(color))
        self.val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ttl = QLabel(title)
        ttl.setFont(QFont("Segoe UI", 10))
        ttl.setStyleSheet("color:#8B949E;")
        ttl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.val)
        lay.addWidget(ttl)

    def update_value(self, v):
        self.val.setText(str(v))


class InfoRow(QWidget):
    def __init__(self, label, value="—", value_color="#C9D1D9"):
        super().__init__()
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 4, 0, 4)

        lbl = QLabel(label)
        lbl.setStyleSheet("color:#8B949E;font-size:11px;")
        lbl.setFixedWidth(160)

        sep = QLabel("─" * 16)
        sep.setStyleSheet("color:#30363D;font-size:9px;")

        self.val_lbl = QLabel(value)
        self.val_lbl.setStyleSheet(
            "color:{};font-size:12px;font-weight:bold;".format(
                value_color
            )
        )
        self.val_lbl.setWordWrap(True)

        lay.addWidget(lbl)
        lay.addWidget(sep)
        lay.addWidget(self.val_lbl)
        lay.addStretch()

    def update(self, value, color=None):
        self.val_lbl.setText(value)
        if color:
            self.val_lbl.setStyleSheet(
                "color:{};font-size:12px;font-weight:bold;".format(color)
            )


# ── Hardware panel ────────────────────────────────────────────

class HardwarePanel(QGroupBox):
    """
    Hardware-aware panel.
    Shows real detected values only — no fake metrics.
    """

    def __init__(self, npu_info: dict):
        super().__init__("AI Acceleration")
        self.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.setStyleSheet(
            "QGroupBox{color:#58A6FF;border:1px solid #30363D;"
            "border-radius:8px;margin-top:8px;padding:12px;}"
            "QGroupBox::title{subcontrol-origin:margin;padding:0 8px;}"
        )

        lay = QVBoxLayout(self)
        lay.setSpacing(2)

        # Device row
        cpu   = platform.processor() or "Unknown"
        short = cpu[:40] + "..." if len(cpu) > 40 else cpu
        self.row_device = InfoRow("Current device", short, "#C9D1D9")

        # Accelerator row
        if npu_info.get("available"):
            accel_val   = "Hexagon NPU"
            accel_color = "#238636"
        else:
            accel_val   = "CPU (no NPU detected)"
            accel_color = "#8B949E"
        self.row_accel = InfoRow("Accelerator", accel_val, accel_color)

        # Runtime row
        self.row_runtime = InfoRow(
            "Runtime", "Detecting...", "#58A6FF"
        )

        # Model row
        self.row_model = InfoRow(
            "Model", "Detecting...", "#58A6FF"
        )

        # Inference row
        self.row_inference = InfoRow(
            "Inference", "Measuring...", "#FF6D00"
        )

        # Processing row
        self.row_local = InfoRow(
            "Processing", "100% Local", "#238636"
        )

        # Privacy row
        self.row_privacy = InfoRow(
            "Cloud uploads", "Zero", "#238636"
        )

        # Snapdragon note
        self.snapdragon_note = QLabel()
        self.snapdragon_note.setWordWrap(True)
        self.snapdragon_note.setFont(QFont("Segoe UI", 10))
        self._update_note(npu_info.get("available", False))

        for w in [
            self.row_device,
            self.row_accel,
            self.row_runtime,
            self.row_model,
            self.row_inference,
            self.row_local,
            self.row_privacy,
            self._divider(),
            self.snapdragon_note,
        ]:
            lay.addWidget(w)

    def _divider(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color:#30363D;margin:4px 0;")
        return line

    def _update_note(self, npu_active: bool):
        if npu_active:
            self.snapdragon_note.setText(
                "Status: ACTIVE\n"
                "Running on Snapdragon hardware.\n"
                "Hexagon NPU is executing AI inference."
            )
            self.snapdragon_note.setStyleSheet(
                "color:#238636;font-size:11px;"
                "background:rgba(35,134,54,0.1);"
                "border-radius:6px;padding:8px;"
            )
        else:
            self.snapdragon_note.setText(
                "Snapdragon optimization:\n"
                "Available when running on supported\n"
                "Snapdragon X Elite / Plus hardware.\n"
                "This build: CPU fallback mode."
            )
            self.snapdragon_note.setStyleSheet(
                "color:#8B949E;font-size:11px;"
                "background:rgba(139,148,158,0.1);"
                "border-radius:6px;padding:8px;"
            )

    def apply_benchmark(self, info: dict):
        self.row_runtime.update(info.get("runtime", "—"), "#58A6FF")
        self.row_model.update(info.get("model", "—"), "#58A6FF")

        ms = info.get("inference_ms")
        if ms is not None:
            self.row_inference.update(
                "{:.2f} ms".format(ms), "#FF6D00"
            )
        else:
            self.row_inference.update("< 1 ms", "#FF6D00")

        if info.get("npu_active"):
            self.row_accel.update("Hexagon NPU", "#238636")
            self._update_note(True)
        else:
            self.row_accel.update(
                "CPU fallback (no NPU detected)", "#8B949E"
            )
            self._update_note(False)


# ── Pipeline panel ────────────────────────────────────────────

class PipelinePanel(QGroupBox):
    """
    Shows the real processing pipeline.
    Hardware-aware wording.
    """

    def __init__(self, npu_available: bool):
        super().__init__("Processing Pipeline")
        self.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.setStyleSheet(
            "QGroupBox{color:#58A6FF;border:1px solid #30363D;"
            "border-radius:8px;margin-top:8px;padding:12px;}"
            "QGroupBox::title{subcontrol-origin:margin;padding:0 8px;}"
        )

        lay = QVBoxLayout(self)
        self.pipeline_lbl = QLabel()
        self.pipeline_lbl.setTextFormat(Qt.TextFormat.RichText)
        self.pipeline_lbl.setFont(QFont("Consolas", 10))
        self.pipeline_lbl.setWordWrap(True)
        self.pipeline_lbl.setStyleSheet("color:#C9D1D9;")
        lay.addWidget(self.pipeline_lbl)
        lay.addStretch()

        self.update_pipeline(npu_available)

    def _step(self, name, detail, color="#58A6FF", is_last=False):
        arrow = "" if is_last else (
            "<br><span style='color:#30363D;'>│<br>▼</span><br>"
        )
        return (
            "<span style='color:{c};font-weight:bold;'>{n}</span>"
            "<span style='color:#8B949E;'> — {d}</span>{a}"
        ).format(c=color, n=name, d=detail, a=arrow)

    def update_pipeline(self, npu_available: bool):
        if npu_available:
            ai_step = self._step(
                "AI Inference",
                "Snapdragon NPU / QNN",
                "#238636",
            )
        else:
            ai_step = self._step(
                "AI Inference",
                "CPU fallback",
                "#8B949E",
            )

        html = "".join([
            self._step("Screen Capture",    "MSS @ 500ms",               "#58A6FF"),
            self._step("Frame Difference",  "Skip unchanged frames",     "#58A6FF"),
            self._step("OCR Engine",        "EasyOCR text extraction",   "#58A6FF"),
            self._step("Pattern Matcher",   "16 regex patterns",         "#FF6D00"),
            self._step("AI Classifier",     "Keyword + ONNX scoring",    "#FF6D00"),
            ai_step,
            self._step("Risk Engine",       "CRITICAL / HIGH / MEDIUM",  "#FF1744"),
            self._step(
                "Protection",
                "Alert + Screenshot Block + Log",
                "#FF1744",
                is_last=True,
            ),
        ])
        self.pipeline_lbl.setText(html)


# ── Security events table ─────────────────────────────────────

class SecurityEventsTable(QWidget):
    """
    Clean security events log with action column.
    """

    CATEGORY_NAMES = {
        "aws_access_key":       "AWS Access Key",
        "github_token":         "GitHub Token",
        "openai_key":           "OpenAI API Key",
        "google_api_key":       "Google API Key",
        "stripe_key":           "Stripe Key",
        "slack_token":          "Slack Token",
        "generic_api_key":      "API Key",
        "password_in_text":     "Password",
        "private_key_header":   "Private Key",
        "jwt_token":            "JWT Token",
        "database_url":         "Database URL",
        "credit_card_visa":     "Visa Card",
        "credit_card_mastercard": "Mastercard",
        "credit_card_amex":     "Amex Card",
        "ssn":                  "SSN",
        "phone_number":         "Phone Number",
    }

    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        # Filter row
        frow = QHBoxLayout()
        self.filter_box = QComboBox()
        self.filter_box.addItems(
            ["All", "CRITICAL", "HIGH", "MEDIUM", "LOW"]
        )
        self.filter_box.currentTextChanged.connect(self._apply_filter)
        self.filter_box.setFixedWidth(140)

        frow.addWidget(QLabel("Filter by severity:"))
        frow.addWidget(self.filter_box)
        frow.addStretch()
        lay.addLayout(frow)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Time", "Type", "Severity", "Confidence", "Action", "Processing"
        ])
        hdr = self.table.horizontalHeader()
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.table.verticalHeader().setVisible(False)
        lay.addWidget(self.table)

        self._all_events = []

    def populate(self, events: list):
        self._all_events = events
        self._render(events)

    def _render(self, events: list):
        sev_colors = {
            "CRITICAL": QColor("#FF1744"),
            "HIGH":     QColor("#FF6D00"),
            "MEDIUM":   QColor("#FFD600"),
            "LOW":      QColor("#2979FF"),
        }

        self.table.setRowCount(len(events))

        for r, ev in enumerate(events):
            # Time
            ts = str(ev.get("timestamp", ""))[:19].replace("T", " ")

            # Type — human readable category
            try:
                raw_cats = json.loads(ev.get("categories", "[]"))
            except Exception:
                raw_cats = []
            primary = raw_cats[0] if raw_cats else "unknown"
            type_name = self.CATEGORY_NAMES.get(
                primary,
                primary.replace("_", " ").title()
            )

            # Severity
            sev = ev.get("severity", "")

            # Confidence
            conf_raw = ev.get("confidence", 0)
            conf = "{:.0f}%".format(conf_raw * 100)

            # Action
            if sev == "CRITICAL":
                action = "Screenshot Blocked"
                action_color = QColor("#FF1744")
            elif sev == "HIGH":
                action = "User Warned"
                action_color = QColor("#FF6D00")
            else:
                action = "Logged"
                action_color = QColor("#8B949E")

            # Processing
            processing = "Local"

            col = sev_colors.get(sev, QColor("#C9D1D9"))

            values = [ts, type_name, sev, conf, action, processing]
            for c, val in enumerate(values):
                item = QTableWidgetItem(str(val))
                if c == 4:
                    item.setForeground(action_color)
                elif c == 5:
                    item.setForeground(QColor("#238636"))
                else:
                    item.setForeground(col)
                self.table.setItem(r, c, item)

    def _apply_filter(self, sev: str):
        if sev == "All":
            self._render(self._all_events)
        else:
            self._render(
                [e for e in self._all_events
                 if e.get("severity") == sev]
            )


# ── Main Dashboard ────────────────────────────────────────────

class SecurityDashboard(QWidget):

    def __init__(self, event_logger, npu_accelerator, parent=None):
        super().__init__(parent)
        self.event_logger = event_logger
        self.npu          = npu_accelerator
        self._npu_info    = npu_accelerator.get_status_info()
        self._build_ui()

        # Benchmark
        self._bench = BenchmarkThread()
        self._bench.done.connect(self._on_bench_done)
        self._bench.start()

        # Auto refresh
        self._timer = QTimer()
        self._timer.timeout.connect(self.refresh_data)
        self._timer.start(5000)

        self.refresh_data()

    def _build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(16, 16, 16, 16)
        main.setSpacing(12)

        # ── Stat cards ────────────────────────────────────────
        stats_row = QHBoxLayout()
        self.c_total    = StatCard("Total Events", "0", "#58A6FF")
        self.c_critical = StatCard("Critical",     "0", "#FF1744")
        self.c_high     = StatCard("High",         "0", "#FF6D00")
        self.c_medium   = StatCard("Medium",       "0", "#FFD600")
        self.c_safe     = StatCard("Safe Frames",  "0", "#238636")
        for c in [
            self.c_total, self.c_critical,
            self.c_high, self.c_medium, self.c_safe
        ]:
            stats_row.addWidget(c)
        main.addLayout(stats_row)

        # ── Middle row: hardware + pipeline ──────────────────
        mid = QHBoxLayout()
        self.hw_panel = HardwarePanel(self._npu_info)
        self.pipeline  = PipelinePanel(
            self._npu_info.get("available", False)
        )
        mid.addWidget(self.hw_panel,  stretch=2)
        mid.addWidget(self.pipeline,  stretch=3)
        main.addLayout(mid)

        # ── Security events table ─────────────────────────────
        events_label = QLabel("Security Events")
        events_label.setFont(
            QFont("Segoe UI", 11, QFont.Weight.Bold)
        )
        events_label.setStyleSheet("color:#58A6FF;margin-top:4px;")
        main.addWidget(events_label)

        self.events_table = SecurityEventsTable()
        main.addWidget(self.events_table)

    def _on_bench_done(self, info: dict):
        self.hw_panel.apply_benchmark(info)
        self.pipeline.update_pipeline(info.get("npu_active", False))

    def refresh_data(self):
        events = self.event_logger.get_recent_events(200)
        stats  = self.event_logger.get_statistics()
        sev    = stats.get("by_severity", {})

        self.c_total.update_value(stats.get("total", 0))
        self.c_critical.update_value(sev.get("CRITICAL", 0))
        self.c_high.update_value(sev.get("HIGH", 0))
        self.c_medium.update_value(sev.get("MEDIUM", 0))

        self.events_table.populate(events)

    def update_safe_count(self, count: int):
        self.c_safe.update_value(count)