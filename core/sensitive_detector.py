import time
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Optional, Callable
from datetime import datetime
from loguru import logger

from core.ocr_engine import OCREngine, OCRResult
from core.pattern_matcher import PatternMatcher, PatternMatch
from core.ai_classifier import AIClassifier
from config.settings import SETTINGS


@dataclass
class DetectionEvent:
    timestamp: datetime
    severity: str
    categories: List[str]
    confidence: float
    matched_patterns: List[PatternMatch]
    frame_path: Optional[str]
    raw_text_sample: str
    alert_message: str
    auto_action_taken: str


class SensitiveDetector:
    def __init__(self, on_detection_callback: Optional[Callable] = None):
        self.on_detection = on_detection_callback
        self.ocr = OCREngine()
        self.pattern_matcher = PatternMatcher()
        self.ai_classifier = AIClassifier()
        self.last_alert_time: Dict[str, float] = {}
        self.alert_cooldown = SETTINGS["ALERT_COOLDOWN_SECONDS"]
        self.stats = {"frames_analyzed": 0, "detections": 0}

    def analyze_frame(
        self, frame: np.ndarray, timestamp: datetime = None
    ) -> Optional[DetectionEvent]:
        if timestamp is None:
            timestamp = datetime.now()
        self.stats["frames_analyzed"] += 1
        try:
            ocr_result = self.ocr.extract_text(frame)
            if not ocr_result or not ocr_result.full_text.strip():
                return None
            
            # DEBUG - remove later
            logger.info("OCR read {} chars: {}".format(
                len(ocr_result.full_text),
                ocr_result.full_text[:100]
            ))
            pattern_matches = self.pattern_matcher.scan_text(ocr_result.full_text)
            ai_scores = self.ai_classifier.classify_text(ocr_result.full_text)
            event = self._build_event(timestamp, pattern_matches, ai_scores, ocr_result)
            if event and self._should_alert(event):
                self.stats["detections"] += 1
                self.last_alert_time[event.severity] = time.time()
                if self.on_detection:
                    self.on_detection(event)
                return event
        except Exception as e:
            logger.error(f"Analysis error: {e}")
        return None

    def _build_event(
        self, timestamp, pattern_matches, ai_scores, ocr_result
    ) -> Optional[DetectionEvent]:
        categories = []
        confidence = 0.0
        severity = "LOW"
        if pattern_matches:
            severity = (
                self.pattern_matcher.get_highest_severity(pattern_matches) or "LOW"
            )
            categories = list(set(m.category for m in pattern_matches))
            confidence = max(m.confidence for m in pattern_matches)
        high_ai = {
            k: v
            for k, v in ai_scores.items()
            if v >= SETTINGS["AI_CLASSIFICATION_THRESHOLD"]
        }
        for k in high_ai:
            if k not in categories:
                categories.append(k)
        if not categories:
            return None
        redacted = self.pattern_matcher.redact_text(
            ocr_result.full_text[:200], pattern_matches
        )
        msg = self._build_msg(categories, severity)
        return DetectionEvent(
            timestamp=timestamp,
            severity=severity,
            categories=categories,
            confidence=confidence,
            matched_patterns=pattern_matches,
            frame_path=None,
            raw_text_sample=redacted,
            alert_message=msg,
            auto_action_taken="",
        )

    def _should_alert(self, event: DetectionEvent) -> bool:
        return (
            time.time() - self.last_alert_time.get(event.severity, 0)
        ) >= self.alert_cooldown

    def _build_msg(self, categories: List[str], severity: str) -> str:
        names = {
            "aws_access_key": "AWS Access Key",
            "password_in_text": "Password",
            "credit_card_visa": "Credit Card",
            "private_key_header": "Private Key",
            "jwt_token": "JWT Token",
            "openai_key": "OpenAI API Key",
            "github_token": "GitHub Token",
            "database_url": "Database URL",
            "stripe_key": "Stripe Key",
        }
        emoji = {
            "CRITICAL": "ALERT",
            "HIGH": "WARNING",
            "MEDIUM": "NOTICE",
            "LOW": "INFO",
        }.get(severity, "WARNING")
        items = ", ".join(
            names.get(c, c.replace("_", " ").title()) for c in categories[:3]
        )
        return f"[{emoji}] {severity}: {items} detected on screen"

    def get_stats(self) -> Dict:
        return self.stats.copy()
