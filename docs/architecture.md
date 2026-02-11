# 🏗️ Architecture & Design

## System Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    CLIENT (Browser)                         │
│   ┌──────────┐  ┌──────────┐  ┌────────────┐  ┌────────┐  │
│   │  Upload   │  │ Analysis │  │  Results   │  │ Token  │  │
│   │  Manager  │  │  Panel   │  │  Viewer    │  │ Stats  │  │
│   └─────┬────┘  └─────┬────┘  └─────┬──────┘  └────┬───┘  │
│         └──────────────┼─────────────┼──────────────┘      │
│                        │ REST API (JSON)                    │
└────────────────────────┼───────────────────────────────────┘
                         │
┌────────────────────────▼───────────────────────────────────┐
│                  FastAPI BACKEND (Python)                   │
│                                                            │
│   ┌─────────────────────────────────────────────────────┐  │
│   │                    EDA AGENT                         │  │
│   │  ┌───────────────┐    ┌────────────────────────┐    │  │
│   │  │    Schema      │    │    History Manager     │    │  │
│   │  │   Compressor   │    │  ┌──────────────────┐  │    │  │
│   │  │  ┌───────────┐ │    │  │ Tier 1: Summary  │  │    │  │
│   │  │  │ Type Map  │ │    │  │ Tier 2: Compact  │  │    │  │
│   │  │  │ Stats     │ │    │  │ Tier 3: Detailed │  │    │  │
│   │  │  │ Compact   │ │    │  └──────────────────┘  │    │  │
│   │  │  └───────────┘ │    └────────────────────────┘    │  │
│   │  └───────────────┘                                   │  │
│   │                                                      │  │
│   │  ┌───────────────┐    ┌────────────────────────┐    │  │
│   │  │    Code        │    │   ScaleDown Client    │    │  │
│   │  │   Executor     │    │  ┌──────────────────┐  │    │  │
│   │  │  ┌───────────┐ │    │  │  API Compress   │  │    │  │
│   │  │  │ Sandbox   │ │    │  │  Local Fallback │  │    │  │
│   │  │  │ Capture   │ │    │  │  Stats Tracker  │  │    │  │
│   │  │  │ Charts    │ │    │  └──────────────────┘  │    │  │
│   │  │  └───────────┘ │    └────────────────────────┘    │  │
│   │  └───────────────┘                                   │  │
│   └─────────────────────────────────────────────────────┘  │
│                                                            │
│   ┌────────────────────────────────────────────────────┐   │
│   │  Static Files: HTML, CSS, JS, Generated Charts     │   │
│   └────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │   ScaleDown API     │
              │  api.scaledown.xyz  │
              │  /compress/raw/     │
              └─────────────────────┘
```

---

## Data Flow

### 1. Dataset Upload Flow
```
User uploads CSV/Excel
        │
        ▼
FastAPI receives file → saves to /uploads/
        │
        ▼
Pandas reads file into DataFrame
        │
        ▼
SchemaCompressor.compress_schema(df)
    ├── Extract column types (abbreviated)
    ├── Calculate null percentages
    ├── Compute numeric stats (min, max, mean, std)
    ├── Identify top categorical values
    ├── Detect skewness & categorical hints
    └── Generate compact string representation
        │
        ▼
Compare full_tokens vs compressed_tokens
        │
        ▼
Return schema + compression stats to UI
```

### 2. Analysis Execution Flow
```
User clicks analysis tool (e.g., "Correlations")
        │
        ▼
EDA Agent generates Python code for the tool
        │
        ▼
CodeExecutor.execute(code, df)
    ├── Create sandboxed namespace (pd, np, plt, sns)
    ├── Execute code in sandbox
    ├── Capture stdout output
    ├── Save generated charts to /static/charts/
    └── Return results + chart paths
        │
        ▼
Compress result summary via ScaleDown API
        │
        ▼
HistoryManager.add_step(compressed_step)
        │
        ▼
Extract key findings from output
        │
        ▼
Return results + updated token stats to UI
```

### 3. Context Building Flow
```
get_context_for_llm() called
        │
        ├── Get compressed schema string
        │   "DS:titanic|891r×10c|0.12MB..."
        │
        ├── Get compressed history
        │   ├── Key findings (always included)
        │   ├── Recent steps (compact)
        │   └── Old steps (summarized)
        │
        ├── Combine into single context
        │
        └── Optionally compress further via ScaleDown API
                │
                ▼
        Final compressed context (minimal tokens)
```

---

## Directory Structure

```
scale-down-challenge-2/
│
├── app.py                      # FastAPI server & API routes
├── requirements.txt            # Python dependencies
├── .env                        # API keys (git-ignored)
├── .env.example                # Template for env vars
├── .gitignore                  # Git ignore rules
├── README.md                   # Project README
│
├── core/                       # Core agent modules
│   ├── __init__.py             # Package init
│   ├── schema_compressor.py    # Schema extraction & compression
│   ├── history_manager.py      # Analysis history management
│   ├── scaledown_client.py     # ScaleDown API integration
│   ├── code_executor.py        # Safe code execution sandbox
│   └── eda_agent.py            # Main agent orchestrator
│
├── static/                     # Frontend assets
│   ├── index.html              # Main HTML page
│   ├── style.css               # CSS styling
│   ├── app.js                  # Frontend JavaScript
│   └── charts/                 # Generated chart images
│
├── sample_data/                # Demo datasets (auto-generated)
│   ├── titanic_sample.csv
│   ├── sales_sample.csv
│   └── students_sample.csv
│
├── uploads/                    # User-uploaded files
│
└── docs/                       # Project documentation
    ├── README.md               # Documentation index
    ├── project-overview.md     # Problem & solution
    ├── architecture.md         # This file
    ├── setup-guide.md          # Installation steps
    ├── api-reference.md        # API endpoints
    ├── core-components.md      # Module documentation
    ├── token-compression.md    # Compression methodology
    ├── usage-guide.md          # User guide
    └── demo.md                 # Sample outputs & results
```

---

## Design Decisions

### 1. Modular Architecture
Each core function is encapsulated in its own module, making the system:
- **Testable**: Each module can be unit-tested independently
- **Extensible**: New analysis tools can be added to the EDA Agent without modifying other components
- **Maintainable**: Clear separation of concerns

### 2. Sandboxed Code Execution
The `CodeExecutor` runs generated code in a controlled namespace to:
- Prevent access to system-level operations
- Capture all outputs (stdout, return values, charts)
- Handle errors gracefully without crashing the server

### 3. Tiered History Compression
Instead of keeping full history or discarding old steps, we use a 3-tier approach:
- This mimics how humans remember analysis — detailed recent memory, summarized older memory
- Key findings are always preserved regardless of age

### 4. Fallback Strategy
The ScaleDown client includes local heuristic compression as a fallback:
- Ensures the application works even without API connectivity
- Provides a baseline compression that still saves tokens

### 5. Dark Theme Visualizations
Charts are generated with dark backgrounds (#1a1a2e) to:
- Match the application's dark theme
- Provide a cohesive visual experience
- Improve readability in low-light environments
