"""Google Gemini provider adapter."""
from datetime import datetime
from typing import Optional

from .base import ProviderAdapter, UsageData


class GeminiAdapter(ProviderAdapter):
    """Google Gemini API usage tracker.

    Gemini provides usage metadata in API responses. For tracking:
    - Use Google Cloud Console for billing/quota info
    - Parse usageMetadata from API responses
    - Or use Google Cloud Billing API
    """

    @property
    def name(self) -> str:
        return "gemini"

    @property
    def supports_quotas(self) -> bool:
        # Gemini free tier has quotas, but API doesn't report remaining
        return False

    @property
    def supports_costs(self) -> bool:
        # Can calculate costs for paid tier
        return True

    def get_usage(self) -> UsageData:
        """Fetch usage from Gemini API.

        Note: Gemini doesn't provide a usage/billing API endpoint.
        """
        if not self.api_key:
            return UsageData(
                provider=self.name,
                error_message="No API key configured. Run: llm-status add-cred gemini",
                quota_available=False
            )

        # Gemini doesn't have a usage API - would need Google Cloud Billing API
        return UsageData(
            provider=self.name,
            tokens_used=None,
            error_message="Gemini doesn't provide usage API. Check https://aistudio.google.com/app/apikey for quotas.",
            quota_available=True,
            last_updated=datetime.now()
        )

    def _get_stub_usage(self) -> UsageData:
        """Stub implementation showing expected data structure."""
        # Example pricing: Gemini 1.5 Pro is ~$3.50/MTok input, ~$10.50/MTok output
        prompt_tokens = 112000
        completion_tokens = 28000
        total_tokens = prompt_tokens + completion_tokens

        cost = (prompt_tokens / 1_000_000 * 3.5) + (completion_tokens / 1_000_000 * 10.5)

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

    # For production, implement:
    # def _fetch_from_google_cloud_billing(self) -> UsageData:
    #     """Fetch usage from Google Cloud Billing API."""
    #     # Requires google-cloud-billing library and service account
    #     # from google.cloud import billing_v1
    #     # client = billing_v1.CloudBillingClient()
    #     # ... fetch and parse billing data
    #     pass
