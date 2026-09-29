import numpy as np
from typing import Dict
from loguru import logger
from config.settings import SETTINGS


class AIClassifier:
    def __init__(self):
        self.threshold = SETTINGS["AI_CLASSIFICATION_THRESHOLD"]
        self._check_npu()

    def _check_npu(self):
        try:
            import onnxruntime as ort
            providers = ort.get_available_providers()
            if "QNNExecutionProvider" in providers:
                logger.success("Qualcomm NPU provider available!")
            else:
                logger.info(f"ONNX providers: {providers}")
        except ImportError:
            logger.info("ONNX Runtime not installed - using keyword classification")

    def classify_text(self, text: str) -> Dict[str, float]:
        scores = {}
        t = text.lower()
        categories = {
            "api_key_visible": [
                "api_key", "api-key", "apikey", "access_token", "secret_key", "bearer"
            ],
            "password_field": [
                "password", "passwd", "pwd", "passphrase", "credentials"
            ],
            "credit_card": [
                "credit card", "card number", "cvv", "expiry", "billing", "visa", "mastercard"
            ],
            "personal_document": [
                "social security", "ssn", "passport", "driver license", "date of birth"
            ],
            "financial_data": [
                "account number", "routing number", "iban", "swift", "bank account"
            ],
            "code_with_secrets": [
                "def ", "import ", "const ", "require(", "function", "class "
            ],
        }
        for category, keywords in categories.items():
            score = sum(1 for kw in keywords if kw in t)
            if score > 0:
                scores[category] = min(score / max(len(keywords) * 0.3, 1), 1.0)
        return scores
