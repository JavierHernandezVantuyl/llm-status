"""Anthropic (Claude) provider adapter."""
from datetime import datetime
from typing import Optional

from .base import ProviderAdapter, UsageData


class AnthropicAdapter(ProviderAdapter):
    """Anthropic API usage tracker.

    Anthropic includes usage info in API response headers but doesn't have
    a dedicated billing endpoint. Best approach is to:
    - Track usage from x-api-usage headers in responses
    - Monitor via Anthropic Console (web UI)
    - Implement local tracking/logging
    """

    @property
    def name(self) -> str:
        return "anthropic"

    @property
    def supports_quotas(self) -> bool:
        # Anthropic has rate limits but quotas not directly queryable
        return False

    @property
    def supports_costs(self) -> bool:
        # Can calculate costs based on published pricing
        return True

    def get_usage(self) -> UsageData:
        """Fetch usage from Anthropic.

        Note: This is a stub implementation. To use real data:
        1. Add your Anthropic API key via: llm-status add-cred anthropic
        2. Implement local tracking by monitoring API call headers
        3. Parse x-api-usage response header from Claude API calls
        """
        if not self.api_key:
            return UsageData(
                provider=self.name,
                error_message="No API key configured. Run: llm-status add-cred anthropic",
                quota_available=False
            )

        # STUB: Replace with real tracking
        return self._get_stub_usage()

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
