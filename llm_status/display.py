"""Display and formatting utilities for llm-status."""
from typing import List, Dict, Any, Optional
from .providers.base import UsageData


def format_number(num: Optional[int]) -> str:
    """Format large numbers with comma separators."""
    if num is None:
        return "N/A"
    return f"{num:,}"


def format_cost(cost: Optional[float]) -> str:
    """Format cost in USD."""
    if cost is None:
        return "N/A"
    return f"${cost:.2f}"


def format_timestamp(timestamp) -> str:
    """Format timestamp for display."""
    if timestamp is None:
        return "N/A"
    if hasattr(timestamp, 'strftime'):
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")
    return str(timestamp)


def draw_table(headers: List[str], rows: List[List[str]], title: Optional[str] = None) -> str:
    """Draw an ASCII table.

    Args:
        headers: Column headers
        rows: Table rows
        title: Optional table title

    Returns:
        Formatted ASCII table as string
    """
    if not rows:
        return "No data available."

    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    # Build separator line
    separator = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"

    # Build header
    header_row = "|" + "|".join(f" {headers[i]:<{col_widths[i]}} " for i in range(len(headers))) + "|"

    # Build rows
    data_rows = []
    for row in rows:
        data_row = "|" + "|".join(f" {str(row[i]):<{col_widths[i]}} " for i in range(len(row))) + "|"
        data_rows.append(data_row)

    # Assemble table
    lines = []
    if title:
        lines.append(f"\n{title}")
        lines.append("=" * len(title))
    lines.append(separator)
    lines.append(header_row)
    lines.append(separator)
    lines.extend(data_rows)
    lines.append(separator)

    return "\n".join(lines)


def format_status_table(usage_data_list: List[UsageData], show_cost: bool = False) -> str:
    """Format status data for all providers as a table.

    Args:
        usage_data_list: List of UsageData objects
        show_cost: Whether to include cost column (default: False)

    Returns:
        Formatted ASCII table
    """
    if show_cost:
        headers = ["Provider", "Tokens Used", "Cost (USD)", "Last Updated", "Status"]
    else:
        headers = ["Provider", "Tokens Used", "Last Updated", "Status"]

    rows = []

    for data in usage_data_list:
        status = "OK" if data.quota_available and not data.error_message else "ERROR"
        if data.error_message and "[STUB]" in data.error_message:
            status = "MOCK"

        if show_cost:
            rows.append([
                data.provider.upper(),
                format_number(data.tokens_used),
                format_cost(data.cost_usd),
                format_timestamp(data.last_updated),
                status
            ])
        else:
            rows.append([
                data.provider.upper(),
                format_number(data.tokens_used),
                format_timestamp(data.last_updated),
                status
            ])

    return draw_table(headers, rows, title="LLM Usage Status")


def format_detailed_usage(usage_data: UsageData, show_cost: bool = False) -> str:
    """Format detailed usage for a single provider.

    Args:
        usage_data: UsageData object
        show_cost: Whether to show cost estimate

    Returns:
        Formatted output string
    """
    lines = [
        f"\nDetailed Usage: {usage_data.provider.upper()}",
        "=" * 50,
    ]

    # Build key-value pairs (core usage info)
    details = [
        ("Provider", usage_data.provider.upper()),
        ("Period", usage_data.period),
        ("Total Tokens", format_number(usage_data.tokens_used)),
        ("Prompt Tokens", format_number(usage_data.prompt_tokens)),
        ("Completion Tokens", format_number(usage_data.completion_tokens)),
        ("Tokens Remaining", format_number(usage_data.tokens_remaining)),
        ("Last Updated", format_timestamp(usage_data.last_updated)),
        ("Quota Available", "Yes" if usage_data.quota_available else "No"),
    ]

    # Add cost if requested and available
    if show_cost and usage_data.cost_usd is not None:
        details.insert(-2, ("Estimated Cost", format_cost(usage_data.cost_usd)))

    # Calculate max key length for alignment
    max_key_len = max(len(key) for key, _ in details)

    for key, value in details:
        lines.append(f"{key:<{max_key_len}} : {value}")

    if usage_data.error_message:
        lines.append("")
        lines.append(f"Note: {usage_data.error_message}")

    lines.append("=" * 50)
    return "\n".join(lines)


def format_error(message: str) -> str:
    """Format an error message.

    Args:
        message: Error message

    Returns:
        Formatted error string
    """
    return f"\nERROR: {message}\n"


def format_success(message: str) -> str:
    """Format a success message.

    Args:
        message: Success message

    Returns:
        Formatted success string
    """
    return f"\nSUCCESS: {message}\n"
