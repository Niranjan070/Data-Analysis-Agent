# 🧩 Core Components

## Module Overview

```
core/
├── schema_compressor.py    — Dataset schema extraction & compression
├── history_manager.py      — Analysis history tracking & compression
├── scaledown_client.py     — ScaleDown API integration
├── code_executor.py        — Safe Python code execution sandbox
└── eda_agent.py            — Main EDA agent orchestrator
```

---

## 1. Schema Compressor (`schema_compressor.py`)

### Purpose
Extracts dataset metadata and compresses it into a **token-efficient representation** that preserves all analytically-relevant information.

### Class: `SchemaCompressor`

#### Key Methods

| Method | Description |
|---|---|
| `compress_schema(df, name)` | Generate compressed schema for a DataFrame |
| `get_full_vs_compressed_comparison(df)` | Compare token usage between full and compressed schemas |

#### How It Works

1. **Type Abbreviation**: Maps verbose type names to short codes
   ```
   "float64" → "f64"
   "int64" → "i64"
   "object" → "str"
   "datetime64[ns]" → "dt"
   ```

2. **Numeric Column Stats**: Extracts min, max, mean, median, std in compact format
   ```
   [0.01..234.5]|μ=32.1|std=45.6
   ```

3. **Categorical Detection**: Identifies numeric columns that are actually categorical
   ```
   Survived(i64)|uniq:2|[0..1]|⚠cat
   ```

4. **Skewness Hints**: Flags highly skewed columns
   ```
   Fare(f64)|skew:high_right
   ```

5. **Null Tracking**: Compact null percentage display
   ```
   Age(f64)|null:19.8%
   ```

#### Example Output
```
DS:titanic|891r×10c|0.12MB
COLS:
  PassengerId(i64)|uniq:891|[1..891]|μ=446
  Survived(i64)|uniq:2|[0..1]|μ=0.38|⚠cat
  Pclass(i64)|uniq:3|[1..3]|μ=2.31|⚠cat
  Name(str)|uniq:891|top:Passenger_0,Passenger_1,Passenger_2|avg_len:11
  Sex(str)|uniq:2|top:male,female
  Age(f64)|null:19.8%|uniq:88|[1.0..80.0]|μ=29.7
  Fare(f64)|uniq:823|[0.01..234.5]|μ=32.1|skew:high_right
  Embarked(str)|null:2%|uniq:3|top:S,C,Q
```

---

## 2. History Manager (`history_manager.py`)

### Purpose
Tracks all analysis steps and compresses the history using a **tiered strategy** to minimize tokens while preserving important findings.

### Classes

#### `AnalysisStep`
Represents a single analysis action:
- `action`: Tool name (e.g., "correlations")
- `description`: What was done
- `result_summary`: Compressed results
- `code`: Python code executed
- `chart_path`: Path to generated chart
- `tokens_used`: Token cost
- `timestamp`: When it was performed

#### `HistoryManager`
Manages the collection of steps with tiered compression.

#### Compression Tiers

```
┌──────────────────────────────────────────────┐
│  Tier 1: VERY OLD STEPS (ultra-compact)      │
│  "EARLIER: 15 steps (3x correlation,         │
│   5x distribution, 4x overview, 3x custom)"  │
├──────────────────────────────────────────────┤
│  Tier 2: RECENT STEPS (compact one-liners)   │
│  "→ [correlations] Correlation matrix → Top  │
│     correlation: Age↔Fare r=0.42 📊"         │
├──────────────────────────────────────────────┤
│  Tier 3: LATEST STEPS (full detail)          │
│  "• [outliers] IQR-based outlier detection"  │
│  "  Result: 5/8 columns have outliers..."    │
│  "  Chart: /static/charts/chart_abc.png"     │
└──────────────────────────────────────────────┘
```

#### Key Finding Preservation
Important discoveries (marked with ⚠, 🔴, ✅) are **always preserved** regardless of step age:
```
KEY FINDINGS:
  1. 🔴 Age ↔ Fare: +0.42 (strong positive correlation)
  2. ⚠ Fare has high right skew 
  3. 5/8 columns have outliers
```

---

## 3. ScaleDown Client (`scaledown_client.py`)

### Purpose
Integrates with the **ScaleDown API** for intelligent prompt compression, with a local fallback mechanism.

### Class: `ScaleDownClient`

#### API Integration
```python
# API endpoint
POST https://api.scaledown.xyz/compress/raw/

# Headers
x-api-key: <your_api_key>
Content-Type: application/json

# Payload
{
    "text": "<text to compress>",
    "target_ratio": 0.5
}
```

#### Fallback Compression
When the API is unavailable, local heuristic compression is applied:
1. **Remove extra whitespace** (triple newlines → double)
2. **Remove filler phrases** ("please note that", "as we can see", etc.)
3. **Abbreviate common terms** ("column" → "col", "standard deviation" → "std")
4. **Clean up artifacts** from removals

#### Stats Tracking
Cumulative metrics tracked:
- Total input tokens sent
- Total output tokens received
- Total tokens saved
- Number of API requests
- Per-request compression history

---

## 4. Code Executor (`code_executor.py`)

### Purpose
Safely executes Python code generated by the EDA agent in a **sandboxed environment**.

### Class: `CodeExecutor`

#### Security Model
The executor creates a controlled namespace with only approved libraries:
```python
exec_globals = {
    'pd': pandas,
    'np': numpy,
    'plt': matplotlib.pyplot,
    'sns': seaborn,
    'df': dataframe_copy,  # Always works on a COPY
}
```

#### Output Capture
1. **stdout**: All `print()` output captured via StringIO redirect
2. **Return values**: Last expression is evaluated if it's not an assignment
3. **Charts**: matplotlib figures detected and saved as PNG to `/static/charts/`
4. **Errors**: Full traceback captured without crashing the server

#### Chart Handling
- Charts use the `Agg` (non-interactive) backend
- Saved with dark background (`facecolor='#1a1a2e'`)
- Unique filenames using UUID
- Previous plots closed before each execution

---

## 5. EDA Agent (`eda_agent.py`)

### Purpose
The **central orchestrator** that ties all components together. It decides what analysis to run, generates code, executes it, and manages the compressed context.

### Class: `EDAAgent`

#### Analysis Tools
| Tool | What It Does |
|---|---|
| `overview` | Shape, types, memory, null counts, head preview |
| `describe` | Full `describe(include='all')` with zero-variance warnings |
| `correlations` | Correlation matrix, top pairs, heatmap |
| `distributions` | Histograms + KDE, skewness/kurtosis per column |
| `value_counts` | Categorical distributions + bar charts |
| `missing_analysis` | Missing value patterns + visual bar chart |
| `outliers` | IQR-based detection + box plots |
| `pairplot` | Pairwise scatter plots (top 5 numeric columns) |
| `time_analysis` | Datetime range detection and analysis |
| `custom` | Pattern-matched analysis from natural language query |

#### Auto-EDA Pipeline
The `run_auto_eda()` method runs a smart sequence:
1. Always: Overview → Statistics
2. If nulls exist: Missing value analysis
3. If numeric columns: Distributions → Correlations (if ≥2 cols)
4. If categorical columns: Value counts
5. If numeric columns: Outlier detection

#### Context Building
`get_context_for_llm()` combines:
```
DATASET SCHEMA:
<compressed schema>

KEY FINDINGS:
<preserved findings>

ANALYSIS HISTORY:
<tiered compressed history>

TOKENS: used=X, saved=Y
```
