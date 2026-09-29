import sys
sys.path.insert(0, ".")

from core.pattern_matcher import PatternMatcher
from core.ai_classifier   import AIClassifier


def run():
    print()
    print("=" * 60)
    print("  AI Guardian -- Detection Demo")
    print("=" * 60)

    m = PatternMatcher()
    c = AIClassifier()

    scenarios = [
        ("AWS Credentials",   "AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE"),
        ("OpenAI Key",        "OPENAI_API_KEY=sk-" + "a" * 48),
        ("Credit Card",       "Card: 4532015112830366  CVV:523"),
        ("Private Key",       "-----BEGIN RSA PRIVATE KEY-----"),
        ("GitHub Token",      "GITHUB_TOKEN=ghp_aBcDeFgHiJkLmNoPqRsTuVwXyZ123456"),
        ("Database URL",      "postgresql://admin:Secret@prod.db.com/users"),
        ("Stripe Key",        "pk_test_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"),
        ("Safe Content",      "Hello world. Python is a great language!"),
    ]

    for name, text in scenarios:
        print(f"\nScenario: {name}")
        print("  " + "-" * 48)
        matches = m.scan_text(text)
        scores  = c.classify_text(text)

        if matches:
            for mt in matches[:3]:
                level = (
                    "CRITICAL"
                    if mt.severity == "CRITICAL"
                    else "HIGH"
                    if mt.severity == "HIGH"
                    else "MEDIUM"
                )
                print(f"  [{level}] {mt.category}")
                print(f"    Redact as -> [{mt.redact_display}]")

        high = {k: v for k, v in scores.items() if v > 0.25}
        for cat, score in high.items():
            print(f"  AI Score: {cat}  ({score:.0%})")

        if not matches and not high:
            print("  SAFE -- no sensitive content detected")
        else:
            sev = m.get_highest_severity(matches) or "MEDIUM"
            print(f"  --> Would trigger: {sev} alert")

    print()
    print("=" * 60)
    print("  Demo done!  Run:  python main.py")
    print("=" * 60)
    print()


if __name__ == "__main__":
    run()
