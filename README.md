# ExamQuest: Interactive O & A Level Paper Downloader

[![Build Status](https://img.shields.io/badge/Build-Success-brightgreen)](https://github.com/fam007e/examquest)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![React 19](https://img.shields.io/badge/React-19-61DAFB)](https://react.dev/)

**ExamQuest** is an asynchronous platform that simplifies retrieving past exam papers for Cambridge (CAIE) and Edexcel boards. It features context-aware filtering, parallelized scraping, automated merging, and an interactive web dashboard.

---

## Tech Stack

ExamQuest is built using modern web and backend technologies:

* **Frontend**: React 19, Vite 7 (Rolldown compiler), Tailwind CSS v4, Framer Motion, and Lucide React.
* **Backend**: FastAPI (Python 3.10+), Uvicorn, BeautifulSoup4, and Brotli compression.
* **Scraper & CLI**: Asynchronous HTTP client, User-Agent rotation, rate-limiting, and `PyPDF2` / `pdfmerger.sh` for PDF utilities.

---

## Features

### Web Dashboard
- **Glassmorphism**: Sleek dashboard styling with smooth transitions and animations.
- **Lucide Icons**: Specialized visual markers for major subjects (Physics, Chemistry, Mathematics, etc.).
- **Context-Aware Search**: Fast searching by subject name or code, plus direct search for papers, years, and mark schemes.
- **Favorites**: Star frequently used subjects for quick access.
- **Mass Download & Merge**: Download multiple papers simultaneously and merge them into a single PDF.

### Command Line Interface (Legacy CLI)
- A standalone command-line downloader for advanced users.
- Clean terminal formatting and asynchronous scraping logic.

---

## Prerequisites

Ensure the following are installed before running:

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

## Quick Start

The fastest way to run the application is with the integrated runner script:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/fam007e/examquest.git
   cd examquest
   ```

2. **Run the Interactive Dashboard**:
   ```bash
   python run_app.py
   ```
   *This script automatically creates a Virtual Environment (`.venv`), installs all frontend and backend dependencies, and launches the app.*

3. **Run the Legacy CLI**:
   ```bash
   python o_and_a_lv_qp_sdl.py
   ```

---

## Project Structure

- `/backend`: FastAPI service handling the scraper logic and PDF processing.
- `/frontend`: React dashboard compiled with Vite 7 and Tailwind CSS v4.
- `o_and_a_lv_qp_sdl.py`: The original standalone CLI script.
- `run_app.py`: The unified automation runner.

---

## Community Standards

We follow standard GitHub community guidelines:
- [CONTRIBUTING.md](CONTRIBUTING.md): Guidelines on how to contribute features or report bugs.
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md): Our pledge to a welcoming community.
- [SECURITY.md](SECURITY.md): How to report security vulnerabilities.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Note

Please use this tool responsibly. The backend uses asynchronous requests with rate-limiting, jitter, and User-Agent rotation to avoid overwhelming source websites. Respect Xtremepapers and PastPapers.co; this tool is for educational use only.
