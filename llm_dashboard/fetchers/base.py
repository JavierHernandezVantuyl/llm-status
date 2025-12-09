"""Base fetcher interface for LLM usage tracking."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class LLMUsage:
    """Standardized usage data across all LLMs."""
    provider: str                    # e.g., "claude", "openai", "chatgpt-web"
    messages_used: Optional[int]     # Messages/requests used
    messages_limit: Optional[int]    # Message limit for period
    messages_remaining: Optional[int]  # Messages remaining
    reset_time: Optional[str]        # When quota resets (human readable)
    plan_type: Optional[str]         # "free", "pro", "plus", etc.
    last_updated: datetime           # When this data was fetched
    status: str                      # "ok", "warning", "critical", "error"
    error_message: Optional[str] = None  # Error if fetch failed

    @property
    def percentage_used(self) -> float:
        """Calculate percentage used."""
        if self.messages_limit and self.messages_limit > 0:
            return (self.messages_used or 0) / self.messages_limit * 100
        return 0.0

    def to_dict(self) -> dict:
        """Convert to dict for storage."""
        return {
            'provider': self.provider,
            'messages_used': self.messages_used,
            'messages_limit': self.messages_limit,
            'messages_remaining': self.messages_remaining,
            'reset_time': self.reset_time,
            'plan_type': self.plan_type,
            'last_updated': self.last_updated.isoformat(),
            'status': self.status,
            'error_message': self.error_message
        }


class BaseFetcher(ABC):
    """Base class for LLM usage fetchers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return provider name (e.g., 'claude', 'openai')."""
        pass

    @abstractmethod
    def fetch_usage(self) -> LLMUsage:
        """Fetch current usage from the provider.

        Returns:
            LLMUsage object with current usage data

        Raises:
            Exception: If fetch fails
        """
        pass

    @property
    def supports_auto_fetch(self) -> bool:
        """Whether this fetcher can automatically fetch data.

        Returns:
            True if can auto-fetch, False if requires manual input
        """
        return True

    def determine_status(self, usage: LLMUsage) -> str:
        """Determine status based on usage percentage.

        Args:
            usage: LLMUsage object

        Returns:
            Status string: "ok", "warning", "critical", "error"
        """
        if usage.error_message:
            return "error"

        if usage.messages_limit is None or usage.messages_used is None:
            return "unknown"

        percentage = usage.percentage_used

        if percentage >= 95:
            return "critical"
        elif percentage >= 80:
            return "warning"
        else:
            return "ok"
