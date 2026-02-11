# 🎯 Project Overview

## Problem Statement

> **Build a data science agent that compresses dataset schemas and analysis history, automating exploratory data analysis with lower token costs.**

In modern AI-driven data analysis, LLMs (Large Language Models) are used to understand datasets, generate insights, and write analysis code. However, a major challenge is the **high token cost** of sending full dataset descriptions and analysis histories to LLMs.

### The Problem

When performing Exploratory Data Analysis (EDA) using LLMs:

1. **Dataset schemas are verbose** — A dataset with 20 columns generates thousands of tokens just for the schema description
2. **Analysis history grows linearly** — Each step adds to the context, quickly filling up the LLM's context window
3. **Token costs scale with data complexity** — More columns, more rows, more unique values = exponentially more tokens
4. **Redundant information** — Full DataFrames, complete `describe()` outputs, and raw column listings waste tokens on redundant information

### Example: Token Waste

For a simple 891-row, 10-column Titanic dataset:

| Representation | Tokens | Cost Impact |
|---|---|---|
| `df.to_string()` | ~20,000 | 💸💸💸 |
| `df.describe()` + `df.dtypes` | ~1,500 | 💸💸 |
| **Our compressed schema** | **~113** | 💚 |

That's a **189x compression ratio** — meaning you can analyze datasets **189 times more efficiently**!

---

## Our Solution

The **Data Analysis Agent** solves this by implementing a three-layer compression strategy:

### Layer 1: Schema Compression
Instead of sending raw DataFrames or verbose `describe()` outputs, we extract only the analytically-relevant metadata and encode it in a compact format:

```
DS:titanic|891r×10c|0.12MB
COLS:
  PassengerId(i64)|uniq:891|[1..891]|μ=446
  Survived(i64)|uniq:2|[0..1]|μ=0.38|⚠cat
  Age(f64)|null:19.8%|uniq:88|[1.0..80.0]|μ=29.7
  Fare(f64)|uniq:823|[0.01..234.5]|μ=32.1|skew:high_right
```

### Layer 2: History Compression
Analysis history is managed in tiers:
- **Latest 5 steps**: Full detail with results
- **Recent 20 steps**: Compact one-liners
- **Older steps**: Summarized as action counts (e.g., "3x correlation, 2x distribution")

### Layer 3: ScaleDown API Compression
The already-compressed context is further optimized using the **ScaleDown API**, which performs intelligent prompt compression while preserving semantic meaning.

---

## Key Features

| Feature | Description |
|---|---|
| 🔬 **Automated EDA** | One-click comprehensive analysis pipeline |
| 📦 **Schema Compression** | 80-99% token reduction for dataset schemas |
| 📜 **History Compression** | Tiered summarization preserving key findings |
| 🔗 **ScaleDown Integration** | API-based prompt compression |
| 📊 **Rich Visualizations** | Dark-themed charts with matplotlib/seaborn |
| 🛡️ **Safe Code Execution** | Sandboxed Python execution environment |
| 📱 **Modern Web UI** | Premium glassmorphism design |
| 📈 **Token Dashboard** | Real-time compression metrics |
| 📁 **Multiple Formats** | CSV, Excel, TSV support |

---

## Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Backend | Python 3.10+ / FastAPI | REST API server |
| Data Analysis | Pandas, NumPy, SciPy | Statistical analysis |
| Visualization | Matplotlib, Seaborn | Chart generation |
| Compression | ScaleDown API | Prompt optimization |
| Frontend | HTML5, CSS3, JavaScript | Interactive UI |
| Design | Inter, JetBrains Mono | Typography |

---

## Target Outcomes

1. **Reduce token costs** by 80-99% for dataset schema representation
2. **Automate EDA** with a comprehensive analysis pipeline
3. **Preserve analytical value** while compressing — no loss of actionable insights
4. **Demonstrate ScaleDown API** integration for real-world prompt optimization
5. **Provide a production-ready** web application with modern UI
