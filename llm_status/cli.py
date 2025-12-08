"""CLI interface for llm-status."""
import argparse
import sys
from typing import List, Optional
from getpass import getpass

from .config import Config
from .cache import Cache
from .providers import PROVIDERS
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
