import cv2
import numpy as np
from typing import Tuple
from loguru import logger
from config.settings import SETTINGS


class ScreenRedactor:
    def __init__(self):
        self.blur_radius = SETTINGS["BLUR_RADIUS"]

    def blur_region(
        self, frame: np.ndarray, bbox: Tuple[int, int, int, int]
    ) -> np.ndarray:
        x, y, w, h = bbox
        result = frame.copy()
        try:
            region = result[y : y + h, x : x + w]
            if region.size == 0:
                return result
            small = cv2.resize(
                region, (max(1, w // 10), max(1, h // 10))
            )
            pixelated = cv2.resize(
                small, (w, h), interpolation=cv2.INTER_NEAREST
            )
            result[y : y + h, x : x + w] = pixelated
        except Exception as e:
            logger.error(f"Blur error: {e}")
        return result

    def redact_full_frame(self, frame: np.ndarray) -> np.ndarray:
        blurred = cv2.GaussianBlur(frame, (99, 99), 30)
        cv2.putText(
            blurred,
            "REDACTED - AI Guardian",
            (50, frame.shape[0] // 2),
            cv2.FONT_HERSHEY_SIMPLEX,
            2,
            (0, 0, 255),
            3,
        )
        return blurred

    def create_warning_overlay(
        self, frame: np.ndarray, message: str
    ) -> np.ndarray:
        result = frame.copy()
        overlay = result.copy()
        cv2.rectangle(overlay, (0, 0), (frame.shape[1], 60), (200, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, result, 0.3, 0, result)
        cv2.putText(
            result,
            f"AI GUARDIAN: {message}",
            (10, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (255, 255, 255),
            2,
        )
        return result
