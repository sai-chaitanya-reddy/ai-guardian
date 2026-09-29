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
