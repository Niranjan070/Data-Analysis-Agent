# 🔌 API Reference

## Base URL

```
http://localhost:8000
```

---

## Endpoints

### Health & Status

#### `GET /api/health`
Health check endpoint.

**Response:**
```json
{
    "status": "ok",
    "version": "1.0.0"
}
```

---

#### `GET /api/test-connection`
Test the ScaleDown API connection.

**Response:**
```json
{
    "connected": true,
    "method": "api",
    "api_error": null
}
```

---

### Dataset Management

#### `GET /api/sample-datasets`
List available sample datasets.

**Response:**
```json
{
    "datasets": [
        {
            "name": "Titanic Sample",
            "filename": "titanic_sample.csv",
            "rows": 891,
            "columns": 10
        },
        {
            "name": "Sales Sample",
            "filename": "sales_sample.csv",
            "rows": 1000,
            "columns": 9
        },
        {
            "name": "Students Sample",
            "filename": "students_sample.csv",
            "rows": 500,
            "columns": 12
        }
    ]
}
```

---

#### `POST /api/upload`
Upload a dataset file (CSV, Excel, or TSV).

**Request:** `multipart/form-data`
| Field | Type | Description |
|---|---|---|
| `file` | File | The dataset file |

**Response:**
```json
{
    "success": true,
    "dataset_name": "my_dataset",
    "shape": { "rows": 891, "cols": 10 },
    "columns": ["col1", "col2", "..."],
    "dtypes": { "col1": "int64", "col2": "object" },
    "schema_compact": "DS:my_dataset|891r×10c|0.12MB\nCOLS:\n  ...",
    "compression": {
        "full_tokens": 21450,
        "compressed_tokens": 113,
        "savings_pct": 99.5,
        "compression_ratio": 189.8
    },
    "preview": [
        { "col1": 1, "col2": "value" }
    ]
}
```

---

#### `POST /api/load-sample`
Load a sample dataset.

**Request:** `application/x-www-form-urlencoded`
| Field | Type | Description |
|---|---|---|
| `filename` | string | Sample dataset filename (e.g., `titanic_sample.csv`) |

**Response:** Same format as `/api/upload`

---

### Analysis

#### `POST /api/auto-eda`
Run the full automated EDA pipeline on the loaded dataset.

**Request:** No body required (uses currently loaded dataset).

**Response:**
```json
{
    "results": [
        {
            "tool": "overview",
            "success": true,
            "stdout": "DATASET OVERVIEW\n...",
            "result_value": "",
            "chart_path": null,
            "error": null,
            "code": "print('DATASET OVERVIEW')...",
            "tokens_used": 77,
            "compression_savings": 15.2
        },
        {
            "tool": "correlations",
            "success": true,
            "stdout": "Top Correlations...",
            "chart_path": "/static/charts/chart_abc123.png",
            "tokens_used": 45,
            "compression_savings": 22.1
        }
    ],
    "token_stats": { ... },
    "history": [ ... ],
    "compressed_context": "DS:dataset|891r×..."
}
```

---

#### `POST /api/analyze`
Run a specific analysis tool.

**Request:** `application/x-www-form-urlencoded`
| Field | Type | Description |
|---|---|---|
| `tool` | string | Tool name (see table below) |
| `query` | string | Optional query for `custom` tool |

**Available Tools:**
| Tool | Description |
|---|---|
| `overview` | Dataset shape, types, memory, nulls |
| `describe` | Statistical summary |
| `correlations` | Correlation matrix & heatmap |
| `distributions` | Histograms with KDE |
| `value_counts` | Categorical value distributions |
| `missing_analysis` | Missing value patterns |
| `outliers` | IQR-based outlier detection |
| `pairplot` | Pairwise scatter plots |
| `time_analysis` | Temporal analysis |
| `custom` | Natural language query (use `query` field) |

**Response:**
```json
{
    "result": {
        "tool": "correlations",
        "success": true,
        "stdout": "CORRELATION ANALYSIS\n...",
        "chart_path": "/static/charts/chart_xyz.png",
        "code": "corr = df.corr()...",
        "tokens_used": 45
    },
    "token_stats": { ... },
    "history": [ ... ]
}
```

---

### Token Statistics

#### `GET /api/token-stats`
Get current token usage statistics.

**Response:**
```json
{
    "schema_compression": {
        "full_tokens": 21450,
        "compressed_tokens": 113,
        "savings_pct": 99.5,
        "compression_ratio": 189.8
    },
    "history_compression": {
        "uncompressed_tokens": 500,
        "compressed_tokens": 120,
        "savings_pct": 76.0
    },
    "scaledown_api": {
        "total_requests": 5,
        "total_input_tokens": 800,
        "total_output_tokens": 650,
        "total_tokens_saved": 150,
        "overall_savings_pct": 18.8
    },
    "total_analysis_steps": 7
}
```

---

#### `GET /api/history`
Get analysis history (both full and compressed).

**Response:**
```json
{
    "full_history": [
        {
            "action": "overview",
            "description": "Get dataset overview",
            "result_summary": "Shape: 891 × 10...",
            "code": "...",
            "chart_path": "",
            "tokens_used": 77,
            "timestamp": "2026-02-11T23:20:00"
        }
    ],
    "compressed_history": "KEY FINDINGS:\n  1. ...\nLATEST STEPS:\n  ...",
    "savings": {
        "uncompressed_tokens": 500,
        "compressed_tokens": 120,
        "savings_pct": 76.0
    }
}
```

---

#### `GET /api/compressed-context`
Get the compressed context that would be sent to an LLM.

**Response:**
```json
{
    "context": "DS:titanic|891r×10c|0.12MB\nCOLS:\n  PassengerId(i64)...",
    "token_estimate": 85
}
```

---

## Error Responses

All errors follow this format:
```json
{
    "detail": "Error message describing what went wrong"
}
```

| Status Code | Meaning |
|---|---|
| 400 | Bad request (e.g., no dataset loaded) |
| 404 | Resource not found |
| 500 | Internal server error |
