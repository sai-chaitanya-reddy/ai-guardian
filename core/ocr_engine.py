import numpy as np
import cv2
from dataclasses import dataclass
from typing import Optional, Tuple
from loguru import logger
from config.settings import SETTINGS


@dataclass
class OCRResult:
    text: str
    confidence: float
    bbox: Tuple[int, int, int, int]
    full_text: str


class OCREngine:
    def __init__(self):
        self.reader = None
        self.confidence_threshold = SETTINGS["OCR_CONFIDENCE_THRESHOLD"]
        self._init_reader()

    def _init_reader(self):
        try:
            import easyocr
            self.reader = easyocr.Reader(["en"], gpu=False, verbose=False)
            logger.info("EasyOCR initialized")
        except Exception as e:
            logger.warning(f"EasyOCR not available: {e}")
            self.reader = None

    def extract_text(self, frame: np.ndarray) -> Optional[OCRResult]:
        if self.reader is None:
            return OCRResult(text="", confidence=0.0, bbox=(0, 0, 0, 0), full_text="")
        try:
            processed = self._preprocess(frame)
            results = self.reader.readtext(processed, detail=1)
            texts = [t for _, t, c in results if c >= self.confidence_threshold]
            full_text = " ".join(texts)
            if full_text.strip():
                return OCRResult(
                    text=full_text,
                    confidence=0.8,
                    bbox=(0, 0, frame.shape[1], frame.shape[0]),
                    full_text=full_text,
                )
        except Exception as e:
            logger.error(f"OCR error: {e}")
        return None

    def _preprocess(self, frame: np.ndarray) -> np.ndarray:
        try:
            if frame.shape[1] < 1000:
                frame = cv2.resize(frame, None, fx=2, fy=2)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            return clahe.apply(gray)
        except Exception:
            return frame
