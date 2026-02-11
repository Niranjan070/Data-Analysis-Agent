"""
Analysis History Manager
========================
Tracks all analysis steps performed on a dataset and compresses the history
for efficient LLM context usage. Instead of keeping the full conversation,
we maintain a rolling summary of what's been done and what was found.
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional


class AnalysisStep:
    """Represents a single analysis step."""

    def __init__(self, action: str, description: str, result_summary: str,
                 code: str = "", chart_path: str = "", tokens_used: int = 0):
        self.action = action
        self.description = description
        self.result_summary = result_summary
        self.code = code
        self.chart_path = chart_path
        self.tokens_used = tokens_used
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "description": self.description,
            "result_summary": self.result_summary,
            "code": self.code,
            "chart_path": self.chart_path,
            "tokens_used": self.tokens_used,
            "timestamp": self.timestamp,
        }

    def to_compact(self) -> str:
        """Compact single-line representation for history compression."""
        parts = [f"[{self.action}]", self.description]
        if self.result_summary:
            # Truncate long results
            summary = self.result_summary[:150] + "..." if len(self.result_summary) > 150 else self.result_summary
            parts.append(f"→ {summary}")
        if self.chart_path:
            parts.append("📊")
        return " | ".join(parts)


class HistoryManager:
    """Manages and compresses analysis history for token efficiency."""

    def __init__(self, max_detailed_steps: int = 5, max_summary_steps: int = 20):
        self.steps: List[AnalysisStep] = []
        self.max_detailed_steps = max_detailed_steps
        self.max_summary_steps = max_summary_steps
        self.key_findings: List[str] = []
        self.total_tokens_used: int = 0
        self.total_tokens_saved: int = 0

    def add_step(self, step: AnalysisStep):
        """Add a new analysis step."""
        self.steps.append(step)
        self.total_tokens_used += step.tokens_used

    def add_finding(self, finding: str):
        """Add a key finding discovered during analysis."""
        self.key_findings.append(finding)

    def get_compressed_history(self) -> str:
        """
        Get a compressed representation of the analysis history.
        
        Strategy:
        - Most recent N steps are shown in detail
        - Older steps are shown as compact one-liners
        - Very old steps are summarized into a single paragraph
        - Key findings are always preserved
        """
        if not self.steps:
            return "No analysis performed yet."

        lines = []

        # Key findings section (always included)
        if self.key_findings:
            lines.append("KEY FINDINGS:")
            for i, finding in enumerate(self.key_findings[-10:], 1):  # Last 10 findings
                lines.append(f"  {i}. {finding}")
            lines.append("")

        total = len(self.steps)

        # Split into tiers
        if total <= self.max_detailed_steps:
            # All steps fit in detailed view
            lines.append(f"ANALYSIS HISTORY ({total} steps):")
            for step in self.steps:
                lines.append(f"  • {step.to_compact()}")
        else:
            # Tier 1: Very old steps → ultra-compact summary
            old_cutoff = max(0, total - self.max_summary_steps)
            if old_cutoff > 0:
                actions = [s.action for s in self.steps[:old_cutoff]]
                action_counts = {}
                for a in actions:
                    action_counts[a] = action_counts.get(a, 0) + 1
                summary_parts = [f"{v}x {k}" for k, v in action_counts.items()]
                lines.append(f"EARLIER: {old_cutoff} steps ({', '.join(summary_parts)})")
                lines.append("")

            # Tier 2: Recent steps → compact one-liners
            recent_start = max(old_cutoff, total - self.max_summary_steps)
            detail_start = total - self.max_detailed_steps

            if recent_start < detail_start:
                lines.append("RECENT STEPS:")
                for step in self.steps[recent_start:detail_start]:
                    lines.append(f"  → {step.to_compact()}")
                lines.append("")

            # Tier 3: Latest steps → detailed
            lines.append("LATEST STEPS:")
            for step in self.steps[detail_start:]:
                lines.append(f"  • [{step.action}] {step.description}")
                if step.result_summary:
                    lines.append(f"    Result: {step.result_summary[:200]}")
                if step.chart_path:
                    lines.append(f"    Chart: {step.chart_path}")

        # Token usage summary
        lines.append("")
        lines.append(f"TOKENS: used={self.total_tokens_used}, saved={self.total_tokens_saved}")

        return "\n".join(lines)

    def get_full_history(self) -> List[Dict[str, Any]]:
        """Get the full uncompressed history for display purposes."""
        return [step.to_dict() for step in self.steps]

    def get_stats(self) -> Dict[str, Any]:
        """Get history statistics."""
        return {
            "total_steps": len(self.steps),
            "total_tokens_used": self.total_tokens_used,
            "total_tokens_saved": self.total_tokens_saved,
            "key_findings_count": len(self.key_findings),
            "actions_performed": list(set(s.action for s in self.steps)),
        }

    def estimate_uncompressed_tokens(self) -> int:
        """Estimate tokens if we sent the full history uncompressed."""
        full = json.dumps(self.get_full_history())
        return len(full) // 4

    def estimate_compressed_tokens(self) -> int:
        """Estimate tokens for the compressed history."""
        compressed = self.get_compressed_history()
        return len(compressed) // 4

    def get_savings_report(self) -> Dict[str, Any]:
        """Report on token savings from history compression."""
        uncompressed = self.estimate_uncompressed_tokens()
        compressed = self.estimate_compressed_tokens()
        return {
            "uncompressed_tokens": uncompressed,
            "compressed_tokens": compressed,
            "savings_pct": round((1 - compressed / max(uncompressed, 1)) * 100, 1),
        }

    def clear(self):
        """Clear all history."""
        self.steps.clear()
        self.key_findings.clear()
        self.total_tokens_used = 0
        self.total_tokens_saved = 0
