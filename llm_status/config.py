"""Configuration management for llm-status."""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """Manages configuration and credentials storage."""

    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize config manager.

        Args:
            config_dir: Custom config directory (defaults to ~/.llm-status)
        """
        if config_dir is None:
            config_dir = Path.home() / ".llm-status"

        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "config.json"
        self._ensure_config_dir()

    def _ensure_config_dir(self) -> None:
        """Create config directory if it doesn't exist."""
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Initialize config file if it doesn't exist
        if not self.config_file.exists():
            self._write_config({
                "credentials": {},
                "settings": {
                    "cache_ttl_minutes": 15,
                    "auto_update_hours": 24
                }
            })

    def _read_config(self) -> Dict[str, Any]:
        """Read config from disk."""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"credentials": {}, "settings": {}}

    def _write_config(self, config: Dict[str, Any]) -> None:
        """Write config to disk."""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)

    def add_credential(self, provider: str, api_key: str) -> None:
        """Add API credential for a provider.

        Args:
            provider: Provider name (e.g., 'openai', 'anthropic')
            api_key: API key
        """
        config = self._read_config()
        if "credentials" not in config:
            config["credentials"] = {}
        config["credentials"][provider] = {"api_key": api_key}
        self._write_config(config)

    def get_credential(self, provider: str) -> Optional[str]:
        """Get API credential for a provider.

        Args:
            provider: Provider name

        Returns:
            API key or None if not found
        """
        config = self._read_config()
        creds = config.get("credentials", {}).get(provider, {})
        return creds.get("api_key")

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value.

        Args:
            key: Setting key
            default: Default value if not found

        Returns:
            Setting value or default
        """
        config = self._read_config()
        return config.get("settings", {}).get(key, default)

    def set_setting(self, key: str, value: Any) -> None:
        """Set a setting value.

        Args:
            key: Setting key
            value: Setting value
        """
        config = self._read_config()
        if "settings" not in config:
            config["settings"] = {}
        config["settings"][key] = value
        self._write_config(config)
