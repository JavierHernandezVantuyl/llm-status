"""CLI interface for llm-status."""
import argparse
import sys
from typing import List, Optional
from getpass import getpass

from .config import Config
from .cache import Cache
from .providers import PROVIDERS
from .tracker import ManualTracker
from .display import (
    format_status_table,
    format_detailed_usage,
    format_error,
    format_success
)


class CLI:
    """Main CLI application."""

    def __init__(self):
        """Initialize CLI."""
        self.config = Config()
        self.cache = Cache()
        self.tracker = ManualTracker()

    def run(self, args: Optional[List[str]] = None) -> int:
        """Run the CLI application.

        Args:
            args: Command-line arguments (defaults to sys.argv)

        Returns:
            Exit code (0 for success, non-zero for error)
        """
        parser = self._build_parser()
        parsed_args = parser.parse_args(args)

        if not hasattr(parsed_args, 'func'):
            parser.print_help()
            return 1

        try:
            return parsed_args.func(parsed_args)
        except KeyboardInterrupt:
            print("\n\nInterrupted by user.")
            return 130
        except Exception as e:
            print(format_error(f"Unexpected error: {e}"))
            return 1

    def _build_parser(self) -> argparse.ArgumentParser:
        """Build argument parser."""
        parser = argparse.ArgumentParser(
            prog="llm-status",
            description="LLM Status & Usage Checker - Track token usage across multiple LLM providers"
        )

        subparsers = parser.add_subparsers(title="commands", dest="command")

        # Status command
        status_parser = subparsers.add_parser(
            "status",
            help="Show usage status for all providers"
        )
        status_parser.add_argument(
            "--force-refresh",
            action="store_true",
            help="Force refresh from API (bypass cache)"
        )
        status_parser.set_defaults(func=self.cmd_status)

        # Usage command
        usage_parser = subparsers.add_parser(
            "usage",
            help="Show detailed usage for a specific provider"
        )
        usage_parser.add_argument(
            "provider",
            choices=list(PROVIDERS.keys()),
            help="Provider name"
        )
        usage_parser.add_argument(
            "--force-refresh",
            action="store_true",
            help="Force refresh from API (bypass cache)"
        )
        usage_parser.set_defaults(func=self.cmd_usage)

        # Add-cred command
        add_cred_parser = subparsers.add_parser(
            "add-cred",
            help="Add API credentials for a provider"
        )
        add_cred_parser.add_argument(
            "provider",
            choices=list(PROVIDERS.keys()),
            help="Provider name"
        )
        add_cred_parser.add_argument(
            "--api-key",
            help="API key (will prompt if not provided)"
        )
        add_cred_parser.set_defaults(func=self.cmd_add_cred)

        # Clear-cache command
        clear_cache_parser = subparsers.add_parser(
            "clear-cache",
            help="Clear cached usage data"
        )
        clear_cache_parser.add_argument(
            "provider",
            nargs="?",
            choices=list(PROVIDERS.keys()),
            help="Provider name (clears all if not specified)"
        )
        clear_cache_parser.set_defaults(func=self.cmd_clear_cache)

        # Track command (manual usage tracking for web services)
        track_parser = subparsers.add_parser(
            "track",
            help="Manually track web service usage (e.g., ChatGPT web)"
        )
        track_parser.add_argument(
            "provider",
            help="Provider name (e.g., 'chatgpt-web', 'claude-web')"
        )
        track_parser.add_argument(
            "--count",
            type=int,
            default=1,
            help="Number of prompts to add (default: 1)"
        )
        track_parser.set_defaults(func=self.cmd_track)

        # Track-status command
        track_status_parser = subparsers.add_parser(
            "track-status",
            help="Show manual tracking status for web services"
        )
        track_status_parser.add_argument(
            "provider",
            nargs="?",
            help="Provider name (shows all if not specified)"
        )
        track_status_parser.set_defaults(func=self.cmd_track_status)

        # Set-limit command
        set_limit_parser = subparsers.add_parser(
            "set-limit",
            help="Set custom limit for manual tracking"
        )
        set_limit_parser.add_argument(
            "provider",
            help="Provider name"
        )
        set_limit_parser.add_argument(
            "limit",
            type=int,
            help="Number of prompts allowed per period"
        )
        set_limit_parser.add_argument(
            "hours",
            type=int,
            help="Period in hours"
        )
        set_limit_parser.set_defaults(func=self.cmd_set_limit)

        # Reset-tracker command
        reset_tracker_parser = subparsers.add_parser(
            "reset-tracker",
            help="Reset manual usage tracker for a provider"
        )
        reset_tracker_parser.add_argument(
            "provider",
            help="Provider name"
        )
        reset_tracker_parser.set_defaults(func=self.cmd_reset_tracker)

        return parser

    def cmd_status(self, args) -> int:
        """Handle 'status' command."""
        usage_data_list = []

        for provider_name in PROVIDERS.keys():
            usage_data = self._get_usage_data(
                provider_name,
                force_refresh=args.force_refresh
            )
            usage_data_list.append(usage_data)

        print(format_status_table(usage_data_list))
        return 0

    def cmd_usage(self, args) -> int:
        """Handle 'usage' command."""
        usage_data = self._get_usage_data(
            args.provider,
            force_refresh=args.force_refresh
        )
        print(format_detailed_usage(usage_data))
        return 0

    def cmd_add_cred(self, args) -> int:
        """Handle 'add-cred' command."""
        api_key = args.api_key

        if not api_key:
            # Prompt for API key securely
            api_key = getpass(f"Enter API key for {args.provider}: ")

        if not api_key:
            print(format_error("API key cannot be empty"))
            return 1

        self.config.add_credential(args.provider, api_key)
        print(format_success(f"API key added for {args.provider}"))

        # Clear cache for this provider to force refresh with new credentials
        self.cache.clear(args.provider)

        return 0

    def cmd_clear_cache(self, args) -> int:
        """Handle 'clear-cache' command."""
        if args.provider:
            self.cache.clear(args.provider)
            print(format_success(f"Cache cleared for {args.provider}"))
        else:
            self.cache.clear()
            print(format_success("All cache cleared"))
        return 0

    def cmd_track(self, args) -> int:
        """Handle 'track' command - increment manual usage."""
        stats = self.tracker.increment(args.provider, args.count)

        print(f"\n✓ Tracked {args.count} prompt(s) for {args.provider}")
        print(f"\nCurrent Status:")
        print(f"  Used: {stats['used']}/{stats['limit']} ({stats['percentage_used']}%)")
        print(f"  Remaining: {stats['remaining']}")
        print(f"  Next Reset: {stats['next_reset']}")

        if stats['warning']:
            print(f"\n⚠ WARNING: Less than 20% remaining!")

        return 0

    def cmd_track_status(self, args) -> int:
        """Handle 'track-status' command - show manual tracking status."""
        if args.provider:
            stats = self.tracker.get_usage(args.provider)
            self._print_tracking_stats(args.provider, stats)
        else:
            all_stats = self.tracker.get_all_usage()
            if not all_stats:
                print("\nNo tracked providers yet.")
                print("Use 'llm-status track <provider>' to start tracking.")
                return 0

            print("\nManual Tracking Status")
            print("=" * 70)
            for provider, stats in all_stats.items():
                self._print_tracking_stats(provider, stats)
                print("-" * 70)

        return 0

    def cmd_set_limit(self, args) -> int:
        """Handle 'set-limit' command - set custom limits."""
        self.tracker.set_limit(args.provider, args.limit, args.hours)
        print(format_success(
            f"Set limit for {args.provider}: {args.limit} prompts per {args.hours} hours"
        ))
        return 0

    def cmd_reset_tracker(self, args) -> int:
        """Handle 'reset-tracker' command - reset manual tracker."""
        self.tracker.reset(args.provider)
        print(format_success(f"Reset tracker for {args.provider}"))
        return 0

    def _print_tracking_stats(self, provider: str, stats: dict) -> None:
        """Print tracking statistics for a provider."""
        print(f"\n{provider.upper()}")
        print(f"  Used:       {stats['used']}/{stats['limit']} prompts ({stats['percentage_used']}%)")
        print(f"  Remaining:  {stats['remaining']} prompts")
        print(f"  Period:     {stats['period_hours']} hours")
        print(f"  Next Reset: {stats['next_reset']}")

        if stats['warning']:
            print(f"  Status:     ⚠ WARNING - Low remaining!")
        else:
            print(f"  Status:     ✓ OK")

    def _get_usage_data(self, provider_name: str, force_refresh: bool = False):
        """Get usage data for a provider (from cache or API).

        Args:
            provider_name: Provider name
            force_refresh: Force refresh from API

        Returns:
            UsageData object
        """
        # Check cache first (unless force refresh)
        if not force_refresh:
            ttl = self.config.get_setting("cache_ttl_minutes", 15)
            cached_data = self.cache.get(provider_name, ttl_minutes=ttl)
            if cached_data:
                from .providers.base import UsageData
                return UsageData.from_dict(cached_data)

        # Fetch fresh data from provider
        provider_class = PROVIDERS[provider_name]
        api_key = self.config.get_credential(provider_name)
        provider = provider_class(api_key=api_key)

        usage_data = provider.get_usage()

        # Cache the result
        self.cache.set(provider_name, usage_data.to_dict())

        return usage_data


def main():
    """Entry point for the CLI."""
    cli = CLI()
    sys.exit(cli.run())


if __name__ == "__main__":
    main()
