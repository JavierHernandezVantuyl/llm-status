"""Cache management for llm-status."""
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional


class Cache:
    """Manages usage data caching with TTL."""

    def __init__(self, cache_file: Optional[Path] = None):
        """Initialize cache manager.

        Args:
            cache_file: Custom cache file path (defaults to ~/.llm-status/cache.json)
        """
        if cache_file is None:
            cache_dir = Path.home() / ".llm-status"
            cache_dir.mkdir(parents=True, exist_ok=True)
            cache_file = cache_dir / "cache.json"

        self.cache_file = Path(cache_file)
        self._ensure_cache_file()

    def _ensure_cache_file(self) -> None:
        """Create cache file if it doesn't exist."""
        if not self.cache_file.exists():
            self._write_cache({})

    def _read_cache(self) -> Dict[str, Any]:
        """Read cache from disk."""
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _write_cache(self, cache: Dict[str, Any]) -> None:
        """Write cache to disk."""
        with open(self.cache_file, 'w') as f:
            json.dump(cache, f, indent=2)

    def get(self, provider: str, ttl_minutes: int = 15) -> Optional[Dict[str, Any]]:
        """Get cached usage data for a provider.

        Args:
            provider: Provider name
            ttl_minutes: Cache TTL in minutes

        Returns:
            Cached data or None if expired/missing
        """
        cache = self._read_cache()
        provider_data = cache.get(provider)

        if provider_data is None:
            return None

        # Check if cache is still valid
        cached_time = provider_data.get("cached_at", 0)
        current_time = time.time()
        age_minutes = (current_time - cached_time) / 60

        if age_minutes > ttl_minutes:
            return None

        return provider_data.get("data")

    def set(self, provider: str, data: Dict[str, Any]) -> None:
        """Cache usage data for a provider.

        Args:
            provider: Provider name
            data: Usage data to cache
        """
        cache = self._read_cache()
        cache[provider] = {
            "cached_at": time.time(),
            "data": data
        }
        self._write_cache(cache)

    def clear(self, provider: Optional[str] = None) -> None:
        """Clear cache for a provider or all providers.

        Args:
            provider: Provider name, or None to clear all
        """
        if provider is None:
            self._write_cache({})
        else:
            cache = self._read_cache()
            cache.pop(provider, None)
            self._write_cache(cache)
