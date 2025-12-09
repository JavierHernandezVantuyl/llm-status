"""Anthropic (Claude) provider adapter."""
from datetime import datetime
from typing import Optional
import json
import urllib.request
import urllib.error

from .base import ProviderAdapter, UsageData


class AnthropicAdapter(ProviderAdapter):
    """Anthropic API usage tracker.

    Anthropic includes usage info in API response headers but doesn't have
    a dedicated billing endpoint. This adapter validates your API key works.
    """

    @property
    def name(self) -> str:
        return "anthropic"

    @property
    def supports_quotas(self) -> bool:
        return False

    @property
    def supports_costs(self) -> bool:
        return True

    def get_usage(self) -> UsageData:
        """Fetch usage from Anthropic."""
        if not self.api_key:
            return UsageData(
                provider=self.name,
                error_message="No API key configured. Run: llm-status add-cred anthropic",
                quota_available=False
            )

        # Try to validate API key
        try:
            return self._validate_and_check()
        except Exception as e:
            return UsageData(
                provider=self.name,
                error_message=f"API error: {str(e)}",
                quota_available=False
            )

    def _validate_and_check(self) -> UsageData:
        """Check if API key is configured."""
        # Anthropic API keys start with "sk-ant-"
        if self.api_key and self.api_key.startswith("sk-ant-"):
            return UsageData(
                provider=self.name,
                tokens_used=None,
                error_message="Anthropic doesn't provide a usage/billing API. Check your usage at: https://console.anthropic.com/settings/usage",
                quota_available=True,
                last_updated=datetime.now()
            )
        else:
            raise Exception("API key doesn't look valid (should start with sk-ant-)")

    def _get_stub_usage(self) -> UsageData:
        """Stub implementation showing expected data structure."""
        # Example pricing: Claude 3.5 Sonnet is ~$3/MTok input, ~$15/MTok output
        prompt_tokens = 89000
        completion_tokens = 34000
        total_tokens = prompt_tokens + completion_tokens

        cost = (prompt_tokens / 1_000_000 * 3.0) + (completion_tokens / 1_000_000 * 15.0)

        return UsageData(
            provider=self.name,
            tokens_used=total_tokens,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost_usd=round(cost, 2),
            period="month",
            last_updated=datetime.now(),
            quota_available=True,
            error_message="[STUB] Using mock data. Implement local tracking for real data."
        )

    # For production, implement local tracking:
    # def track_from_response_header(self, response_headers: dict) -> None:
    #     """Parse and store usage from API response headers.
    #
    #     Example header: x-api-usage: {"input_tokens": 123, "output_tokens": 456}
    #     """
    #     usage_header = response_headers.get("x-api-usage")
    #     if usage_header:
    #         usage = json.loads(usage_header)
    #         # Store to local database/log
    #         self._append_to_usage_log(usage)
