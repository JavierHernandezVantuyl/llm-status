"""Base provider interface for llm-status."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class UsageData:
    """Standardized usage data structure."""
    provider: str
    tokens_used: Optional[int] = None
    tokens_remaining: Optional[int] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    cost_usd: Optional[float] = None
    period: str = "session"  # session, day, week, month
    last_updated: Optional[datetime] = None
    quota_available: bool = True
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "provider": self.provider,
            "tokens_used": self.tokens_used,
            "tokens_remaining": self.tokens_remaining,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "cost_usd": self.cost_usd,
            "period": self.period,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "quota_available": self.quota_available,
            "error_message": self.error_message
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UsageData':
        """Create from dictionary."""
        if data.get("last_updated"):
            data["last_updated"] = datetime.fromisoformat(data["last_updated"])
        return cls(**data)


class ProviderAdapter(ABC):
    """Base class for provider adapters."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize provider adapter.

        Args:
            api_key: API key for the provider
        """
        self.api_key = api_key

    @abstractmethod
    def get_usage(self) -> UsageData:
        """Fetch current usage data from the provider.

        Returns:
            UsageData object with current usage information
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name."""
        pass

    @property
    def supports_quotas(self) -> bool:
        """Whether this provider supports quota reporting."""
        return False

    @property
    def supports_costs(self) -> bool:
        """Whether this provider supports cost reporting."""
        return False
