# 🩺 DependenceDoc — Automated Environment Restoration & Diagnostic Engine

[![VoltHacks 2026 Submission](https://img.shields.io/badge/VoltHacks%202026-Project-blueviolet.svg)](https://volthacks2026.devpost.com/)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Paste a chaotic terminal crash dump. Get exact, deterministic recovery commands in seconds.**

DependenceDoc is an intelligent, multi-domain diagnostic engine designed to solve developer environment chaos — Python dependency hell, missing native build toolchains (GCC, OpenSSL), unconfigured environment variables, and blocked infrastructure ports. Built for **VoltHacks 2026**.

---

## 🎥 Video Demo & Presentation

- **Demo Video:** [Watch the 3-Minute DependenceDoc Walkthrough on YouTube](https://www.youtube.com/watch?v=ejuxOH8hIYc)
- **Live Interface:** Run locally via `streamlit run main.py` or deploy seamlessly to Streamlit Community Cloud.

---

## 🌟 Key Features & Killer Innovations

1. **🩺 Multi-Domain Signal Router (Sentinel):**
   - Automatically classifies terminal crashes across four isolated failure domains:
     - 📦 **Python Package Dependency Conflicts:** PEP 440 mathematical constraint matching and PyPI historical releases.
     - 🖥️ **OS System Toolchains:** Native C/C++ compiler and SSL development libraries (`gcc`, `libssl-dev`).
     - 🌐 **Environment Configuration:** Inactive virtualenvs, missing packages (`yaml` → `pyyaml`, `cv2` → `opencv-python`), and missing environment secret tokens (`OPENAI_API_KEY`).
     - ⚙️ **Infrastructure Sockets:** Blocked network ports (`lsof` socket cleanup) and database connection refusals.

2. **🧠 Live PyPI Constraint Sieve (Healer & Detective Engine):**
   - Fetches live PyPI release matrices and evaluates version specifier sets using PEP 440 logic to find the exact newest stable release that resolves complex dependency deadlocks.

3. **🛡️ Embedded Execution Warden (Sandbox Watcher):**
   - Guarantees runtime safety and rate-limit guardrails with real-time CPU thread execution timeouts and API call tracking.

4. **🤖 Dual AI Insight Air-Lock (Auditor):**
   - Combines deterministic heuristic solutions with natural language AI context using **Gemini 2.5 Flash** or **Groq LLaMA-3.3-70B** for root-cause explanations and predictive risk simulation.

5. **📄 Executive PDF & Shell Script Export:**
   - Instantly export executable `.sh` recovery scripts or generate a comprehensive 3-page executive PDF report (built with ReportLab).

---

## 🏗️ System Architecture

```
                                  ┌────────────────────────┐
                                  │   Raw Terminal Log     │
                                  └───────────┬────────────┘
                                              │
                                  ┌───────────▼────────────┐
                                  │     Sentinel Guard     │
                                  │   (core/sentinel.py)   │
                                  └───────────┬────────────┘
                                              │
         ┌──────────────────┬─────────────────┼──────────────────┐
         │                  │                 │                  │
┌────────▼────────┐ ┌───────▼────────┐ ┌──────▼─────────┐ ┌──────▼─────────┐
│ System Resolver │ │ Env Resolver   │ │Runtime Resolver│ │  Scout Parser   │
│ (OS C-Toolchain)│ │(Vars / Modules)│ │(Ports / DBs)   │ │(Regex Parser)   │
└────────┬────────┘ └───────┬────────┘ └──────┬─────────┘ └──────┬──────────┘
         │                  │                 │                  │
         │                  │                 │         ┌────────▼────────┐
         │                  │                 │         │ Detective Engine│
         │                  │                 │         │(PEP 440 Logic)  │
         │                  │                 │         └────────┬────────┘
         │                  │                 │                  │
         │                  │                 │         ┌────────▼────────┐
         │                  │                 │         │  Healer Engine  │
         │                  │                 │         │  & PyPI Client  │
         │                  │                 │         └────────┬────────┘
         │                  │                 │                  │
         └──────────────────┴────────┬────────┴──────────────────┘
                                     │
                         ┌───────────▼────────────┐
                         │    Bankai Orchestrator │ ◄── [ Monitored by ]
                         │       (app.py)         │     Sandbox Watcher
                         └───────────┬────────────┘
                                     │
                         ┌───────────▼────────────┐
                         │   Streamlit Frontend   │
                         │       (main.py)        │
                         └────────────────────────┘
```

---

## ⚡ Quickstart Guide

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/your-username/everyone_ships_now.git
cd everyone_ships_now

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Configure API Keys (Optional)
AI insights use Google Gemini or Groq if available, but the system falls back seamlessly to deterministic rule-based solutions if no key is supplied.

Set environment variables or enter them directly in the Streamlit UI sidebar:
```bash
export GEMINI_API_KEY="your-gemini-api-key"
export GROQ_API_KEY="your-groq-api-key"
```

### 3. Launch the Application
```bash
streamlit run main.py
```

---

## 🧪 Testing & Verification

DependenceDoc includes a comprehensive test suite covering all internal engines, parsers, and report generators:

```bash
python3 -m unittest discover -s tests
```

To run individual module self-tests:
```bash
python3 app.py
```

---

## 🏆 VoltHacks 2026 Evaluation Alignment

- **Innovation & Creativity:** Replaces generic search queries with deterministic, automated root-cause isolation and single-click recovery script generation.
- **Technical Complexity:** Merges multi-domain regex parsing, PEP 440 mathematical constraint resolution, real-time PyPI API lookups, thread sandboxing, and dual AI provider fallback chains.
- **Real-World Impact:** Saves developers hours of tedious debugging and environment troubleshooting.
- **Design & Functionality:** Clean Streamlit interface, interactive architecture explorer, one-click demo samples, and production-ready PDF report generation.

---

## 📜 License & Ownership

DependenceDoc was created during VoltHacks 2026. All rights reserved by the original project contributors.
