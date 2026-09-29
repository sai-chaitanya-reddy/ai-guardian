import re
from dataclasses import dataclass
from typing import List, Optional
from loguru import logger


@dataclass
class PatternMatch:
    category: str
    matched_text: str
    confidence: float
    start_pos: int
    end_pos: int
    severity: str
    redact_display: str


class PatternMatcher:

    PATTERNS = {
        "aws_access_key": {
            "pattern": "AKIA[0-9A-Z]{16}",
            "severity": "CRITICAL",
            "confidence": 0.99,
            "display": "AWS_KEY_REDACTED",
        },
        "github_token": {
            "pattern": "gh[pousr]_[A-Za-z0-9_]{36,255}",
            "severity": "CRITICAL",
            "confidence": 0.98,
            "display": "GITHUB_TOKEN_REDACTED",
        },
        "password_in_text": {
            "pattern": "(?i)(password|passwd|pwd|pass)[ \\t]*[=:][ \\t]*(\\S{6,})",
            "severity": "CRITICAL",
            "confidence": 0.90,
            "display": "PASSWORD_REDACTED",
        },
        "private_key_header": {
            "pattern": "-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----",
            "severity": "CRITICAL",
            "confidence": 0.99,
            "display": "PRIVATE_KEY_REDACTED",
        },
        "jwt_token": {
            "pattern": "eyJ[A-Za-z0-9_-]{10,}\\.[A-Za-z0-9_-]{10,}\\.[A-Za-z0-9_-]{10,}",
            "severity": "HIGH",
            "confidence": 0.95,
            "display": "JWT_TOKEN_REDACTED",
        },
        "credit_card_visa": {
            "pattern": "4[0-9]{12}(?:[0-9]{3})?",
            "severity": "CRITICAL",
            "confidence": 0.90,
            "display": "CREDIT_CARD_REDACTED",
        },
        "credit_card_amex": {
            "pattern": "3[47][0-9]{13}",
            "severity": "CRITICAL",
            "confidence": 0.90,
            "display": "CREDIT_CARD_REDACTED",
        },
        "credit_card_mastercard": {
            "pattern": "5[1-5][0-9]{14}",
            "severity": "CRITICAL",
            "confidence": 0.90,
            "display": "CREDIT_CARD_REDACTED",
        },
        "ssn": {
            "pattern": "[0-9]{3}-[0-9]{2}-[0-9]{4}",
            "severity": "CRITICAL",
            "confidence": 0.88,
            "display": "SSN_REDACTED",
        },
        "database_url": {
            "pattern": "(?i)(mongodb|postgresql|mysql|redis|sqlite)://[^\\s]+",
            "severity": "CRITICAL",
            "confidence": 0.92,
            "display": "DB_CONNECTION_REDACTED",
        },
        "google_api_key": {
            "pattern": "AIza[0-9A-Za-z\\-_]{35}",
            "severity": "HIGH",
            "confidence": 0.98,
            "display": "GOOGLE_API_KEY_REDACTED",
        },
        "slack_token": {
            "pattern": "xox[baprs]-[0-9a-zA-Z\\-]{10,48}",
            "severity": "HIGH",
            "confidence": 0.97,
            "display": "SLACK_TOKEN_REDACTED",
        },
        "stripe_key": {
            "pattern": "sk_(live|test)_[0-9a-zA-Z]{24,}",
            "severity": "CRITICAL",
            "confidence": 0.98,
            "display": "STRIPE_KEY_REDACTED",
        },
        "openai_key": {
            "pattern": "sk-[A-Za-z0-9]{48}",
            "severity": "CRITICAL",
            "confidence": 0.99,
            "display": "OPENAI_KEY_REDACTED",
        },
        "generic_api_key": {
            "pattern": "(?i)(api_key|apikey|api-key)[ \\t]*[=:][ \\t]*[A-Za-z0-9\\-_]{20,}",
            "severity": "HIGH",
            "confidence": 0.85,
            "display": "API_KEY_REDACTED",
        },
        "phone_number": {
            "pattern": "[0-9]{3}[-.\\s][0-9]{3}[-.\\s][0-9]{4}",
            "severity": "MEDIUM",
            "confidence": 0.75,
            "display": "PHONE_REDACTED",
        },
    }

    def __init__(self):
        self.compiled_patterns = {}
        for name, config in self.PATTERNS.items():
            try:
                self.compiled_patterns[name] = {
                    "regex": re.compile(config["pattern"], re.MULTILINE),
                    "severity": config["severity"],
                    "confidence": config["confidence"],
                    "display": config["display"],
                }
            except re.error as e:
                logger.error("Pattern compile failed for {}: {}".format(name, e))

        logger.info("PatternMatcher ready: {} patterns loaded".format(
            len(self.compiled_patterns)
        ))

    def scan_text(self, text: str) -> List[PatternMatch]:
        matches = []
        for pattern_name, pattern_config in self.compiled_patterns.items():
            for match in pattern_config["regex"].finditer(text):
                matches.append(
                    PatternMatch(
                        category=pattern_name,
                        matched_text=match.group(0),
                        confidence=pattern_config["confidence"],
                        start_pos=match.start(),
                        end_pos=match.end(),
                        severity=pattern_config["severity"],
                        redact_display=pattern_config["display"],
                    )
                )
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        matches.sort(key=lambda x: severity_order.get(x.severity, 4))
        return matches

    def get_highest_severity(self, matches: List[PatternMatch]) -> Optional[str]:
        if not matches:
            return None
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        return min(
            matches,
            key=lambda x: severity_order.get(x.severity, 4)
        ).severity

    def redact_text(self, text: str, matches: List[PatternMatch]) -> str:
        redacted = text
        for match in sorted(matches, key=lambda x: x.start_pos, reverse=True):
            redacted = (
                redacted[: match.start_pos]
                + "[" + match.redact_display + "]"
                + redacted[match.end_pos :]
            )
        return redacted