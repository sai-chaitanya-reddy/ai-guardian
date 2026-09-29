Markdown

<div align="center">

# 🛡️ AI Guardian
### On-Device Privacy & Screen-Safety Agent

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![ONNX](https://img.shields.io/badge/ONNX-Runtime-005CED?style=for-the-badge&logo=onnx&logoColor=white)
![PyQt5](https://img.shields.io/badge/PyQt5-UI-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

<br/>

> 🔒 **AI Guardian** continuously monitors your screen for sensitive information —
> API keys, passwords, credit cards, and confidential data —
> and alerts you **instantly**, with all processing done **100% on-device**.

<br/>

### 👨‍💻 Developed by **Bussireddy Sai Chaitanya Reddy** &nbsp;|&nbsp; Solo Project

</div>

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [How It Works](#-how-it-works)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Usage](#-usage)
- [Demo Output](#-demo-output)
- [Deployment Status](#-deployment-status)
- [Privacy and Security](#-privacy-and-security)
- [Author](#-author)

---

## 🔍 Overview

**AI Guardian** is a real-time desktop application that silently monitors your screen
and detects sensitive information before it causes a data breach.

### What It Detects

| Category | Examples |
|----------|---------|
| 🔑 API Keys and Tokens | AWS, OpenAI, GitHub, Stripe keys |
| 🔐 Passwords and Credentials | Login details, secret keys |
| 💳 Credit Card and CVV | Visa, Mastercard, Amex numbers |
| 🪪 Personal Identification | SSN, personal info, ID numbers |
| 🗄️ Database Credentials | PostgreSQL, MySQL connection strings |
| 📄 Private Keys | RSA, SSH, PEM certificates |

### Why It Matters

- Remote workers accidentally expose credentials during screen sharing
- Confidential documents visible in public spaces
- API keys committed or displayed during live coding sessions
- Data breaches cost an average of **$4.45 million** per incident (IBM 2023)

**AI Guardian protects you silently, instantly, and privately.**

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🖥️ **Real-Time Monitoring** | Continuously captures and analyzes screen content without interrupting workflow |
| 🔍 **OCR Text Extraction** | Extracts all visible text from screen frames using OCR engine |
| 🧩 **Pattern Matching** | Regex-based detection for 20+ sensitive data patterns |
| 🧠 **AI Classification** | ONNX MobileNetV2 model classifies privacy risk levels in real time |
| 🚨 **Instant Alerts** | Notifies user immediately when sensitive content is detected |
| 📵 **Screenshot Blocking** | Blocks screenshots when sensitive data is visible on screen |
| 📋 **Event Logging** | All detection events logged securely in local SQLite database |
| ⚡ **NPU Acceleration** | Designed for Snapdragon NPU/QNN hardware acceleration |
| 🔄 **CPU Fallback** | Auto fallback to optimized CPU inference on unsupported systems |
| 🔒 **Local Processing** | Zero cloud dependency — 100% on-device, zero data leaves machine |

---

## ⚙️ How It Works
┌─────────────────────────────────────────────────────────────────┐
│ │
│ STEP 1 STEP 2 STEP 3 │
│ Screen → OCR → Pattern │
│ Capture Extraction Matching │
│ │
│ STEP 4 STEP 5 STEP 6 │
│ AI → Risk → Instant │
│ Classification Assessment Alert │
│ │
│ STEP 7 STEP 8 │
│ Event → Screenshot │
│ Logged Blocked │
│ │
└─────────────────────────────────────────────────────────────────┘

text


| Step | Module | What Happens |
|------|--------|-------------|
| 1 | `screen_capture.py` | Screen captured periodically in real time |
| 2 | `ocr_engine.py` | All visible text extracted from screen frame |
| 3 | `pattern_matcher.py` | Text scanned with regex for 20+ sensitive patterns |
| 4 | `ai_classifier.py` | ONNX model scores overall privacy risk level |
| 5 | `sensitive_detector.py` | Severity determined — CRITICAL, HIGH, or MEDIUM |
| 6 | `alert_popup.py` | User instantly notified with detailed alert |
| 7 | `event_logger.py` | Detection event saved to local SQLite database |
| 8 | `screenshot_guard.py` | Screenshot blocked if sensitive data on screen |

---

## 🛠️ Tech Stack

| Technology | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.8+ | Core application language |
| **ONNX Runtime** | Latest | AI model inference engine |
| **MobileNetV2** | ONNX | Lightweight neural network for classification |
| **OCR Engine** | — | Text extraction from screen captures |
| **PyQt5** | 5.x | Desktop UI and system tray |
| **SQLite** | Built-in | Local event logging database |
| **Snapdragon NPU/QNN** | Target | Hardware acceleration on HP Snapdragon PCs |
| **CPU Inference** | Fallback | Auto fallback on non-Snapdragon devices |

---

## 📁 Project Structure
ai_guardian/
│
├── 📄 main.py ← Application entry point
├── 📄 demo_test.py ← Detection demo script
├── 📄 requirements.txt ← Python dependencies
├── 📄 .gitignore ← Git ignore rules
├── 🗄️ guardian_events.db ← Local SQLite event database
│
├── 📂 core/ ← Core detection engine
│ ├── ai_classifier.py ← ONNX AI model classifier
│ ├── npu_accelerator.py ← Snapdragon NPU/QNN support
│ ├── ocr_engine.py ← OCR text extraction
│ ├── pattern_matcher.py ← Regex pattern matching
│ ├── screen_capture.py ← Screen capture module
│ └── sensitive_detector.py ← Main detection coordinator
│
├── 📂 ui/ ← User Interface
│ ├── main_window.py ← Main application window
│ ├── alert_popup.py ← Alert notification popup
│ ├── dashboard.py ← Dashboard view
│ ├── overlay_widget.py ← Screen overlay widget
│ ├── settings_panel.py ← Settings configuration panel
│ └── system_tray.py ← System tray integration
│
├── 📂 security/ ← Security modules
│ ├── event_logger.py ← Detection event logger
│ ├── redactor.py ← Sensitive data redactor
│ └── screenshot_guard.py ← Screenshot blocking guard
│
├── 📂 models/ ← AI Models
│ ├── model_manager.py ← Model loading and management
│ └── cached/
│ └── mobilenetv2.onnx.data ← ONNX model weights
│
├── 📂 config/ ← Configuration
│ └── settings.py ← App settings and config
│
├── 📂 tests/ ← Unit Tests
│ └── test_patterns.py ← Pattern matcher tests
│
└── 📂 assets/ ← UI Assets
└── styles/
└── dark_theme.qss ← Dark theme stylesheet

text


---

## 🚀 Installation

### Prerequisites

```bash
# Ensure Python 3.8 or higher is installed
python --version
Clone the Repository
Bash

git clone https://github.com/sai-chaitanya-reddy/ai-guardian.git
cd ai-guardian
Install Dependencies
Bash

pip install -r requirements.txt
Run the Application
Bash

python main.py
Run the Detection Demo
Bash

python demo_test.py
🎮 Usage
Launch AI Guardian
Bash

python main.py
Run Detection Demo Only
Bash

python demo_test.py
Run Tests
Bash

python -m pytest tests/
🖥️ Demo Output
text

============================================================
  AI Guardian -- Detection Demo
============================================================

Scenario: AWS Credentials
  ------------------------------------------------
  [CRITICAL] AWS Access Key
    Redact as -> [AKIA***EXAMPLE]
  --> Would trigger: CRITICAL alert

Scenario: OpenAI Key
  ------------------------------------------------
  [CRITICAL] OpenAI API Key
    Redact as -> [sk-***aaaa]
  --> Would trigger: CRITICAL alert

Scenario: Credit Card
  ------------------------------------------------
  [CRITICAL] Credit Card Number
    Redact as -> [4532***0366]
  --> Would trigger: CRITICAL alert

Scenario: Private Key
  ------------------------------------------------
  [CRITICAL] RSA Private Key
    Redact as -> [-----BEGIN***-----]
  --> Would trigger: CRITICAL alert

Scenario: GitHub Token
  ------------------------------------------------
  [HIGH] GitHub Token
    Redact as -> [ghp_***XXXX]
  --> Would trigger: HIGH alert

Scenario: Database URL
  ------------------------------------------------
  [HIGH] Database Credentials
    Redact as -> [postgresql://***@prod.db.com]
  --> Would trigger: HIGH alert

Scenario: Stripe Key
  ------------------------------------------------
  [HIGH] Stripe API Key
    Redact as -> [pk_test_***XXXX]
  --> Would trigger: HIGH alert

Scenario: Safe Content
  ------------------------------------------------
  SAFE -- no sensitive content detected

============================================================
  Demo done!  Run:  python main.py
============================================================
📊 Deployment Status
Environment	Inference Mode	Status
Current Development Machine — Intel CPU	ONNX CPU Inference	✅ Tested and Working
Snapdragon-Powered HP PC — Target	Snapdragon NPU / QNN	🎯 Target Platform
Any Non-Snapdragon Device	CPU Fallback — Automatic	⚡ Auto Fallback
Note: The application is designed and optimized for deployment on
Snapdragon-powered HP PCs with Snapdragon NPU/QNN hardware acceleration.
On unsupported systems, including the current development environment,
it seamlessly falls back to optimized CPU inference,
maintaining full functionality across all devices.

🔐 Privacy and Security
Principle	Status	Detail
Local Processing Only	✅	All detection happens on-device
No Cloud APIs	✅	Zero communication with external servers
No Remote Data Storage	✅	Screen content never stored remotely
Open Source	✅	Full code transparency — inspect everything
Secure Event Logging	✅	Stored only in local SQLite database
Screenshot Protection	✅	Actively blocks screenshots when sensitive data visible
Zero Telemetry	✅	No usage data collected or transmitted
👤 Author
<div align="center"><br/>
Bussireddy Sai Chaitanya Reddy
Solo Developer — AI Guardian Project

<br/>
GitHub

<br/></div>
<div align="center">
🛡️ AI Guardian
Protecting Your Privacy with On-Device AI
All sensitive data detection occurs 100% on-device.

Zero cloud dependency. Zero data exposure. Zero compromise.

<br/>
Python
ONNX
PyQt5

</div> ```
