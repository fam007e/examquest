# ExamQuest: Interactive O & A Level Paper Downloader

[![Build Status](https://img.shields.io/badge/Build-Success-brightgreen)](https://github.com/fam007e/examquest)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![React 18](https://img.shields.io/badge/React-18-61DAFB)](https://reactjs.org/)

**ExamQuest** is a high-performance, asynchronous platform designed for the modern-day student. It streamlines the retrieval of past exam papers for Cambridge (CAIE) and Edexcel boards through a stunning, interactive web dashboard. With context-aware filtering, parallelized scraping, and automated merging, it transforms the tedious process of finding papers into a seamless experience.

---

## ✨ Features

### 💻 Modern Web Dashboard
- **Luxury UI**: Multi-layered glassmorphism and smooth animations.
- **Specialized Icons**: Handcrafted SVGs for major subjects (Physics, Chemistry, Math, etc.).
- **Context-Aware Search**: Instantly find subjects by name or code, or search for specific papers, years, and mark schemes within a subject.
- **Favorites**: Star your most-used subjects for instant access.
- **Mass Download & Merge**: Download multiple years at once or merge them into a single PDF with one click.

### 🐚 Powerful CLI (Legacy)
- For advanced users who prefer the command line.
- Same robust scraping logic with columnar subject displays.

---

## 📋 Prerequisites

Ensure these are installed before running:

| Requirement | Version | Download |
|-------------|---------|----------|
| **Python** | 3.10+ | [python.org](https://www.python.org/downloads/) |
| **Node.js** | 18+ | [nodejs.org](https://nodejs.org/) |

> [!TIP]
> On Windows, check **"Add Python to PATH"** during installation.

Verify your setup:
```bash
python3 --version   # or `python --version` on Windows
node --version
```

---

## ⚡ Quick Start

The fastest way to get started is using the integrated runner script:

1. **Clone the repo**:
   ```bash
   git clone https://github.com/fam007e/examquest.git
   cd examquest
   ```

2. **Run the Interactive Dashboard (Web)**:
   ```bash
   python run_app.py
   ```
   *This script automatically creates a **Virtual Environment (.venv)**, installs all dependencies, and launches the app. This avoids "Externally Managed Environment" errors found on Arch, Fedora, etc.*

3. **Run the Legacy CLI**:
   ```bash
   python o_and_a_lv_qp_sdl.py
   ```
   *For advanced users who prefer a terminal-based interface.*

---

## 🛠️ Project Structure

- `/backend`: FastAPI service handling the scraper logic and PDF processing.
- `/frontend`: Vite + React dashboard with Tailwind CSS and Framer Motion.
- `o_and_a_lv_qp_sdl.py`: The original standalone CLI script.
- `run_app.py`: The unified automation runner.

---

## 🤝 Community Standards

We follow standard GitHub community guidelines:
- [CONTRIBUTING.md](CONTRIBUTING.md): Guidelines on how to contribute features or report bugs.
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md): Our pledge to a welcoming community.
- [SECURITY.md](SECURITY.md): How to report security vulnerabilities.

---

## ⚖️ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🎓 Note

Please use this tool responsibly. The backend uses asynchronous requests with built-in "politeness" features (rate-limiting, jitter, and User-Agent rotation) to avoid overwhelming source websites. Respect Xtremepapers and Papacambridge; this tool is designed for educational purposes only.
