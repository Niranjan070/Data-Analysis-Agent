# 📦 Token Compression — How It Works

## The Core Innovation

This project's key innovation is **three-layer compression** that reduces the tokens needed for LLM-powered data analysis by **80-99%**.

---

## Layer 1: Schema Compression

### Problem
When sending dataset information to an LLM, the naive approach is extremely token-heavy:

```python
# Naive approach — ~21,450 tokens for Titanic dataset
context = df.to_string() + "\n" + df.describe().to_string() + "\n" + str(df.dtypes)
```

### Solution
Our `SchemaCompressor` extracts only what matters and encodes it compactly:

```python
# Our approach — ~113 tokens for the same dataset
context = schema_compressor.compress_schema(df)["compact_string"]
```

### Compression Techniques

| Technique | Before | After | Saving |
|---|---|---|---|
| Type abbreviation | `float64` | `f64` | 57% |
| Stats condensation | `min=0.42, max=512.33, mean=32.20, std=49.69` | `[0.42..512.33]\|μ=32.20` | 60% |
| Null representation | `177 out of 891 values are missing (19.8%)` | `null:19.8%` | 80% |
| Categorical hint | `This column has only 2 unique values and appears categorical` | `⚠cat` | 95% |
| Skewness flag | `The distribution is highly right-skewed with skewness of 4.79` | `skew:high_right` | 88% |

### Benchmarks

| Dataset | Rows | Cols | Full Tokens | Compressed Tokens | Ratio | Savings |
|---|---|---|---|---|---|---|
| Titanic | 891 | 10 | 21,450 | 113 | **189.8x** | **99.5%** |
| Sales | 1,000 | 9 | 25,100 | 108 | **232.4x** | **99.6%** |
| Students | 500 | 12 | 13,800 | 135 | **102.2x** | **99.0%** |

### What's Preserved

Despite the massive compression, all analytically-useful information is retained:

✅ Column names and types  
✅ Null percentages  
✅ Unique value counts  
✅ Min/max/mean for numeric columns  
✅ Top values for categorical columns  
✅ Skewness indicators  
✅ Categorical encoding hints  
✅ Memory usage  
✅ Dataset dimensions  

### What's Removed

❌ Actual data rows (only stats matter for analysis planning)  
❌ Verbose type descriptions  
❌ Redundant statistics (e.g., 25th/75th percentile when min/max/mean suffice)  
❌ Row indices  
❌ Formatting whitespace  

---

## Layer 2: History Compression

### Problem
As analysis progresses, the history of steps grows linearly:

```
Step 1: Overview — full output (200 tokens)
Step 2: Statistics — full output (300 tokens)
Step 3: Correlations — full output (400 tokens)
...
Step 20: Custom query — full output (250 tokens)
Total: ~5,000+ tokens
```

### Solution
Tiered compression strategy:

```
Step 1-15: "EARLIER: 15 steps (3x correlation, 5x overview...)"  ← 20 tokens
Step 16-17: Compact one-liners                                    ← 40 tokens
Step 18-20: Full detail                                           ← 120 tokens
Key findings: Always preserved                                   ← 50 tokens
Total: ~230 tokens (95.4% savings!)
```

### How Tiers Work

| Tier | Steps | Detail Level | Example |
|---|---|---|---|
| **Ultra-compact** | Oldest | Action counts | `"15 steps (3x correlation, 5x dist)"` |
| **Compact** | Recent | One-line summaries | `"→ [correlations] Top: Age↔Fare r=0.42 📊"` |
| **Detailed** | Latest 5 | Full results | Full description + result + chart path |
| **Findings** | All ages | Always preserved | `"🔴 Age ↔ Fare: +0.42"` |

### Adaptive Behavior
- With ≤5 steps: All shown in detail
- With 6-25 steps: Compact + detailed tiers
- With 25+ steps: All three tiers active
- Findings: Always preserved (last 10)

---

## Layer 3: ScaleDown API Compression

### Purpose
The already-compressed schema + history is further optimized using the ScaleDown API's intelligent compression.

### How It Works

```
1. Combine compressed schema + compressed history → context string
2. Send to ScaleDown API: POST /compress/raw/
3. API returns semantically-compressed version
4. Track token savings
```

### API Request Example
```python
import requests

response = requests.post(
    "https://api.scaledown.xyz/compress/raw/",
    headers={
        "x-api-key": "your_api_key",
        "Content-Type": "application/json"
    },
    json={
        "text": compressed_context,
        "target_ratio": 0.5
    }
)
```

### Fallback: Local Heuristic Compression
When the API is unavailable, local compression applies:
1. Remove redundant whitespace
2. Strip filler phrases ("please note that", "basically", etc.)
3. Abbreviate common data terms ("column" → "col", "maximum" → "max")
4. Clean up artifacts

---

## Combined Compression Results

### Full Pipeline Example

```
Original context (raw data + verbose description):
→ ~27,000 tokens

After Layer 1 (Schema Compression):
→ ~150 tokens (99.4% reduction)

After Layer 2 (History Compression, 10 steps):
→ ~350 tokens total (schema + history)

After Layer 3 (ScaleDown API):
→ ~280 tokens (additional 20% reduction)

TOTAL SAVINGS: 99.0% (~189x compression)
```

### Token Cost Impact

| Scenario | Without Compression | With Compression | Cost Savings |
|---|---|---|---|
| 1 analysis call | ~27,000 tokens | ~280 tokens | 99.0% |
| 10 analysis calls | ~75,000 tokens | ~3,200 tokens | 95.7% |
| Full EDA session (50 calls) | ~200,000 tokens | ~8,500 tokens | 95.8% |

### Why This Matters

At typical LLM pricing ($0.01-0.03 per 1K tokens):

| Session Type | Without | With | Saved |
|---|---|---|---|
| Single dataset EDA | $2.00 - $6.00 | $0.09 - $0.26 | **$1.91 - $5.74** |
| 10 datasets/day | $20 - $60 | $0.85 - $2.55 | **$19.15 - $57.45** |
| Monthly (300 datasets) | $600 - $1,800 | $25 - $76 | **$575 - $1,724** |

---

## Measuring Compression

The application provides real-time compression metrics through:

1. **Token Dashboard**: Visual display of schema/history compression percentages
2. **Compression Card**: Side-by-side comparison bars showing original vs compressed
3. **API Stats**: Cumulative ScaleDown API usage tracking
4. **Context Modal**: View the exact compressed context that would be sent to an LLM
