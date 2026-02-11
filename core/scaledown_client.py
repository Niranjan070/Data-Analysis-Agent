"""
ScaleDown API Client
====================
Integrates with the ScaleDown prompt compression API to further reduce
token usage before sending prompts to any LLM.

API Endpoint: https://api.scaledown.xyz/compress/raw/
Auth: x-api-key header
"""

import requests
import json
import time
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import os

load_dotenv()


class ScaleDownClient:
    """Client for the ScaleDown prompt compression API."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SCALEDOWN_API_KEY", "")
        self.api_url = os.getenv("SCALEDOWN_API_URL", "https://api.scaledown.xyz/compress/raw/")
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_requests = 0
        self.compression_history = []

    def compress(self, text: str, target_ratio: float = 0.5) -> Dict[str, Any]:
        """
        Compress text using the ScaleDown API.
        
        Args:
            text: The text/prompt to compress
            target_ratio: Target compression ratio (0.0-1.0, lower = more compressed)
            
        Returns:
            Dict with compressed text, stats, and metadata
        """
        if not self.api_key:
            return self._fallback_compress(text)

        start_time = time.time()

        try:
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json",
            }

            payload = {
                "text": text,
                "target_ratio": target_ratio,
            }

            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30,
            )

            elapsed = time.time() - start_time

            if response.status_code == 200:
                result = response.json()
                compressed_text = result.get("compressed", result.get("text", text))

                input_tokens = len(text) // 4
                output_tokens = len(compressed_text) // 4

                self.total_input_tokens += input_tokens
                self.total_output_tokens += output_tokens
                self.total_requests += 1

                stats = {
                    "success": True,
                    "compressed_text": compressed_text,
                    "original_length": len(text),
                    "compressed_length": len(compressed_text),
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "savings_pct": round((1 - len(compressed_text) / max(len(text), 1)) * 100, 1),
                    "latency_ms": round(elapsed * 1000, 1),
                    "api_response": result,
                }

                self.compression_history.append(stats)
                return stats

            else:
                # API error — use fallback
                print(f"ScaleDown API returned {response.status_code}: {response.text}")
                fallback = self._fallback_compress(text)
                fallback["api_error"] = f"HTTP {response.status_code}"
                return fallback

        except requests.exceptions.RequestException as e:
            print(f"ScaleDown API error: {e}")
            fallback = self._fallback_compress(text)
            fallback["api_error"] = str(e)
            return fallback

    def _fallback_compress(self, text: str) -> Dict[str, Any]:
        """
        Local fallback compression when API is unavailable.
        Uses heuristic text compression techniques.
        """
        compressed = self._heuristic_compress(text)

        input_tokens = len(text) // 4
        output_tokens = len(compressed) // 4

        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_requests += 1

        return {
            "success": True,
            "compressed_text": compressed,
            "original_length": len(text),
            "compressed_length": len(compressed),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "savings_pct": round((1 - len(compressed) / max(len(text), 1)) * 100, 1),
            "latency_ms": 0,
            "method": "local_fallback",
        }

    def _heuristic_compress(self, text: str) -> str:
        """
        Apply heuristic text compression:
        - Remove redundant whitespace
        - Abbreviate common words
        - Remove filler phrases
        - Compact formatting
        """
        import re

        result = text

        # Remove extra whitespace
        result = re.sub(r'\n{3,}', '\n\n', result)
        result = re.sub(r' {2,}', ' ', result)
        result = re.sub(r'\t', ' ', result)

        # Remove filler phrases common in data descriptions
        fillers = [
            r'\bplease note that\b',
            r'\bit is important to\b',
            r'\bit should be noted that\b',
            r'\bas we can see\b',
            r'\bin other words\b',
            r'\bbasically\b',
            r'\bessentially\b',
            r'\bthe following\b',
        ]
        for filler in fillers:
            result = re.sub(filler, '', result, flags=re.IGNORECASE)

        # Abbreviate common data terms
        abbreviations = {
            'column': 'col',
            'columns': 'cols',
            'number': 'num',
            'average': 'avg',
            'maximum': 'max',
            'minimum': 'min',
            'standard deviation': 'std',
            'correlation': 'corr',
            'distribution': 'dist',
            'percentage': 'pct',
            'approximately': '~',
            'greater than': '>',
            'less than': '<',
            'missing values': 'nulls',
            'null values': 'nulls',
        }
        for full, short in abbreviations.items():
            result = re.sub(r'\b' + full + r'\b', short, result, flags=re.IGNORECASE)

        # Clean up extra spaces from removals
        result = re.sub(r' {2,}', ' ', result)
        result = result.strip()

        return result

    def get_stats(self) -> Dict[str, Any]:
        """Get cumulative compression statistics."""
        return {
            "total_requests": self.total_requests,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens_saved": self.total_input_tokens - self.total_output_tokens,
            "overall_savings_pct": round(
                (1 - self.total_output_tokens / max(self.total_input_tokens, 1)) * 100, 1
            ),
        }

    def test_connection(self) -> Dict[str, Any]:
        """Test the ScaleDown API connection."""
        test_text = "This is a test prompt to verify the ScaleDown API connection is working properly."
        result = self.compress(test_text)
        return {
            "connected": result.get("success", False),
            "method": result.get("method", "api"),
            "api_error": result.get("api_error", None),
        }
