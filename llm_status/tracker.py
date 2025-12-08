"""Manual usage tracker for web-based LLM services (ChatGPT, Claude web, etc)."""
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timedelta


class ManualTracker:
    """Track manual usage for web-based LLM services without APIs."""

    def __init__(self, tracker_file: Optional[Path] = None):
        """Initialize manual tracker.

        Args:
            tracker_file: Custom tracker file path
        """
        if tracker_file is None:
            tracker_dir = Path.home() / ".llm-status"
            tracker_dir.mkdir(parents=True, exist_ok=True)
            tracker_file = tracker_dir / "manual_usage.json"

        self.tracker_file = Path(tracker_file)
        self._ensure_tracker_file()

    def _ensure_tracker_file(self) -> None:
        """Create tracker file if it doesn't exist."""
        if not self.tracker_file.exists():
            self._write_tracker({
                "providers": {
                    "chatgpt-web": {
                        "limit_per_period": 40,
                        "period_hours": 3,
                        "usage_history": [],
                        "last_reset": time.time()
                    },
                    "claude-web": {
                        "limit_per_period": 45,
                        "period_hours": 5,
                        "usage_history": [],
                        "last_reset": time.time()
                    }
                }
            })

    def _read_tracker(self) -> Dict[str, Any]:
        """Read tracker from disk."""
        try:
            with open(self.tracker_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"providers": {}}

    def _write_tracker(self, data: Dict[str, Any]) -> None:
        """Write tracker to disk."""
        with open(self.tracker_file, 'w') as f:
            json.dump(data, f, indent=2)

    def increment(self, provider: str, count: int = 1) -> Dict[str, Any]:
        """Increment usage count for a provider.

        Args:
            provider: Provider name (e.g., 'chatgpt-web')
            count: Number of prompts to add (default 1)

        Returns:
            Current usage stats
        """
        data = self._read_tracker()

        if provider not in data["providers"]:
            data["providers"][provider] = {
                "limit_per_period": 40,
                "period_hours": 3,
                "usage_history": [],
                "last_reset": time.time()
            }

        provider_data = data["providers"][provider]

        # Clean up old history entries
        self._clean_history(provider_data)

        # Add new usage entry
        provider_data["usage_history"].append({
            "timestamp": time.time(),
            "count": count
        })

        self._write_tracker(data)
        return self.get_usage(provider)

    def get_usage(self, provider: str) -> Dict[str, Any]:
        """Get current usage for a provider.

        Args:
            provider: Provider name

        Returns:
            Usage statistics
        """
        data = self._read_tracker()

        if provider not in data["providers"]:
            return {
                "provider": provider,
                "used": 0,
                "limit": 0,
                "remaining": 0,
                "period_hours": 0,
                "next_reset": None,
                "warning": False
            }

        provider_data = data["providers"][provider]
        self._clean_history(provider_data)

        # Calculate usage in current period
        used = sum(entry["count"] for entry in provider_data["usage_history"])
        limit = provider_data["limit_per_period"]
        remaining = max(0, limit - used)
        period_hours = provider_data["period_hours"]

        # Find oldest entry to determine next reset
        if provider_data["usage_history"]:
            oldest_timestamp = min(entry["timestamp"] for entry in provider_data["usage_history"])
            next_reset = datetime.fromtimestamp(oldest_timestamp + (period_hours * 3600))
        else:
            next_reset = datetime.now() + timedelta(hours=period_hours)

        # Warning if < 20% remaining
        warning = remaining < (limit * 0.2)

        return {
            "provider": provider,
            "used": used,
            "limit": limit,
            "remaining": remaining,
            "period_hours": period_hours,
            "next_reset": next_reset.strftime("%Y-%m-%d %H:%M:%S"),
            "warning": warning,
            "percentage_used": round((used / limit * 100) if limit > 0 else 0, 1)
        }

    def _clean_history(self, provider_data: Dict[str, Any]) -> None:
        """Remove history entries older than the period.

        Args:
            provider_data: Provider data dict
        """
        period_seconds = provider_data["period_hours"] * 3600
        cutoff_time = time.time() - period_seconds

        provider_data["usage_history"] = [
            entry for entry in provider_data["usage_history"]
            if entry["timestamp"] > cutoff_time
        ]

    def reset(self, provider: str) -> None:
        """Manually reset usage for a provider.

        Args:
            provider: Provider name
        """
        data = self._read_tracker()

        if provider in data["providers"]:
            data["providers"][provider]["usage_history"] = []
            data["providers"][provider]["last_reset"] = time.time()
            self._write_tracker(data)

    def set_limit(self, provider: str, limit: int, period_hours: int) -> None:
        """Set custom limit for a provider.

        Args:
            provider: Provider name
            limit: Number of prompts allowed
            period_hours: Period in hours
        """
        data = self._read_tracker()

        if provider not in data["providers"]:
            data["providers"][provider] = {
                "usage_history": [],
                "last_reset": time.time()
            }

        data["providers"][provider]["limit_per_period"] = limit
        data["providers"][provider]["period_hours"] = period_hours
        self._write_tracker(data)

    def get_all_usage(self) -> Dict[str, Dict[str, Any]]:
        """Get usage for all tracked providers.

        Returns:
            Dict of provider name to usage stats
        """
        data = self._read_tracker()
        result = {}

        for provider in data["providers"].keys():
            result[provider] = self.get_usage(provider)

        return result
