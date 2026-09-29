import sys
sys.path.insert(0, ".")

import mss
import numpy as np
import cv2
from datetime import datetime

print("=" * 50)
print("Testing OCR - Reading Your Screen")
print("=" * 50)

# Capture screen
print("\n[1] Capturing screen...")
with mss.mss() as sct:
    monitor = sct.monitors[1]
    screenshot = sct.grab(monitor)
    frame = np.array(screenshot)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
print(f"    Screen captured: {frame.shape[1]}x{frame.shape[0]}")

# Try OCR
print("\n[2] Loading OCR engine...")
try:
    from core.ocr_engine import OCREngine
    ocr = OCREngine()
    if ocr.reader is None:
        print("    ERROR: OCR reader is None!")
        print("    EasyOCR did not load properly")
    else:
        print("    OCR loaded OK")
except Exception as e:
    print(f"    ERROR loading OCR: {e}")
    sys.exit(1)

# Read text from screen
print("\n[3] Reading text from your screen...")
print("    (This takes 5-15 seconds first time)")
result = ocr.extract_text(frame)

if result and result.full_text.strip():
    print(f"\n    TEXT FOUND! Length: {len(result.full_text)} chars")
    print("    First 300 characters:")
    print("    " + "-" * 40)
    print("    " + result.full_text[:300])
    print("    " + "-" * 40)
else:
    print("\n    NO TEXT FOUND!")
    print("    OCR could not read any text from screen")

# Test detection on found text
print("\n[4] Testing detection on screen text...")
if result and result.full_text.strip():
    from core.pattern_matcher import PatternMatcher
    pm = PatternMatcher()
    matches = pm.scan_text(result.full_text)
    if matches:
        print(f"    DETECTED {len(matches)} sensitive items:")
        for m in matches[:5]:
            print(f"      [{m.severity}] {m.category}")
    else:
        print("    No sensitive patterns in screen text")
        print("    (Make sure a secret is visible on screen!)")

print("\n" + "=" * 50)
print("Test complete")
print("=" * 50)