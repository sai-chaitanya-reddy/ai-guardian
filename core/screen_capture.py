import mss
import numpy as np
import cv2
import threading
import time
from datetime import datetime
from loguru import logger
from config.settings import SETTINGS


class ScreenCaptureEngine:
    def __init__(self, on_frame_callback=None):
        self.on_frame_callback = on_frame_callback
        self.running = False
        self.thread = None
        self.previous_frame = None
        self.capture_interval = SETTINGS["CAPTURE_INTERVAL_MS"] / 1000.0
        self.change_threshold = SETTINGS["MIN_CHANGE_THRESHOLD"]

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
        logger.info("Screen capture started")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        logger.info("Screen capture stopped")

    def _capture_loop(self):
        try:
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                while self.running:
                    try:
                        screenshot = sct.grab(monitor)
                        frame = np.array(screenshot)
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                        timestamp = datetime.now()
                        if self.previous_frame is None or self._has_changed(
                            self.previous_frame, frame
                        ):
                            if self.on_frame_callback:
                                self.on_frame_callback(frame, timestamp)
                            self.previous_frame = frame.copy()
                        time.sleep(self.capture_interval)
                    except Exception as e:
                        logger.error(f"Capture error: {e}")
                        time.sleep(1)
        except Exception as e:
            logger.error(f"Capture engine error: {e}")

    def _has_changed(self, f1, f2) -> bool:
        try:
            s1 = cv2.resize(f1, (320, 180))
            s2 = cv2.resize(f2, (320, 180))
            g1 = cv2.cvtColor(s1, cv2.COLOR_BGR2GRAY)
            g2 = cv2.cvtColor(s2, cv2.COLOR_BGR2GRAY)
            diff = cv2.absdiff(g1, g2)
            _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
            return (np.sum(thresh > 0) / thresh.size) > self.change_threshold
        except Exception:
            return True

    def capture_single_frame(self):
        try:
            with mss.mss() as sct:
                screenshot = sct.grab(sct.monitors[1])
                frame = np.array(screenshot)
                return cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        except Exception as e:
            logger.error(f"Single capture error: {e}")
            return None
