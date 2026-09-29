<div align="center">

# 🛡️ AI Guardian
### On-Device Privacy & Screen-Safety Agent

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![ONNX](https://img.shields.io/badge/ONNX-Runtime-005CED?style=for-the-badge&logo=onnx&logoColor=white)
![PyQt5](https://img.shields.io/badge/PyQt5-UI-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

> **AI Guardian** is an on-device privacy and screen-safety agent that
> continuously monitors screen content to detect and alert users about
> sensitive information — all processed **locally**, with zero cloud exposure.

---

**Developed by Bussireddy Sai Chaitanya Reddy** — Solo Project

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
- [Demo](#-demo)
- [Deployment Status](#-deployment-status)
- [Author](#-author)

---

## 🔍 Overview

AI Guardian is a real-time desktop application that monitors your screen
for sensitive information such as:

- 🔑 API Keys & Tokens (AWS, OpenAI, GitHub, Stripe)
- 🔐 Passwords & Credentials
- 💳 Credit Card Numbers & CVV
- 🪪 Personal Identification Data
- 🗄️ Database URLs & Connection Strings
- 📄 Private Keys & Certificates

When sensitive content is detected, AI Guardian **immediately alerts the user**
and can **block screenshots** to prevent accidental data exposure.

All processing happens **entirely on your local device** —
no data is ever sent to external servers or cloud APIs.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🖥️ **Real-Time Monitoring** | Continuously captures and analyzes screen content |
| 🔍 **OCR Text Extraction** | Extracts visible text using OCR engine |
| 🧩 **Pattern Matching** | Regex-based detection for credentials and sensitive patterns |
| 🧠 **AI Classification** | ONNX-based MobileNetV2 model classifies privacy risk levels |
| 🚨 **Instant Alerts** | Notifies user immediately when sensitive content is found |
| 📵 **Screenshot Blocking** | Prevents accidental exposure by blocking screenshots |
| 📋 **Event Logging** | Logs all detection events securely for later review |
| ⚡ **NPU Acceleration** | Designed for Snapdragon NPU/QNN hardware acceleration |
| 🔄 **CPU Fallback** | Seamlessly falls back to CPU on unsupported systems |
| 🔒 **Local Processing** | Zero cloud dependency — 100% on-device |

---

## ⚙️ How It Works
