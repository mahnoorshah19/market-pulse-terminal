# MarketPulse Terminal 

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Framework-FastAPI-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Transformers](https://img.shields.io/badge/NLP-FinBERT%20%7C%20Zero--Shot-yellow.svg)](https://huggingface.co/)
[![TailwindCSS](https://img.shields.io/badge/UI-TailwindCSS-38B2AC.svg?logo=tailwind-css)](https://tailwindcss.com/)

> **Real-Time Macroeconomic & Treasury Impact Radar**  
> An automated, production-grade financial intelligence engine that ingests financial news wires, categorizes macroeconomic sectors via Zero-Shot Natural Language Inference, and assesses market sentiment/directional risk using domain-calibrated FinBERT models.

---

## Business & Analytical Motivation

Treasury desks, corporate finance teams, and institutional market analysts must rapidly assess incoming macroeconomic news, foreign exchange shifts, monetary policy announcements, and sector-specific policy updates. 

Standard NLP solutions and off-the-shelf sentiment libraries fail in finance because financial terminology is counter-intuitive:
* Phrases like *"State Bank hikes policy rate by 100 bps"* are labeled neutral or positive by generic tools, yet they represent market tightening and liquidity contraction risks.
* Rule-based scrapers break frequently and rely on fragile keyword matching that struggles with out-of-vocabulary terms.

**MarketPulse Terminal** provides a persistent, automated intelligence layer that:
1. Replaces fragile HTML web scraping with structured, clean financial RSS ingestion wires.
2. Uses **Zero-Shot NLI Classification** (`valhalla/distilbart-mnli-12-3`) to map dynamic headlines directly to banking, treasury, energy, tech, and FX markets without requiring thousands of manually labeled examples.
3. Implements **FinBERT** (`ProsusAI/finbert`) to assign high-confidence directional impact labels (`BULLISH`, `BEARISH`, or `NEUTRAL`).
4. Provides a collaborative testing sandbox with crowdsourced feedback validation for quality assurance.

---

## System Architecture

```text
       ┌───────────────────────────────┐
       │     Financial Wire Feeds      │
       │    (ProPakistani, BRecorder)  │
       └───────────────┬───────────────┘
                       │
                       ▼
       ┌───────────────────────────────┐
       │   FastAPI Ingestion Engine    │
       │  - RSS parsing & cleaning     │
       │  - Story deduplication        │
       └───────────────┬───────────────┘
                       │
                       ▼
       ┌───────────────────────────────┐
       │     Inference Pipelines       │
       │  - FinBERT (Direction/Risk)   │
       │  - Zero-Shot (Sector Mapping) │
       └───────────────┬───────────────┘
                       │
                       ▼
       ┌───────────────────────────────┐
       │    Persistent SQLite Layer    │
       │  - Historical impact database │
       │  - Validation feedback votes  │
       └───────────────┬───────────────┘
                       │
        ┌──────────────┴──────────────┐
        ▼                             ▼
┌───────────────┐           ┌──────────────────┐
│ REST Endpoints│           │ Tailwind Web UI  │
│  /api/v1/...  │           │ - Live terminal  │
│               │           │ - Tester sandbox │
└───────────────┘           └──────────────────┘

## Tech Stack
Backend & API: FastAPI, Uvicorn

Database & ORM: SQLite, SQLAlchemy

NLP & Deep Learning: Hugging Face transformers, PyTorch, FinBERT (ProsusAI/finbert), DistilBART-MNLI (valhalla/distilbart-mnli-12-3)

Feed Ingestion: BeautifulSoup4, urllib, XML/RSS

Frontend: Jinja2 Templates, Tailwind CSS (via CDN), FontAwesome

## Repository Structure

market-pulse-terminal/
│
├── assets/
│   ├── Dashboard.png
│   └── Dashboard2.png
│
├── backend/
│   ├── __init__.py
│   ├── database.py        # SQLAlchemy engine and session lifecycle
│   ├── main.py            # FastAPI endpoints, templating & route handling
│   ├── ml_engine.py       # FinBERT & Zero-Shot transformer pipelines
│   ├── models.py          # Relational DB schema (NewsItem, feedback logs)
│   └── scraper.py         # Multi-feed RSS wire ingestor & deduplicator
│
├── frontend/
│   ├── static/
│   │   └── app.js         # Optional client-side utilities
│   └── templates/
│       └── index.html     # Responsive Tailwind dark-mode terminal layout
│
├── .gitignore
├── Procfile               # Cloud deployment command (Render/Railway)
├── README.md
└── requirements.txt


## Quickstart & Local Setup

1. Prerequisites: Ensure you have Python 3.10 or newer installed.

2. Clone the Repository:
git clone [https://github.com/mahnoorshah19/market-pulse-terminal.git](https://github.com/mahnoorshah19/market-pulse-terminal.git)
cd market-pulse-terminal

3. Create and Activate Virtual Environment:
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

4. Install Dependencies:
pip install -r requirements.txt

5. Launch the Server
uvicorn backend.main:app --reload

## License
This project is open-source under the MIT License.