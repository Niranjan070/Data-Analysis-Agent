# 🧠 Data Analysis Agent

> **Intel Unnati Challenge 2 — AI Agents**
> Build a data science agent that compresses dataset schemas and analysis history, automating exploratory data analysis with lower token costs.

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![ScaleDown](https://img.shields.io/badge/Powered%20by-ScaleDown-6c5ce7)](https://scaledown.ai)

---

## 📋 Overview

This project implements an **AI-powered Data Analysis Agent** that automates Exploratory Data Analysis (EDA) while dramatically reducing token costs through intelligent compression. The agent uses the **ScaleDown API** to compress dataset schemas and analysis history before sending them to LLMs.

### Key Innovation: Token-Efficient EDA

| Component | Without Compression | With Compression | Savings |
|---|---|---|---|
| Dataset Schema | ~2,000 tokens | ~200 tokens | **~90%** |
| Analysis History | ~5,000 tokens | ~800 tokens | **~84%** |
| Full Context | ~7,000 tokens | ~1,000 tokens | **~85%** |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│           Web UI (Browser)              │
│  Upload → Analyze → View Results        │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│          FastAPI Backend                │
│  ┌──────────┐ ┌────────┐ ┌──────────┐  │
│  │  Schema   │ │History │ │  Code    │  │
│  │Compressor│ │Manager │ │Executor  │  │
│  └────┬─────┘ └───┬────┘ └────┬─────┘  │
│       └─────┬─────┘           │        │
│        ┌────▼─────┐           │        │
│        │EDA Agent │←──────────┘        │
│        └────┬─────┘                    │
└─────────────┼──────────────────────────┘
              │
     ┌────────▼────────┐
     │  ScaleDown API  │
     │  (Compression)  │
     └─────────────────┘
```

---

## ✨ Features

- **🔬 Automated EDA Pipeline** — One-click comprehensive analysis
- **📦 Schema Compression** — 80-90% token reduction for dataset schemas
- **📜 History Compression** — Tiered summarization of analysis steps
- **🔗 ScaleDown Integration** — API-based prompt compression
- **📊 Rich Visualizations** — Charts with dark theme styling
- **🛡️ Safe Code Execution** — Sandboxed Python execution
- **📱 Modern Web UI** — Glassmorphism design with animations
- **📁 Sample Datasets** — Built-in demo datasets
- **📈 Token Dashboard** — Real-time token savings tracking

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- pip package manager

### Installation

```bash
# 1. Navigate to project directory
cd scale-down-challenge-2

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
# source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the application
python app.py
```

### Access
Open your browser and navigate to: **http://localhost:8000**

---

## 📂 Project Structure

```
scale-down-challenge-2/
├── app.py                    # FastAPI backend server
├── requirements.txt          # Python dependencies
├── .env                      # API keys (not committed)
├── .gitignore               # Git ignore rules
├── README.md                 # This file
├── core/                     # Core agent modules
│   ├── __init__.py
│   ├── schema_compressor.py  # Dataset schema compression
│   ├── history_manager.py    # Analysis history management
│   ├── scaledown_client.py   # ScaleDown API integration
│   ├── code_executor.py      # Safe Python code execution
│   └── eda_agent.py          # Main EDA agent orchestrator
├── static/                   # Frontend assets
│   ├── index.html            # Main HTML page
│   ├── style.css             # Styling
│   ├── app.js                # Frontend logic
│   └── charts/               # Generated charts
├── sample_data/              # Demo datasets
│   ├── titanic_sample.csv
│   ├── sales_sample.csv
│   └── students_sample.csv
└── uploads/                  # User uploaded files
```

---

## 🔧 Core Components

### 1. Schema Compressor (`core/schema_compressor.py`)
Extracts and compresses dataset metadata into compact representations:
- Column types abbreviated (e.g., `float64` → `f64`)
- Numeric stats condensed (min, max, mean, median, std)
- Categorical top values extracted
- Missing value percentages included
- Skewness and categorical hints added

**Example compressed output:**
```
DS:titanic|891r×10c|0.12MB
COLS:
  PassengerId(i64)|null:0%|uniq:891|[1..891]|μ=446
  Survived(i64)|null:0%|uniq:2|[0..1]|μ=0.38|⚠cat
  Age(f64)|null:19.8%|uniq:88|[1.0..80.0]|μ=29.7
```

### 2. History Manager (`core/history_manager.py`)
Uses tiered compression for analysis history:
- **Tier 1** (very old): Action count summaries
- **Tier 2** (recent): Compact one-liners
- **Tier 3** (latest): Full details with results

### 3. ScaleDown Client (`core/scaledown_client.py`)
- Integrates with ScaleDown API for prompt compression
- Includes local fallback compression
- Tracks cumulative token savings

### 4. Code Executor (`core/code_executor.py`)
- Executes Python code in sandboxed environment
- Captures stdout, results, and generated charts
- Supports pandas, numpy, matplotlib, seaborn

### 5. EDA Agent (`core/eda_agent.py`)
- Orchestrates the full analysis pipeline
- Generates analysis code for different tools
- Builds compressed LLM context
- Extracts and preserves key findings

---

## 📊 Analysis Tools

| Tool | Description |
|---|---|
| Overview | Dataset shape, types, memory, nulls |
| Statistics | Descriptive statistics (describe) |
| Correlations | Correlation matrix + heatmap |
| Distributions | Histograms with KDE |
| Categories | Value counts + bar charts |
| Missing Values | Null pattern analysis |
| Outliers | IQR-based outlier detection |
| Pair Plot | Pairwise scatter plots |
| Custom Query | Natural language analysis requests |

---

## 🔑 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Serve web UI |
| GET | `/api/health` | Health check |
| GET | `/api/test-connection` | Test ScaleDown API |
| GET | `/api/sample-datasets` | List sample datasets |
| POST | `/api/upload` | Upload dataset (file) |
| POST | `/api/load-sample` | Load sample dataset |
| POST | `/api/auto-eda` | Run full auto-EDA |
| POST | `/api/analyze` | Run specific tool |
| GET | `/api/token-stats` | Token usage stats |
| GET | `/api/history` | Analysis history |
| GET | `/api/compressed-context` | Compressed LLM context |

---

## 🛡️ Tech Stack

- **Backend**: Python 3.10+ / FastAPI
- **Data Analysis**: Pandas, NumPy, SciPy
- **Visualization**: Matplotlib, Seaborn
- **Compression**: ScaleDown API + Local heuristics
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Fonts**: Inter, JetBrains Mono

---

## 📄 License

This project was built for the **Intel Unnati Industrial Training Program — Challenge 2: AI Agents**.

---

*Built with ❤️ using ScaleDown API for intelligent prompt compression*
