"""Terminal display for LLM usage dashboard."""
from typing import List
from .fetchers.base import LLMUsage


def format_usage_table(usages: List[LLMUsage]) -> str:
    """Format multiple LLM usages as a table.

    Args:
        usages: List of LLMUsage objects

    Returns:
        Formatted table string
    """
    if not usages:
        return "\nNo usage data available.\n"

    # Calculate column widths
    col_widths = {
        'provider': max(len("Provider"), max(len(u.provider.upper()) for u in usages)),
        'used': max(len("Used"), max(len(str(u.messages_used or "N/A")) for u in usages)),
        'limit': max(len("Limit"), max(len(str(u.messages_limit or "N/A")) for u in usages)),
        'remaining': max(len("Remaining"), max(len(str(u.messages_remaining or "N/A")) for u in usages)),
        'status': max(len("Status"), 8),
    }

    # Build table
    lines = []
    lines.append("\n" + "=" * 80)
    lines.append("  LLM Usage Dashboard")
    lines.append("=" * 80)

    # Header
    header = (f"{'Provider':<{col_widths['provider']}}  "
              f"{'Used':>{col_widths['used']}}  "
              f"{'Limit':>{col_widths['limit']}}  "
              f"{'Remaining':>{col_widths['remaining']}}  "
              f"{'%':>6}  "
              f"{'Status':<{col_widths['status']}}")
    lines.append(header)
    lines.append("-" * 80)

    # Rows
    for usage in usages:
        provider = usage.provider.upper()
        used = str(usage.messages_used) if usage.messages_used is not None else "N/A"
        limit = str(usage.messages_limit) if usage.messages_limit is not None else "N/A"
        remaining = str(usage.messages_remaining) if usage.messages_remaining is not None else "N/A"
        percentage = f"{usage.percentage_used:>5.1f}" if usage.messages_limit else "  N/A"

        # Status with emoji
        status_display = {
            "ok": "✓ OK",
            "warning": "⚠ WARN",
            "critical": "🔴 CRIT",
            "error": "❌ ERROR",
            "unknown": "? UNKNOWN"
        }.get(usage.status, usage.status)

        row = (f"{provider:<{col_widths['provider']}}  "
               f"{used:>{col_widths['used']}}  "
               f"{limit:>{col_widths['limit']}}  "
               f"{remaining:>{col_widths['remaining']}}  "
               f"{percentage}%  "
               f"{status_display:<{col_widths['status']}}")
        lines.append(row)

    lines.append("=" * 80)

    # Show details for any errors or warnings
    has_issues = False
    for usage in usages:
        if usage.status in ["error", "warning", "critical"]:
            if not has_issues:
                lines.append("\nDetails:")
                lines.append("-" * 80)
                has_issues = True

            lines.append(f"\n{usage.provider.upper()}:")
            if usage.error_message:
                lines.append(f"  {usage.error_message}")
            if usage.status == "critical":
                lines.append(f"  🔴 CRITICAL: Only {usage.messages_remaining} messages left!")
            elif usage.status == "warning":
                lines.append(f"  ⚠️  WARNING: {usage.messages_remaining} messages remaining")
            if usage.reset_time:
                lines.append(f"  Resets in: {usage.reset_time}")
            if usage.plan_type:
                lines.append(f"  Plan: {usage.plan_type.upper()}")

    if has_issues:
        lines.append("=" * 80)

    lines.append("")
    return "\n".join(lines)


def format_single_usage(usage: LLMUsage) -> str:
    """Format single LLM usage with details.

    Args:
        usage: LLMUsage object

    Returns:
        Formatted string
    """
    lines = []
    lines.append("\n" + "=" * 60)
    lines.append(f"  {usage.provider.upper()} Usage")
    lines.append("=" * 60)

    lines.append(f"Last Updated    : {usage.last_updated.strftime('%Y-%m-%d %H:%M:%S')}")

    if usage.plan_type:
        lines.append(f"Plan Type       : {usage.plan_type.upper()}")

    if usage.messages_used is not None and usage.messages_limit is not None:
        lines.append(f"Messages Used   : {usage.messages_used}/{usage.messages_limit} ({usage.percentage_used:.1f}%)")
        lines.append(f"Remaining       : {usage.messages_remaining} messages")
    else:
        lines.append(f"Messages        : N/A")

    if usage.reset_time:
        lines.append(f"Resets In       : {usage.reset_time}")

    # Status with color
    status_display = {
        "ok": "✓ OK - Plenty remaining",
        "warning": "⚠️  WARNING - Running low",
        "critical": "🔴 CRITICAL - Very few messages left!",
        "error": "❌ ERROR - Could not fetch data",
        "unknown": "? UNKNOWN"
    }.get(usage.status, usage.status)

    lines.append(f"Status          : {status_display}")

    if usage.error_message:
        lines.append("")
        lines.append(f"Error: {usage.error_message}")

    lines.append("=" * 60)
    lines.append("")

    return "\n".join(lines)
