"""Tests for display formatting."""
import unittest
from datetime import datetime
from llm_status.providers.base import UsageData
from llm_status.display import (
    format_number,
    format_cost,
    format_status_table,
    format_detailed_usage,
    draw_table
)


class TestDisplayFormatting(unittest.TestCase):
    """Test display formatting functions."""

    def test_format_number(self):
        """Test number formatting with commas."""
        self.assertEqual(format_number(1000), "1,000")
        self.assertEqual(format_number(1000000), "1,000,000")
        self.assertEqual(format_number(None), "N/A")
        self.assertEqual(format_number(0), "0")

    def test_format_cost(self):
        """Test cost formatting."""
        self.assertEqual(format_cost(1.5), "$1.50")
        self.assertEqual(format_cost(0.99), "$0.99")
        self.assertEqual(format_cost(None), "N/A")
        self.assertEqual(format_cost(100), "$100.00")

    def test_draw_table(self):
        """Test ASCII table drawing."""
        headers = ["Name", "Value"]
        rows = [["Test", "123"], ["Example", "456"]]
        result = draw_table(headers, rows)

        # Check that result contains table elements
        self.assertIn("+", result)
        self.assertIn("|", result)
        self.assertIn("-", result)
        self.assertIn("Name", result)
        self.assertIn("Value", result)
        self.assertIn("Test", result)
        self.assertIn("123", result)

    def test_format_status_table(self):
        """Test status table formatting with mocked usage data."""
        # Create mock usage data
        usage_data_list = [
            UsageData(
                provider="openai",
                tokens_used=100000,
                cost_usd=2.50,
                period="month",
                last_updated=datetime(2025, 1, 15, 10, 30, 0),
                quota_available=True
            ),
            UsageData(
                provider="anthropic",
                tokens_used=50000,
                cost_usd=1.25,
                period="month",
                last_updated=datetime(2025, 1, 15, 10, 30, 0),
                quota_available=True
            )
        ]

        result = format_status_table(usage_data_list)

        # Verify output contains expected data
        self.assertIn("OPENAI", result)
        self.assertIn("ANTHROPIC", result)
        self.assertIn("100,000", result)
        self.assertIn("50,000", result)
        self.assertIn("$2.50", result)
        self.assertIn("$1.25", result)
        self.assertIn("OK", result)

    def test_format_detailed_usage(self):
        """Test detailed usage formatting."""
        usage_data = UsageData(
            provider="openai",
            tokens_used=100000,
            prompt_tokens=60000,
            completion_tokens=40000,
            cost_usd=2.50,
            period="month",
            last_updated=datetime(2025, 1, 15, 10, 30, 0),
            quota_available=True,
            error_message="Test note"
        )

        result = format_detailed_usage(usage_data)

        # Verify output contains expected information
        self.assertIn("OPENAI", result)
        self.assertIn("100,000", result)
        self.assertIn("60,000", result)
        self.assertIn("40,000", result)
        self.assertIn("$2.50", result)
        self.assertIn("Test note", result)


class TestMockProvider(unittest.TestCase):
    """Test that providers return expected data structure."""

    def test_openai_stub_returns_valid_data(self):
        """Test OpenAI adapter returns valid UsageData."""
        from llm_status.providers.openai import OpenAIAdapter

        adapter = OpenAIAdapter(api_key="test-key")
        usage = adapter.get_usage()

        # Verify required fields are present
        self.assertEqual(usage.provider, "openai")
        self.assertIsNotNone(usage.tokens_used)
        self.assertIsNotNone(usage.prompt_tokens)
        self.assertIsNotNone(usage.completion_tokens)
        self.assertIsNotNone(usage.cost_usd)
        self.assertIsNotNone(usage.last_updated)

    def test_anthropic_stub_returns_valid_data(self):
        """Test Anthropic adapter returns valid UsageData."""
        from llm_status.providers.anthropic import AnthropicAdapter

        adapter = AnthropicAdapter(api_key="test-key")
        usage = adapter.get_usage()

        self.assertEqual(usage.provider, "anthropic")
        self.assertIsNotNone(usage.tokens_used)
        self.assertIsNotNone(usage.cost_usd)


if __name__ == "__main__":
    unittest.main()
