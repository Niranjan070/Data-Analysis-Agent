"""
Schema Compressor Module
========================
Extracts dataset metadata and compresses it into a token-efficient representation.
This is the KEY innovation — instead of sending full DataFrames or verbose schema 
descriptions to the LLM, we compress them into a compact format that preserves 
all analytical value while dramatically reducing token count.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional


class SchemaCompressor:
    """Compresses dataset schemas into token-efficient representations."""

    # Type abbreviation map for compact representation
    TYPE_MAP = {
        "int64": "i64",
        "int32": "i32",
        "float64": "f64",
        "float32": "f32",
        "object": "str",
        "bool": "bool",
        "datetime64[ns]": "dt",
        "category": "cat",
        "timedelta64[ns]": "td",
    }

    def __init__(self, max_sample_values: int = 3, max_unique_display: int = 5):
        self.max_sample_values = max_sample_values
        self.max_unique_display = max_unique_display

    def compress_schema(self, df: pd.DataFrame, dataset_name: str = "dataset") -> Dict[str, Any]:
        """
        Generate a compressed schema representation of a DataFrame.
        Returns both the structured data and a compact string representation.
        """
        schema = {
            "name": dataset_name,
            "shape": {"rows": len(df), "cols": len(df.columns)},
            "columns": [],
            "memory_mb": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
        }

        for col in df.columns:
            col_info = self._compress_column(df[col])
            schema["columns"].append(col_info)

        schema["compact_string"] = self._to_compact_string(schema)
        schema["token_estimate"] = self._estimate_tokens(schema["compact_string"])

        return schema

    def _compress_column(self, series: pd.Series) -> Dict[str, Any]:
        """Compress a single column's metadata."""
        dtype_str = str(series.dtype)
        compact_type = self.TYPE_MAP.get(dtype_str, dtype_str[:4])

        col_info = {
            "name": series.name,
            "type": compact_type,
            "nulls": int(series.isna().sum()),
            "null_pct": round(series.isna().mean() * 100, 1),
            "unique": int(series.nunique()),
        }

        # Add type-specific stats
        if pd.api.types.is_numeric_dtype(series):
            col_info.update(self._numeric_stats(series))
        elif pd.api.types.is_object_dtype(series) or isinstance(series.dtype, pd.CategoricalDtype):
            col_info.update(self._categorical_stats(series))
        elif pd.api.types.is_datetime64_any_dtype(series):
            col_info.update(self._datetime_stats(series))

        return col_info

    def _numeric_stats(self, series: pd.Series) -> Dict[str, Any]:
        """Extract compressed numeric statistics."""
        clean = series.dropna()
        if len(clean) == 0:
            return {"stats": "all_null"}

        stats = {
            "min": self._format_num(clean.min()),
            "max": self._format_num(clean.max()),
            "mean": self._format_num(clean.mean()),
            "median": self._format_num(clean.median()),
            "std": self._format_num(clean.std()),
        }

        # Detect if column is likely an ID or categorical encoded as numeric
        if clean.nunique() < 20 and clean.nunique() < len(clean) * 0.05:
            stats["likely_categorical"] = True
            stats["values"] = sorted(clean.unique().tolist())[:self.max_unique_display]

        # Detect skewness
        skew_val = clean.skew()
        if abs(skew_val) > 1:
            stats["skew"] = "high_right" if skew_val > 0 else "high_left"

        return {"stats": stats}

    def _categorical_stats(self, series: pd.Series) -> Dict[str, Any]:
        """Extract compressed categorical statistics."""
        clean = series.dropna()
        if len(clean) == 0:
            return {"stats": "all_null"}

        value_counts = clean.value_counts()
        top_n = min(self.max_unique_display, len(value_counts))

        stats = {
            "top_values": {
                str(k): int(v) for k, v in value_counts.head(top_n).items()
            },
            "avg_len": round(clean.astype(str).str.len().mean(), 1),
        }

        # Check if it looks like it could be parsed as numeric or date
        sample = clean.head(20)
        try:
            pd.to_numeric(sample)
            stats["hint"] = "parseable_as_numeric"
        except (ValueError, TypeError):
            try:
                pd.to_datetime(sample)
                stats["hint"] = "parseable_as_datetime"
            except (ValueError, TypeError):
                pass

        return {"stats": stats}

    def _datetime_stats(self, series: pd.Series) -> Dict[str, Any]:
        """Extract compressed datetime statistics."""
        clean = series.dropna()
        if len(clean) == 0:
            return {"stats": "all_null"}

        return {
            "stats": {
                "range": f"{clean.min().strftime('%Y-%m-%d')} to {clean.max().strftime('%Y-%m-%d')}",
                "span_days": (clean.max() - clean.min()).days,
            }
        }

    def _format_num(self, val) -> str:
        """Format a number compactly."""
        if pd.isna(val):
            return "NaN"
        if isinstance(val, (int, np.integer)):
            return str(int(val))
        if abs(val) >= 1e6:
            return f"{val:.2e}"
        if abs(val) < 0.01 and val != 0:
            return f"{val:.4f}"
        return f"{val:.2f}"

    def _to_compact_string(self, schema: Dict[str, Any]) -> str:
        """Convert schema to a compact string representation for LLM consumption."""
        lines = []
        lines.append(f"DS:{schema['name']}|{schema['shape']['rows']}r×{schema['shape']['cols']}c|{schema['memory_mb']}MB")
        lines.append("COLS:")

        for col in schema["columns"]:
            parts = [f"  {col['name']}({col['type']})"]

            if col["null_pct"] > 0:
                parts.append(f"null:{col['null_pct']}%")

            parts.append(f"uniq:{col['unique']}")

            if isinstance(col.get("stats"), dict):
                stats = col["stats"]
                if "min" in stats:
                    parts.append(f"[{stats['min']}..{stats['max']}]")
                    parts.append(f"μ={stats['mean']}")
                if "top_values" in stats:
                    top = list(stats["top_values"].keys())[:3]
                    parts.append(f"top:{','.join(top)}")
                if "range" in stats:
                    parts.append(f"range:{stats['range']}")
                if stats.get("likely_categorical"):
                    parts.append("⚠cat")
                if "skew" in stats:
                    parts.append(f"skew:{stats['skew']}")
                if "hint" in stats:
                    parts.append(f"hint:{stats['hint']}")

            lines.append("|".join(parts))

        return "\n".join(lines)

    def _estimate_tokens(self, text: str) -> int:
        """Rough token estimate (1 token ≈ 4 chars for English text)."""
        return len(text) // 4

    def get_full_vs_compressed_comparison(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Compare token usage between full df.describe() and compressed schema."""
        # Full representation
        full_repr = df.to_string() + "\n" + df.describe().to_string() + "\n" + str(df.dtypes)
        full_tokens = len(full_repr) // 4

        # Compressed representation
        schema = self.compress_schema(df)
        compressed_tokens = schema["token_estimate"]

        return {
            "full_tokens": full_tokens,
            "compressed_tokens": compressed_tokens,
            "savings_pct": round((1 - compressed_tokens / max(full_tokens, 1)) * 100, 1),
            "compression_ratio": round(full_tokens / max(compressed_tokens, 1), 1),
        }
