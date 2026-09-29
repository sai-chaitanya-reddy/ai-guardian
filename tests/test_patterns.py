import sys
sys.path.insert(0, ".")
import pytest
from core.pattern_matcher import PatternMatcher


@pytest.fixture
def m():
    return PatternMatcher()


def test_aws_key(m):
    assert any(
        x.category == "aws_access_key"
        for x in m.scan_text("AKIAIOSFODNN7EXAMPLE")
    )


def test_openai_key(m):
    assert any(
        x.category == "openai_key"
        for x in m.scan_text("sk-" + "a" * 48)
    )


def test_password(m):
    assert any(
        x.category == "password_in_text"
        for x in m.scan_text("password=Secret123!")
    )


def test_credit_card(m):
    assert any(
        "credit_card" in x.category
        for x in m.scan_text("4532015112830366")
    )


def test_private_key(m):
    assert any(
        x.category == "private_key_header"
        for x in m.scan_text("-----BEGIN RSA PRIVATE KEY-----")
    )


def test_safe_text(m):
    assert len(m.scan_text("Hello world nice weather today")) == 0


def test_github_token(m):
    assert any(
        x.category == "github_token"
        for x in m.scan_text("ghp_aBcDeFgHiJkLmNoPqRsTuVwXyZ123456")
    )


def test_database_url(m):
    assert any(
        x.category == "database_url"
        for x in m.scan_text("postgresql://admin:pass@localhost/db")
    )


def test_redaction(m):
    text = "key is AKIAIOSFODNN7EXAMPLE here"
    matches = m.scan_text(text)
    redacted = m.redact_text(text, matches)
    assert "AKIAIOSFODNN7EXAMPLE" not in redacted
    assert "REDACTED" in redacted
