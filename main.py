import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication, QSplashScreen
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QColor, QFont, QPainter
from loguru import logger


def setup_logging():
    from config.settings import SETTINGS
    logger.remove()
    logger.add(
        sys.stdout,
        format=(
            "<green>{time:HH:mm:ss}</green> | "
            "<level>{level:<8}</level> | "
            "<cyan>{name}</cyan> -- "
            "<level>{message}</level>"
        ),
        level=SETTINGS["LOG_LEVEL"],
    )
    logger.add(
        SETTINGS["LOG_FILE"],
        rotation="10 MB",
        retention="7 days",
        level="DEBUG",
    )


def make_splash():
    pix = QPixmap(520, 300)
    pix.fill(QColor("#0D1117"))
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(QColor("#58A6FF"))
    p.setFont(QFont("Segoe UI", 30, QFont.Weight.Bold))
    p.drawText(40, 100, "AI Guardian")
    p.setPen(QColor("#8B949E"))
    p.setFont(QFont("Segoe UI", 13))
    p.drawText(40, 140, "Privacy & Screen Safety Agent")
    p.drawText(40, 168, "Powered by Qualcomm Snapdragon NPU")
    p.setPen(QColor("#238636"))
    p.setFont(QFont("Segoe UI", 10))
    p.drawText(40, 258, "Loading -- all processing is 100% local & private")
    p.end()
    splash = QSplashScreen(pix)
    splash.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
    return splash


def main():
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    app = QApplication(sys.argv)
    app.setApplicationName("AI Guardian")
    app.setApplicationVersion("1.0.0")
    app.setQuitOnLastWindowClosed(False)

    setup_logging()
    logger.info("=" * 50)
    logger.info("AI Guardian Starting")
    logger.info("=" * 50)

    splash = make_splash()
    splash.show()
    app.processEvents()

    try:
        from models.model_manager import ModelManager
        ModelManager().ensure_models_available()
    except Exception as e:
        logger.warning(f"Model preload skipped: {e}")

    from ui.main_window import MainWindow
    window = MainWindow()

    def show():
        splash.finish(window)
        window.show()
        logger.success(
            "AI Guardian running! Monitoring is 100% local & private."
        )

    QTimer.singleShot(2200, show)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
