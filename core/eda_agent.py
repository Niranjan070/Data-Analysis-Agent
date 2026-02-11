"""
EDA Agent
=========
The main AI agent that orchestrates Exploratory Data Analysis.
Uses compressed schemas and history to minimize token usage while
providing comprehensive data analysis capabilities.

The agent works in a loop:
1. Receives compressed context (schema + history)
2. Decides what analysis to perform next
3. Generates Python code
4. Executes code and captures results
5. Updates history with findings
6. Repeats or responds to user queries
"""

import json
import re
from typing import Dict, Any, Optional, List
from .schema_compressor import SchemaCompressor
from .history_manager import HistoryManager, AnalysisStep
from .scaledown_client import ScaleDownClient
from .code_executor import CodeExecutor
import pandas as pd


class EDAAgent:
    """AI-powered Exploratory Data Analysis Agent."""

    # Predefined EDA tools the agent can use
    TOOLS = {
        "overview": "Get dataset overview (shape, types, memory, null counts)",
        "describe": "Statistical summary of numeric columns",
        "correlations": "Correlation matrix and top correlations",
        "distributions": "Distribution plots for numeric columns",
        "value_counts": "Value counts for categorical columns",
        "missing_analysis": "Analyze missing value patterns",
        "outliers": "Detect outliers using IQR method",
        "pairplot": "Pairwise scatter plots for numeric columns",
        "time_analysis": "Time-based analysis (if datetime columns exist)",
        "custom": "Run custom analysis based on user query",
    }

    def __init__(self):
        self.schema_compressor = SchemaCompressor()
        self.history_manager = HistoryManager()
        self.scaledown_client = ScaleDownClient()
        self.code_executor = CodeExecutor()
        self.current_df: Optional[pd.DataFrame] = None
        self.current_schema: Optional[Dict] = None
        self.dataset_name: str = "dataset"

    def load_dataset(self, df: pd.DataFrame, name: str = "dataset") -> Dict[str, Any]:
        """Load a dataset and generate compressed schema."""
        self.current_df = df
        self.dataset_name = name
        self.history_manager.clear()

        # Generate compressed schema
        self.current_schema = self.schema_compressor.compress_schema(df, name)
        comparison = self.schema_compressor.get_full_vs_compressed_comparison(df)

        return {
            "schema": self.current_schema,
            "comparison": comparison,
            "compact_repr": self.current_schema["compact_string"],
        }

    def run_auto_eda(self) -> List[Dict[str, Any]]:
        """
        Run automated EDA pipeline — performs a smart sequence of analyses
        based on the dataset characteristics.
        """
        if self.current_df is None:
            return [{"error": "No dataset loaded"}]

        results = []

        # Step 1: Overview
        results.append(self._run_analysis("overview"))

        # Step 2: Statistical description
        results.append(self._run_analysis("describe"))

        # Step 3: Missing value analysis (if there are nulls)
        if self.current_df.isna().any().any():
            results.append(self._run_analysis("missing_analysis"))

        # Step 4: Distributions of numeric columns
        numeric_cols = self.current_df.select_dtypes(include='number').columns
        if len(numeric_cols) > 0:
            results.append(self._run_analysis("distributions"))

        # Step 5: Correlations (if multiple numeric columns)
        if len(numeric_cols) >= 2:
            results.append(self._run_analysis("correlations"))

        # Step 6: Value counts for categorical columns
        cat_cols = self.current_df.select_dtypes(include='object').columns
        if len(cat_cols) > 0:
            results.append(self._run_analysis("value_counts"))

        # Step 7: Outlier detection
        if len(numeric_cols) > 0:
            results.append(self._run_analysis("outliers"))

        return results

    def _run_analysis(self, tool_name: str, query: str = "") -> Dict[str, Any]:
        """Run a specific analysis tool."""
        df = self.current_df
        code = self._generate_code(tool_name, query)

        # Execute the code
        exec_result = self.code_executor.execute(code, df)

        # Create result summary for history
        result_summary = self.code_executor.get_result_summary(exec_result)

        # Compress the result summary using ScaleDown
        compressed = self.scaledown_client.compress(result_summary)
        compressed_summary = compressed.get("compressed_text", result_summary)

        # Track token savings
        tokens_saved = compressed.get("input_tokens", 0) - compressed.get("output_tokens", 0)
        self.history_manager.total_tokens_saved += max(tokens_saved, 0)

        # Add to history
        step = AnalysisStep(
            action=tool_name,
            description=self.TOOLS.get(tool_name, query or tool_name),
            result_summary=compressed_summary,
            code=code,
            chart_path=exec_result.get("chart_path", ""),
            tokens_used=compressed.get("output_tokens", len(result_summary) // 4),
        )
        self.history_manager.add_step(step)

        # Extract key findings
        if exec_result["success"] and exec_result.get("stdout"):
            findings = self._extract_findings(exec_result["stdout"])
            for f in findings:
                self.history_manager.add_finding(f)

        return {
            "tool": tool_name,
            "success": exec_result["success"],
            "stdout": exec_result.get("stdout", ""),
            "result_value": exec_result.get("result_value", ""),
            "chart_path": exec_result.get("chart_path"),
            "error": exec_result.get("error"),
            "code": code,
            "tokens_used": step.tokens_used,
            "compression_savings": compressed.get("savings_pct", 0),
        }

    def run_custom_query(self, query: str) -> Dict[str, Any]:
        """Run a custom analysis based on user query."""
        return self._run_analysis("custom", query)

    def _generate_code(self, tool_name: str, query: str = "") -> str:
        """Generate Python analysis code based on the tool and dataset."""
        df = self.current_df

        if tool_name == "overview":
            return self._code_overview()
        elif tool_name == "describe":
            return self._code_describe()
        elif tool_name == "correlations":
            return self._code_correlations()
        elif tool_name == "distributions":
            return self._code_distributions()
        elif tool_name == "value_counts":
            return self._code_value_counts()
        elif tool_name == "missing_analysis":
            return self._code_missing_analysis()
        elif tool_name == "outliers":
            return self._code_outliers()
        elif tool_name == "pairplot":
            return self._code_pairplot()
        elif tool_name == "time_analysis":
            return self._code_time_analysis()
        elif tool_name == "custom":
            return self._code_custom(query)
        else:
            return f'print("Unknown tool: {tool_name}")'

    def _code_overview(self) -> str:
        return '''
print("=" * 50)
print("DATASET OVERVIEW")
print("=" * 50)
print(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
print(f"Memory Usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
print()
print("Column Types:")
print(df.dtypes.value_counts().to_string())
print()
print("Null Summary:")
null_counts = df.isnull().sum()
null_pcts = (df.isnull().mean() * 100).round(1)
null_df = pd.DataFrame({"Nulls": null_counts, "Pct": null_pcts})
null_df = null_df[null_df["Nulls"] > 0].sort_values("Nulls", ascending=False)
if len(null_df) > 0:
    print(null_df.to_string())
else:
    print("  No missing values!")
print()
print("First 5 rows:")
print(df.head().to_string())
'''

    def _code_describe(self) -> str:
        return '''
print("=" * 50)
print("STATISTICAL SUMMARY")
print("=" * 50)
desc = df.describe(include='all').round(2)
print(desc.to_string())
print()
# Check for columns with zero variance
numeric_cols = df.select_dtypes(include='number').columns
if len(numeric_cols) > 0:
    zero_var = [c for c in numeric_cols if df[c].std() == 0]
    if zero_var:
        print(f"⚠ Zero-variance columns: {zero_var}")
'''

    def _code_correlations(self) -> str:
        return '''
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

numeric_df = df.select_dtypes(include='number')
if len(numeric_df.columns) < 2:
    print("Need at least 2 numeric columns for correlation analysis")
else:
    corr = numeric_df.corr().round(3)
    
    print("=" * 50)
    print("CORRELATION ANALYSIS")
    print("=" * 50)
    
    # Find top correlations
    upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
    pairs = []
    for col in upper.columns:
        for idx in upper.index:
            val = upper.loc[idx, col]
            if pd.notna(val) and abs(val) > 0.3:
                pairs.append((idx, col, val))
    
    pairs.sort(key=lambda x: abs(x[2]), reverse=True)
    
    if pairs:
        print("\\nTop Correlations (|r| > 0.3):")
        for a, b, r in pairs[:10]:
            emoji = "🔴" if abs(r) > 0.7 else "🟡" if abs(r) > 0.5 else "🟢"
            print(f"  {emoji} {a} ↔ {b}: {r:+.3f}")
    else:
        print("\\nNo strong correlations found (|r| > 0.3)")
    
    # Heatmap
    cols_to_plot = numeric_df.columns[:15]  # Limit for readability
    fig, ax = plt.subplots(figsize=(10, 8))
    plt.style.use('dark_background')
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#1a1a2e')
    
    mask = np.triu(np.ones_like(corr.loc[cols_to_plot, cols_to_plot], dtype=bool))
    sns.heatmap(corr.loc[cols_to_plot, cols_to_plot], mask=mask, annot=True, 
                fmt='.2f', cmap='RdYlBu_r', center=0, ax=ax,
                square=True, linewidths=0.5, 
                annot_kws={'size': 8, 'color': 'white'})
    ax.set_title('Correlation Matrix', fontsize=14, color='white', pad=20)
    plt.tight_layout()
'''

    def _code_distributions(self) -> str:
        return '''
import matplotlib.pyplot as plt
import seaborn as sns

numeric_cols = df.select_dtypes(include='number').columns.tolist()
n_cols = min(len(numeric_cols), 12)
plot_cols = numeric_cols[:n_cols]

print("=" * 50)
print("DISTRIBUTION ANALYSIS")
print("=" * 50)

for col in plot_cols:
    skew = df[col].skew()
    kurt = df[col].kurtosis()
    print(f"  {col}: skew={skew:.2f}, kurtosis={kurt:.2f}", end="")
    if abs(skew) > 2:
        print(" ⚠ highly skewed", end="")
    if kurt > 7:
        print(" ⚠ heavy tails", end="")
    print()

# Plot distributions
n_rows = (n_cols + 2) // 3
fig, axes = plt.subplots(n_rows, 3, figsize=(14, 4 * n_rows))
plt.style.use('dark_background')
fig.patch.set_facecolor('#1a1a2e')

axes_flat = axes.flatten() if n_cols > 3 else ([axes] if n_cols == 1 else axes)
if not isinstance(axes_flat, np.ndarray):
    axes_flat = [axes_flat]
else:
    axes_flat = axes_flat.flatten()

colors = ['#6c5ce7', '#00b894', '#fd79a8', '#fdcb6e', '#0984e3', 
          '#e17055', '#a29bfe', '#55efc4', '#fab1a0', '#74b9ff',
          '#ff7675', '#ffeaa7']

for i, col in enumerate(plot_cols):
    ax = axes_flat[i]
    ax.set_facecolor('#16213e')
    try:
        sns.histplot(df[col].dropna(), kde=True, ax=ax, color=colors[i % len(colors)], alpha=0.7)
    except:
        ax.hist(df[col].dropna(), bins=30, color=colors[i % len(colors)], alpha=0.7)
    ax.set_title(col, fontsize=11, color='white')
    ax.tick_params(colors='#888')

# Hide empty subplots
for j in range(n_cols, len(axes_flat)):
    axes_flat[j].set_visible(False)

fig.suptitle('Feature Distributions', fontsize=16, color='white', y=1.02)
plt.tight_layout()
'''

    def _code_value_counts(self) -> str:
        return '''
import matplotlib.pyplot as plt
import seaborn as sns

cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

print("=" * 50)
print("CATEGORICAL ANALYSIS")
print("=" * 50)

for col in cat_cols:
    vc = df[col].value_counts()
    n_unique = len(vc)
    print(f"\\n{col} ({n_unique} unique values):")
    print(vc.head(10).to_string())
    if n_unique > 10:
        print(f"  ... and {n_unique - 10} more")

# Plot top categorical columns (max 6)
plot_cols = [c for c in cat_cols if df[c].nunique() <= 20][:6]
if plot_cols:
    n_plots = len(plot_cols)
    n_rows = (n_plots + 1) // 2
    fig, axes = plt.subplots(n_rows, 2, figsize=(12, 4 * n_rows))
    plt.style.use('dark_background')
    fig.patch.set_facecolor('#1a1a2e')
    
    if n_plots == 1:
        axes_flat = [axes] if not hasattr(axes, '__len__') else axes.flatten()
    else:
        axes_flat = axes.flatten()
    
    colors = ['#6c5ce7', '#00b894', '#fd79a8', '#fdcb6e', '#0984e3', '#e17055']
    
    for i, col in enumerate(plot_cols):
        ax = axes_flat[i]
        ax.set_facecolor('#16213e')
        vc = df[col].value_counts().head(10)
        bars = ax.barh(vc.index.astype(str), vc.values, color=colors[i % len(colors)], alpha=0.8)
        ax.set_title(col, fontsize=11, color='white')
        ax.tick_params(colors='#888')
        ax.invert_yaxis()
    
    for j in range(n_plots, len(axes_flat)):
        axes_flat[j].set_visible(False)
    
    fig.suptitle('Categorical Distributions', fontsize=16, color='white', y=1.02)
    plt.tight_layout()
'''

    def _code_missing_analysis(self) -> str:
        return '''
import matplotlib.pyplot as plt
import seaborn as sns

print("=" * 50)
print("MISSING VALUE ANALYSIS")
print("=" * 50)

null_counts = df.isnull().sum().sort_values(ascending=False)
null_pcts = (df.isnull().mean() * 100).round(1)
total_cells = df.shape[0] * df.shape[1]
total_missing = df.isnull().sum().sum()

print(f"Total missing: {total_missing}/{total_cells} ({total_missing/total_cells*100:.1f}%)")
print()

cols_with_nulls = null_counts[null_counts > 0]
if len(cols_with_nulls) > 0:
    for col in cols_with_nulls.index:
        bar = "█" * int(null_pcts[col] / 5) + "░" * (20 - int(null_pcts[col] / 5))
        print(f"  {col:30s} {bar} {null_pcts[col]:5.1f}% ({null_counts[col]})")
    
    # Plot
    fig, ax = plt.subplots(figsize=(10, max(4, len(cols_with_nulls) * 0.4)))
    plt.style.use('dark_background')
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#16213e')
    
    colors = ['#ff6b6b' if p > 50 else '#feca57' if p > 20 else '#48dbfb' 
              for p in null_pcts[cols_with_nulls.index]]
    
    ax.barh(cols_with_nulls.index.astype(str), null_pcts[cols_with_nulls.index], 
            color=colors, alpha=0.8)
    ax.set_xlabel('Missing %', color='white')
    ax.set_title('Missing Values by Column', fontsize=14, color='white')
    ax.tick_params(colors='#888')
    plt.tight_layout()
else:
    print("  ✅ No missing values found!")
'''

    def _code_outliers(self) -> str:
        return '''
import matplotlib.pyplot as plt
import numpy as np

numeric_cols = df.select_dtypes(include='number').columns.tolist()

print("=" * 50)
print("OUTLIER ANALYSIS (IQR Method)")
print("=" * 50)

outlier_summary = {}
for col in numeric_cols:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    outliers = ((df[col] < lower) | (df[col] > upper)).sum()
    pct = outliers / len(df) * 100
    outlier_summary[col] = {"count": int(outliers), "pct": round(pct, 1), 
                            "lower": round(lower, 2), "upper": round(upper, 2)}
    if outliers > 0:
        print(f"  {col}: {outliers} outliers ({pct:.1f}%) | bounds: [{lower:.2f}, {upper:.2f}]")

total_outlier_cols = sum(1 for v in outlier_summary.values() if v["count"] > 0)
print(f"\\n{total_outlier_cols}/{len(numeric_cols)} columns have outliers")

# Box plots
plot_cols = numeric_cols[:12]
n_cols_plot = len(plot_cols)
n_rows = (n_cols_plot + 2) // 3
fig, axes = plt.subplots(n_rows, 3, figsize=(14, 4 * n_rows))
plt.style.use('dark_background')
fig.patch.set_facecolor('#1a1a2e')

axes_flat = np.array(axes).flatten() if n_cols_plot > 1 else [axes]

for i, col in enumerate(plot_cols):
    ax = axes_flat[i]
    ax.set_facecolor('#16213e')
    bp = ax.boxplot(df[col].dropna(), patch_artist=True, vert=True,
                    boxprops=dict(facecolor='#6c5ce7', alpha=0.7),
                    whiskerprops=dict(color='#a29bfe'),
                    capprops=dict(color='#a29bfe'),
                    medianprops=dict(color='#ffeaa7'),
                    flierprops=dict(marker='o', markerfacecolor='#ff6b6b', markersize=4))
    ax.set_title(f"{col}\\n({outlier_summary[col]['count']} outliers)", 
                fontsize=10, color='white')
    ax.tick_params(colors='#888')

for j in range(n_cols_plot, len(axes_flat)):
    axes_flat[j].set_visible(False)

fig.suptitle('Outlier Detection (Box Plots)', fontsize=16, color='white', y=1.02)
plt.tight_layout()
'''

    def _code_pairplot(self) -> str:
        return '''
import matplotlib.pyplot as plt
import seaborn as sns

numeric_cols = df.select_dtypes(include='number').columns.tolist()[:5]  # Limit to 5

if len(numeric_cols) >= 2:
    plt.style.use('dark_background')
    fig = sns.pairplot(df[numeric_cols].dropna().sample(min(500, len(df))), 
                      diag_kind='hist', plot_kws={'alpha': 0.5, 'color': '#6c5ce7'},
                      diag_kws={'color': '#00b894'})
    fig.fig.patch.set_facecolor('#1a1a2e')
    fig.fig.suptitle('Pairwise Relationships', fontsize=16, color='white', y=1.02)
    print("Pairplot generated for columns:", numeric_cols)
else:
    print("Need at least 2 numeric columns for pairplot")
'''

    def _code_time_analysis(self) -> str:
        return '''
import matplotlib.pyplot as plt

dt_cols = df.select_dtypes(include='datetime').columns.tolist()
if not dt_cols:
    # Try to find date-like columns
    for col in df.select_dtypes(include='object').columns:
        try:
            pd.to_datetime(df[col].head(20))
            dt_cols.append(col)
        except:
            pass

if dt_cols:
    print(f"DateTime columns found: {dt_cols}")
    dt_col = dt_cols[0]
    if df[dt_col].dtype == 'object':
        df[dt_col] = pd.to_datetime(df[dt_col], errors='coerce')
    
    print(f"Range: {df[dt_col].min()} to {df[dt_col].max()}")
    print(f"Span: {(df[dt_col].max() - df[dt_col].min()).days} days")
else:
    print("No datetime columns found")
'''

    def _code_custom(self, query: str) -> str:
        """Generate code for custom analysis queries."""
        # Map common query patterns to code
        query_lower = query.lower()

        if any(w in query_lower for w in ['correlat', 'relationship', 'relation']):
            return self._code_correlations()
        elif any(w in query_lower for w in ['distribut', 'histogram', 'hist']):
            return self._code_distributions()
        elif any(w in query_lower for w in ['missing', 'null', 'nan']):
            return self._code_missing_analysis()
        elif any(w in query_lower for w in ['outlier', 'anomal']):
            return self._code_outliers()
        elif any(w in query_lower for w in ['categor', 'value count', 'unique']):
            return self._code_value_counts()
        elif any(w in query_lower for w in ['describe', 'summary', 'stats', 'statistic']):
            return self._code_describe()
        elif any(w in query_lower for w in ['overview', 'info', 'shape']):
            return self._code_overview()
        elif any(w in query_lower for w in ['pair', 'scatter']):
            return self._code_pairplot()
        elif any(w in query_lower for w in ['time', 'date', 'trend', 'temporal']):
            return self._code_time_analysis()
        else:
            # Generic query — try to interpret
            return f'''
# Custom analysis: {query}
print("=" * 50)
print("CUSTOM ANALYSIS")
print("=" * 50)
print(f"Dataset: {{df.shape[0]}} rows × {{df.shape[1]}} columns")
print()
print("Columns:", list(df.columns))
print()
print(df.describe(include='all').round(2).to_string())
'''

    def _extract_findings(self, stdout: str) -> List[str]:
        """Extract key findings from analysis output."""
        findings = []
        lines = stdout.split('\n')

        for line in lines:
            line = line.strip()
            # Look for lines with significant findings
            if any(marker in line for marker in ['⚠', '🔴', '✅', 'outlier', 'skew', 'correlation']):
                if len(line) > 10 and len(line) < 200:
                    findings.append(line)

        return findings[:5]  # Max 5 findings per step

    def get_context_for_llm(self) -> str:
        """
        Build the complete compressed context for LLM consumption.
        This is the key method that combines schema + history into
        a token-efficient prompt.
        """
        parts = []

        if self.current_schema:
            parts.append("DATASET SCHEMA:")
            parts.append(self.current_schema["compact_string"])
            parts.append("")

        parts.append(self.history_manager.get_compressed_history())

        full_context = "\n".join(parts)

        # Optionally compress further with ScaleDown
        compressed = self.scaledown_client.compress(full_context)
        return compressed.get("compressed_text", full_context)

    def get_token_stats(self) -> Dict[str, Any]:
        """Get comprehensive token usage statistics."""
        schema_stats = {}
        if self.current_df is not None:
            schema_stats = self.schema_compressor.get_full_vs_compressed_comparison(self.current_df)

        history_stats = self.history_manager.get_savings_report()
        api_stats = self.scaledown_client.get_stats()

        return {
            "schema_compression": schema_stats,
            "history_compression": history_stats,
            "scaledown_api": api_stats,
            "total_analysis_steps": len(self.history_manager.steps),
        }
