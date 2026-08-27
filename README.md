# 🩺 DependenceDoc // Automated Environment Recovery & Dependency Hell Resolver

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B.svg)](https://streamlit.io/)
[![VoltHacks 2026](https://img.shields.io/badge/VoltHacks-2026%20Submission-indigo.svg)](https://devpost.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Paste an error log. Get exact, mathematical terminal commands to restore your environment in seconds.**

DependenceDoc is an intelligent, multi-domain environment recovery framework built for developers, DevOps engineers, and researchers. It diagnoses chaotic terminal stack traces, detects PEP 440 dependency constraint conflicts, identifies missing native OS toolchains, isolates blocked infrastructure sockets, and compiles deterministic, non-breaking recovery scripts alongside AI-generated root-cause insights and 3-page executive PDF reports.

---

## 🌟 Key Features

- **🚦 Multi-Domain Sentinel Signal Matrix**: Automatically classifies crash logs into four distinct operational sectors:
  - 🖥️ **System C-Library**: Missing GCC toolchains, OpenSSL headers, wheel compilation failures.
  - 🌐 **Environment Path**: Module import mismatches (e.g., `cv2` → `opencv-python`), missing `.env` tokens, inactive virtual environments.
  - ⚙️ **Runtime Infrastructure**: Port socket collisions (`lsof`/`kill`), database connection refusals.
  - 📦 **Package Dependency**: Complex PEP 440 version bounds, conflicting requirements, and unresolvable deadlocks.
- **🕵️ PEP 440 Detective Engine**: Performs exact mathematical constraint solving over extracted requirement specifiers (`<`, `<=`, `>`, `>=`, `==`, `!=`). Detects mutually exclusive dependency deadlocks.
- **💊 Live PyPI Release Sieve & Healer**: Queries PyPI indexes in real-time, sifting through historical package releases to locate the newest stable release satisfying all constraint boundaries without breaking parent packages.
- **🛡️ Sandbox Execution Warden**: Enforces thread execution timeouts and API call rate limits to prevent runaway loops or API exhaustion during log analysis.
- **🤖 Dual AI Insight Air-Lock**: Queries **Gemini 2.5 Flash** or **Groq LLaMA 3.3 70B** to generate deep root-cause explanations and predictive side-effect simulations ("pre-thinking"), with a zero-downtime deterministic fallback if API keys are absent.
- **💻 Dual CLI & Web Dashboard**: Run via a polished interactive Streamlit dashboard (`main.py`) or directly in your terminal via the high-speed CLI (`cli.py`).
- **📄 Executive Reports & Script Generator**: Exports single-click self-executing shell scripts (`.sh`) and multi-page vector PDF reports built with ReportLab.
- **💾 Diagnostic Snapshot Serialization**: Export and import full diagnostic state snapshots as JSON for team collaboration and bug report attachments.
- **📊 Integrated Novus / Pendo Telemetry**: Tracks diagnostic execution milestones and export metrics seamlessly.

---

## 🎯 VoltHacks 2026 Hackathon Alignment

DependenceDoc was developed for **VoltHacks 2026** under the **Open Innovation & Engineering Tooling** track.

### 🏆 Judging Criteria Matrix

| Criteria | Implementation in DependenceDoc |
| :--- | :--- |
| **Innovation & Creativity** | Combines PEP 440 mathematical constraint solving with live PyPI historical release querying and LLM predictive pre-thinking, moving beyond generic error search engines. |
| **Technical Complexity** | Features a multi-layered modular architecture: Sentinel Signal Detector, Scout Extraction Regex Sieve, Detective PEP 440 Engine, Healer Release Sieve, Sandbox Watcher Guard, and PDF Report Engine. |
| **Real World Impact** | Saves developers and CI/CD pipelines hours of frustrating trial-and-error during environment setups, dependency resolution, and build crashes. |
| **Design & Functionality** | Clean, dark-mode Streamlit dashboard with instant 1-click test logs, system health gauges, interactive Graphviz architecture flow, and CLI terminal tool. |
| **Presentation Quality** | Clear technical documentation, embedded architecture explorer, executive PDF reporting, and self-contained command export. |

---

## 🏗️ Architecture & Pipeline Execution Flow

```
                      ┌───────────────────────────┐
                      │    Raw Terminal Crash     │
                      └─────────────┬─────────────┘
                                    │
                                    ▼
                      ┌───────────────────────────┐
                      │   Sentinel Guard Matrix   │
                      └─────────────┬─────────────┘
                                    │
       ┌──────────────────┬─────────┴─────────┬──────────────────┐
       ▼                  ▼                   ▼                  ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│    System    │   │ Environment  │   │   Runtime    │   │  Scout Regex │
│   Resolver   │   │   Resolver   │   │   Resolver   │   │    Parser    │
└──────┬───────┘   └──────┬───────┘   └──────┬───────┘   └──────┬───────┘
       │                  │                   │                 │
       │                  │                   │                 ▼
       │                  │                   │          ┌──────────────┐
       │                  │                   │          │  Detective   │
       │                  │                   │          │  PEP 440 Math│
       │                  │                   │          └──────┬───────┘
       │                  │                   │                 │
       │                  │                   │                 ▼
       │                  │                   │          ┌──────────────┐
       │                  │                   │          │ PyPI Release │
       │                  │                   │          │ Index Sieve  │
       │                  │                   │          └──────┬───────┘
       │                  │                   │                 │
       │                  │                   │                 ▼
       │                  │                   │          ┌──────────────┐
       │                  │                   │          │Healer Recover│
       │                  │                   │          │ Plan Compiler│
       │                  │                   │          └──────┬───────┘
       │                  │                   │                 │
       └──────────────────┼───────────────────┴─────────────────┘
                          │
                          ▼
            ┌───────────────────────────┐
            │   AI Auditor & Pre-Think  │
            └─────────────┬─────────────┘
                          │
                          ▼
            ┌───────────────────────────┐
            │ Shell Script / PDF / UI   │
            └───────────────────────────┘
```

---

## 🛠️ Module Registry

- **`app.py`**: Core orchestrator (`BankaiOrchestrator`). Routes logs across parallel resolvers, calculates explainable confidence scores, and manages snapshot import/export.
- **`main.py`**: Streamlit web application interface with metric cards, progress bars, architecture visualizer, and instant 1-click sample crash scenarios.
- **`cli.py`**: Command-line interface for running terminal diagnostics directly without a browser.
- **`core/sentinel.py`**: Signal detection gate that maps log inputs to problem domains.
- **`core/scout.py`**: Constraint parser using regular expressions to extract requirement specifiers and installed package versions.
- **`core/detective.py`**: PEP 440 specifier math and deadlock detection engine.
- **`core/healer.py`**: Recovery plan compiler that matches constraint intersections against PyPI releases.
- **`core/watcher.py`**: Execution warden monitoring thread lifecycles and API call frequencies.
- **`core/system_resolver.py`**: Native C-toolchain and OS package dependency resolver.
- **`core/environment_resolver.py`**: Path mapping, ModuleNotFoundError package lookup table, and `.env` secret detector.
- **`core/runtime_resolver.py`**: Socket collision and database process resolver.
- **`services/pdf_generator.py`**: PDF report builder using ReportLab.
- **`services/pypi_client.py`**: LRU-cached PyPI JSON API client.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- `pip`

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/krishivjoshi219-collab/everyone_ships_now.git
cd everyone_ships_now

# Install dependencies
pip install -r requirements.txt
```

---

### 2. Running the Streamlit Web Application

```bash
streamlit run main.py
```

Open your browser to `http://localhost:8501`. You can:
1. Click any **"Try It Instantly"** sample button (Python dependency conflict, missing GCC compiler, ModuleNotFoundError, or missing API token).
2. Paste any custom terminal traceback or `pip` error log.
3. Inspect AI root-cause analysis, pre-thinking risk evaluations, and exact terminal commands.
4. Download executable bash recovery scripts (`.sh`) or executive PDF reports.

---

### 3. Running via Command Line (CLI)

Diagnose a log file directly from the terminal:

```bash
# Analyze a log file
python3 cli.py sample_logs/dependency_conflict.txt

# Export recovery script directly
python3 cli.py sample_logs/missing_gcc.txt --export-script fix_gcc.sh

# Output raw JSON payload
python3 cli.py sample_logs/module_not_found.txt --json

# Pipe logs directly via STDIN
cat my_crash.log | python3 cli.py
```

---

## 🧪 Running Unit Tests

DependenceDoc comes with comprehensive automated test suites covering all core modules, resolvers, parsers, and CLI interfaces:

```bash
python3 -m unittest discover -s tests
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Built for **VoltHacks 2026**. Special thanks to hackathon sponsors **CodeCrafters**, **Featherless.ai**, **Gen.xyz**, **Dialogate**, **Tin Computer**, **Eventopia**, **DevSwarm**, and **AdaptionLabs**.
