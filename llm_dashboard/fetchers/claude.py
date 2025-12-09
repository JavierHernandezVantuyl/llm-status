"""Claude usage fetcher - gets usage from /usage command or claude.ai."""
import re
from datetime import datetime
from typing import Optional
from .base import BaseFetcher, LLMUsage


class ClaudeFetcher(BaseFetcher):
    """Fetch Claude usage from /usage command output."""

    @property
    def provider_name(self) -> str:
        return "claude"

    def fetch_usage(self) -> LLMUsage:
        """Fetch Claude usage.

        For now, prompts user to paste /usage output.
        Future: Could auto-scrape from claude.ai
        """
        print("\n" + "=" * 60)
        print("  Claude Usage - Quick Check")
        print("=" * 60)
        print("\n📋 In Claude Code, run: /usage")
        print("   Or visit: https://claude.ai/settings/usage")
        print("\nThen paste the output here (or press Enter to skip):")
        print("-" * 60)

        # Read multiple lines until empty line
        lines = []
        while True:
            try:
                line = input()
                if not line.strip():
                    break
                lines.append(line)
            except EOFError:
                break

        if not lines:
            return LLMUsage(
                provider="claude",
                messages_used=None,
                messages_limit=None,
                messages_remaining=None,
                reset_time=None,
                plan_type=None,
                last_updated=datetime.now(),
                status="error",
                error_message="No usage data provided. Run /usage in Claude Code."
            )

        # Parse the output
        return self._parse_usage_output("\n".join(lines))

    def _parse_usage_output(self, output: str) -> LLMUsage:
        """Parse /usage command output.

        Example output formats:
        - "You have used 25 of your 45 messages in the current 5-hour window."
        - "Messages: 25/45"
        - "Usage: 25 out of 45 messages"
        """
        # Try different patterns
        patterns = [
            r'(\d+)\s*(?:of|/)\s*(?:your\s*)?(\d+)\s*messages',
            r'Messages:\s*(\d+)\s*/\s*(\d+)',
            r'used\s*(\d+).*?of.*?(\d+)',
        ]

        used = None
        limit = None

        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                used = int(match.group(1))
                limit = int(match.group(2))
                break

        if used is None or limit is None:
            return LLMUsage(
                provider="claude",
                messages_used=None,
                messages_limit=None,
                messages_remaining=None,
                reset_time=None,
                plan_type=None,
                last_updated=datetime.now(),
                status="error",
                error_message="Could not parse usage data. Please check format."
            )

        remaining = limit - used
        plan_type = "free" if limit <= 50 else "pro"

        # Try to extract reset time
        reset_time = None
        reset_patterns = [
            r'resets?\s+in[:\s]+([^.\n]+)',
            r'window\s+resets?\s+in[:\s]+([^.\n]+)',
        ]

        for pattern in reset_patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                reset_time = match.group(1).strip()
                break

        usage = LLMUsage(
            provider="claude",
            messages_used=used,
            messages_limit=limit,
            messages_remaining=remaining,
            reset_time=reset_time,
            plan_type=plan_type,
            last_updated=datetime.now(),
            status="ok"
        )

        usage.status = self.determine_status(usage)
        return usage

    def fetch_from_pasted_output(self, output: str) -> LLMUsage:
        """Fetch usage from pre-pasted /usage output.

        Args:
            output: Output from /usage command

        Returns:
            LLMUsage object
        """
        return self._parse_usage_output(output)
