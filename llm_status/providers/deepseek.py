"""DeepSeek provider adapter."""
from datetime import datetime
from typing import Optional

from .base import ProviderAdapter, UsageData


class DeepSeekAdapter(ProviderAdapter):
    """DeepSeek API usage tracker.

    DeepSeek API usage tracking may vary. Best approach:
    - Check DeepSeek API documentation for usage endpoints
    - Track usage from API response headers/metadata
    - Implement local tracking/logging
    """

    @property
    def name(self) -> str:
        return "deepseek"

    @property
    def supports_quotas(self) -> bool:
        # Depends on DeepSeek API implementation
        return False

    @property
    def supports_costs(self) -> bool:
        # Can calculate if pricing is published
        return True

    def get_usage(self) -> UsageData:
        """Fetch usage from DeepSeek API.

        Note: DeepSeek usage API endpoint not yet implemented.
        """
        if not self.api_key:
            return UsageData(
                provider=self.name,
                error_message="No API key configured. Run: llm-status add-cred deepseek",
                quota_available=False
            )

        # DeepSeek usage API not yet implemented
        return UsageData(
            provider=self.name,
            tokens_used=None,
            error_message="DeepSeek usage API not yet implemented. Check https://platform.deepseek.com for your usage.",
            quota_available=True,
            last_updated=datetime.now()
        )

    def _get_stub_usage(self) -> UsageData:
        """Stub implementation showing expected data structure."""
        # Example pricing: Assuming competitive pricing similar to other providers
        prompt_tokens = 67000
        completion_tokens = 18000
        total_tokens = prompt_tokens + completion_tokens

        # Using example pricing (adjust based on actual DeepSeek pricing)
        cost = (prompt_tokens / 1_000_000 * 0.14) + (completion_tokens / 1_000_000 * 0.28)

        return UsageData(
            provider=self.name,
            tokens_used=total_tokens,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost_usd=round(cost, 2),
            period="month",
            last_updated=datetime.now(),
            quota_available=True,
            error_message="[STUB] Using mock data. Check DeepSeek docs for real API."
        )

    # For production, implement based on DeepSeek API:
    # def _fetch_real_usage(self) -> UsageData:
    #     """Fetch real usage from DeepSeek API."""
    #     import requests
    #
    #     headers = {
    #         "Authorization": f"Bearer {self.api_key}",
    #         "Content-Type": "application/json"
    #     }
    #
    #     # Check DeepSeek API documentation for correct endpoint
    #     response = requests.get(
    #         "https://api.deepseek.com/v1/usage",  # Example endpoint
    #         headers=headers,
    #         timeout=10
    #     )
    #     # Parse and return usage data
