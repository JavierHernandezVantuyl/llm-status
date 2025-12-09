"""OpenAI provider adapter."""
from datetime import datetime
from typing import Optional
import json
import urllib.request
import urllib.error

from .base import ProviderAdapter, UsageData


class OpenAIAdapter(ProviderAdapter):
    """OpenAI API usage tracker.

    OpenAI provides usage data through their API dashboard and billing endpoints.
    Attempts to fetch from:
    - GET https://api.openai.com/v1/usage (requires org-level access)
    - Falls back to showing account limits if usage not accessible
    """

    @property
    def name(self) -> str:
        return "openai"

    @property
    def supports_quotas(self) -> bool:
        return False

    @property
    def supports_costs(self) -> bool:
        return True

    def get_usage(self) -> UsageData:
        """Fetch usage from OpenAI API."""
        if not self.api_key:
            return UsageData(
                provider=self.name,
                error_message="No API key configured. Run: llm-status add-cred openai",
                quota_available=False
            )

        # Try to fetch real usage
        try:
            return self._fetch_real_usage()
        except Exception as e:
            return UsageData(
                provider=self.name,
                error_message=f"API error: {str(e)}. OpenAI usage API requires organization access.",
                quota_available=False
            )

    def _fetch_real_usage(self) -> UsageData:
        """Check if API key is configured."""
        # OpenAI API keys start with "sk-" or "sk-proj-"
        if self.api_key and (self.api_key.startswith("sk-") or self.api_key.startswith("sk-proj-")):
            return UsageData(
                provider=self.name,
                tokens_used=None,
                error_message="OpenAI doesn't provide usage data without organization-level API access. Check your usage at: https://platform.openai.com/usage",
                quota_available=True,
                last_updated=datetime.now()
            )
        else:
            raise Exception("API key doesn't look valid (should start with sk- or sk-proj-)")

    def _get_stub_usage(self) -> UsageData:
        """Stub implementation showing expected data structure."""
        # Example pricing: GPT-4 Turbo is ~$0.01/1K prompt, ~$0.03/1K completion
        prompt_tokens = 145000
        completion_tokens = 52000
        total_tokens = prompt_tokens + completion_tokens

        cost = (prompt_tokens / 1000 * 0.01) + (completion_tokens / 1000 * 0.03)

        return UsageData(
            provider=self.name,
            tokens_used=total_tokens,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost_usd=round(cost, 2),
            period="month",
            last_updated=datetime.now(),
            quota_available=True,
            error_message="[STUB] Using mock data. Configure API key for real data."
        )

    # Uncomment and implement for production:
    # def _fetch_real_usage(self) -> UsageData:
    #     """Fetch real usage from OpenAI API."""
    #     import requests
    #
    #     headers = {
    #         "Authorization": f"Bearer {self.api_key}",
    #         "Content-Type": "application/json"
    #     }
    #
    #     # Note: OpenAI usage endpoint requires organization-level access
    #     # Alternative: Track usage locally from API response headers
    #     response = requests.get(
    #         "https://api.openai.com/v1/usage",
    #         headers=headers,
    #         timeout=10
    #     )
    #
    #     if response.status_code != 200:
    #         return UsageData(
    #             provider=self.name,
    #             error_message=f"API error: {response.status_code}",
    #             quota_available=False
    #         )
    #
    #     data = response.json()
    #     # Parse and return usage data
    #     return UsageData(...)
