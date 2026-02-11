# 📖 Usage Guide

## Getting Started

### 1. Launch the Application
```bash
cd scale-down-challenge-2
venv\Scripts\activate    # Windows
python app.py
```
Open **http://localhost:8000** in your browser.

---

## Step-by-Step Usage

### Step 1: Load a Dataset

You have two options:

#### Option A: Upload Your Own
1. Click the **drag & drop zone** or drag a file onto it
2. Supported formats: `.csv`, `.xlsx`, `.xls`, `.tsv`
3. Wait for the schema analysis to complete

#### Option B: Use a Sample Dataset
1. Click on any **sample dataset** from the right panel:
   - **Titanic Sample**: 891 rows × 10 columns (passenger survival data)
   - **Sales Sample**: 1,000 rows × 9 columns (product sales data)
   - **Students Sample**: 500 rows × 12 columns (student performance data)

### Step 2: Review Schema Compression

After loading, you'll see:
- **Compression ratio** (e.g., "189.8x")
- **Token comparison bars** (original vs compressed)
- **Compressed schema** in compact format
- **Data preview** showing first 5 rows

### Step 3: Run Analysis

#### Full Auto-EDA (Recommended)
Click the **🚀 Run Full Auto-EDA** button for a comprehensive analysis pipeline:
- Dataset overview
- Statistical summary
- Missing value analysis
- Distributions (histograms)
- Correlations (heatmap)
- Categorical analysis
- Outlier detection

#### Individual Tools
Click any tool card for targeted analysis:
| Tool | Best For |
|---|---|
| 📊 Overview | First look at the dataset |
| 📈 Statistics | Understanding data ranges and distributions |
| 🔗 Correlations | Finding relationships between variables |
| 📉 Distributions | Understanding data shape and skewness |
| 🏷️ Categories | Analyzing categorical columns |
| 🕳️ Missing Values | Identifying data quality issues |
| ⚡ Outliers | Finding anomalous data points |
| 🔄 Pair Plot | Visual pairwise relationships |

#### Custom Query
Type a natural language question in the input field:
- "Show me correlations"
- "What are the distributions?"
- "Find missing values"
- "Detect outliers"
- "Show category counts"

### Step 4: Review Results

Each analysis result shows:
- **Status badge** (✓ Success or ✗ Error)
- **Token usage** for that step
- **Text output** (statistics, summaries)
- **Charts** (if generated)
- **Code** (click "Show Code" to view the Python code)

### Step 5: Monitor Token Savings

The **Token Dashboard** shows real-time metrics:
- Schema compression percentage
- History compression percentage
- Total tokens saved
- Number of analysis steps

### Step 6: View Compressed Context

Click **"View LLM Context"** to see the exact compressed context that would be sent to an LLM. This demonstrates the token efficiency of the system.

---

## Tips & Best Practices

### For Best Results
1. **Start with Auto-EDA** to get a comprehensive overview
2. **Then drill down** with individual tools based on findings
3. **Use custom queries** for specific questions about your data

### For Demonstrations
1. Load the **Titanic dataset** (most familiar for demonstrations)
2. Run **Auto-EDA** to show the full pipeline
3. Click **"View LLM Context"** to show the compression in action
4. Point out the **compression ratio** (189.8x for Titanic)
5. Show the **Token Dashboard** metrics

### For Maximum Token Savings
1. The system automatically compresses history as steps accumulate
2. Key findings are always preserved for context
3. The ScaleDown API provides additional compression on top of local compression
