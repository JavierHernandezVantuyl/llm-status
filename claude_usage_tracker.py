#!/usr/bin/env python3
"""
Claude Usage Tracker - Track your Claude.ai/Claude Code usage over time

Lightweight tool to monitor your Claude chat usage without additional API calls.
Works with both Claude Code and claude.ai (they share the same quota).

Usage:
    ./claude_usage_tracker.py log <used> <limit>    # Log current usage
    ./claude_usage_tracker.py status                # Show current status
    ./claude_usage_tracker.py history               # Show usage history
    ./claude_usage_tracker.py trend                 # Show usage trend
"""

import sqlite3
import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple, Optional


class ClaudeUsageTracker:
    """Track Claude usage over time."""

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize tracker.

        Args:
            db_path: Path to SQLite database (defaults to ~/.llm-status/claude_usage.db)
        """
        if db_path is None:
            config_dir = Path.home() / ".llm-status"
            config_dir.mkdir(parents=True, exist_ok=True)
            db_path = config_dir / "claude_usage.db"

        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usage_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                messages_used INTEGER NOT NULL,
                messages_limit INTEGER NOT NULL,
                messages_remaining INTEGER NOT NULL,
                percentage_used REAL NOT NULL,
                plan_type TEXT DEFAULT 'unknown',
                notes TEXT
            )
        """)

        conn.commit()
        conn.close()

    def log_usage(self, used: int, limit: int, plan_type: str = "unknown", notes: str = "") -> None:
        """Log current usage snapshot.

        Args:
            used: Number of messages used
            limit: Message limit for current period
            plan_type: Plan type (free, pro, etc.)
            notes: Optional notes
        """
        remaining = limit - used
        percentage = (used / limit * 100) if limit > 0 else 0

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO usage_log (
                timestamp, messages_used, messages_limit,
                messages_remaining, percentage_used, plan_type, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            used, limit, remaining, percentage, plan_type, notes
        ))

        conn.commit()
        conn.close()

        print(f"\n✓ Usage logged: {used}/{limit} messages ({percentage:.1f}%)")
        if percentage > 80:
            print(f"⚠️  WARNING: Over 80% used! {remaining} messages remaining.")

    def get_current_status(self) -> Optional[Tuple]:
        """Get most recent usage entry.

        Returns:
            Tuple of (timestamp, used, limit, remaining, percentage, plan_type, notes) or None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT timestamp, messages_used, messages_limit,
                   messages_remaining, percentage_used, plan_type, notes
            FROM usage_log
            ORDER BY timestamp DESC
            LIMIT 1
        """)

        result = cursor.fetchone()
        conn.close()

        return result

    def get_history(self, days: int = 7) -> List[Tuple]:
        """Get usage history for the last N days.

        Args:
            days: Number of days to retrieve

        Returns:
            List of usage tuples
        """
        since = (datetime.now() - timedelta(days=days)).isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT timestamp, messages_used, messages_limit,
                   messages_remaining, percentage_used, plan_type
            FROM usage_log
            WHERE timestamp >= ?
            ORDER BY timestamp DESC
        """, (since,))

        results = cursor.fetchall()
        conn.close()

        return results

    def get_trend(self) -> dict:
        """Analyze usage trend.

        Returns:
            Dict with trend analysis
        """
        history = self.get_history(days=7)

        if not history:
            return {"error": "No usage data yet"}

        # Calculate average daily usage
        daily_usage = {}
        for entry in history:
            timestamp, used, limit, remaining, percentage, plan_type = entry
            date = timestamp.split('T')[0]
            if date not in daily_usage:
                daily_usage[date] = []
            daily_usage[date].append(used)

        # Get max usage per day
        daily_max = {date: max(usages) for date, usages in daily_usage.items()}

        # Calculate trend
        if len(daily_max) >= 2:
            sorted_days = sorted(daily_max.items())
            recent_avg = sum(u for _, u in sorted_days[-3:]) / min(3, len(sorted_days))
            older_avg = sum(u for _, u in sorted_days[-7:-3]) / max(1, len(sorted_days) - 3)

            if recent_avg > older_avg * 1.2:
                trend = "increasing"
            elif recent_avg < older_avg * 0.8:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "insufficient data"

        current = history[0]
        _, used, limit, remaining, percentage, plan_type = current

        return {
            "current_used": used,
            "current_limit": limit,
            "current_percentage": percentage,
            "trend": trend,
            "days_tracked": len(daily_max),
            "avg_daily_max": sum(daily_max.values()) / len(daily_max) if daily_max else 0
        }


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Claude Usage Tracker - Monitor your Claude chat usage",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Log current usage (30 messages used out of 45 limit)
  %(prog)s log 30 45

  # Log with plan type
  %(prog)s log 30 45 --plan free

  # Show current status
  %(prog)s status

  # View 7-day history
  %(prog)s history

  # Show usage trend
  %(prog)s trend

Tip: Run /usage in Claude Code or check https://claude.ai/settings/usage
     then log your current usage here to track over time.
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Log command
    log_parser = subparsers.add_parser('log', help='Log current usage')
    log_parser.add_argument('used', type=int, help='Messages used')
    log_parser.add_argument('limit', type=int, help='Message limit')
    log_parser.add_argument('--plan', default='unknown', help='Plan type (free/pro)')
    log_parser.add_argument('--notes', default='', help='Optional notes')

    # Status command
    subparsers.add_parser('status', help='Show current status')

    # History command
    history_parser = subparsers.add_parser('history', help='Show usage history')
    history_parser.add_argument('--days', type=int, default=7, help='Days to show (default: 7)')

    # Trend command
    subparsers.add_parser('trend', help='Show usage trend analysis')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    tracker = ClaudeUsageTracker()

    if args.command == 'log':
        tracker.log_usage(args.used, args.limit, args.plan, args.notes)

    elif args.command == 'status':
        status = tracker.get_current_status()
        if not status:
            print("\nNo usage data yet. Run 'log' command first.")
            print("Example: ./claude_usage_tracker.py log 30 45")
            return 1

        timestamp, used, limit, remaining, percentage, plan_type, notes = status

        print("\n" + "=" * 50)
        print("  Claude Usage Status")
        print("=" * 50)
        print(f"Last Updated    : {timestamp[:19].replace('T', ' ')}")
        print(f"Plan Type       : {plan_type.upper()}")
        print(f"Messages Used   : {used}/{limit} ({percentage:.1f}%)")
        print(f"Remaining       : {remaining} messages")

        if percentage > 90:
            print(f"Status          : 🔴 CRITICAL - Very low remaining!")
        elif percentage > 75:
            print(f"Status          : ⚠️  WARNING - Running low")
        else:
            print(f"Status          : ✓ OK")

        if notes:
            print(f"Notes           : {notes}")
        print("=" * 50)

    elif args.command == 'history':
        history = tracker.get_history(days=args.days)
        if not history:
            print(f"\nNo usage data in the last {args.days} days.")
            return 1

        print(f"\n" + "=" * 70)
        print(f"  Usage History (Last {args.days} Days)")
        print("=" * 70)
        print(f"{'Date & Time':<20} {'Used':<10} {'Limit':<10} {'%':<8} {'Plan':<10}")
        print("-" * 70)

        for entry in history:
            timestamp, used, limit, remaining, percentage, plan_type = entry
            dt = timestamp[:19].replace('T', ' ')
            print(f"{dt:<20} {used:<10} {limit:<10} {percentage:>6.1f}% {plan_type:<10}")

        print("=" * 70)

    elif args.command == 'trend':
        trend_data = tracker.get_trend()

        if "error" in trend_data:
            print(f"\n{trend_data['error']}")
            return 1

        print("\n" + "=" * 50)
        print("  Usage Trend Analysis")
        print("=" * 50)
        print(f"Current Usage   : {trend_data['current_used']}/{trend_data['current_limit']} "
              f"({trend_data['current_percentage']:.1f}%)")
        print(f"Trend           : {trend_data['trend'].upper()}")
        print(f"Days Tracked    : {trend_data['days_tracked']}")
        print(f"Avg Daily Max   : {trend_data['avg_daily_max']:.1f} messages")

        if trend_data['trend'] == 'increasing':
            print("\n💡 Tip: Your usage is increasing. Consider upgrading to Pro if needed.")
        elif trend_data['trend'] == 'stable':
            print("\n✓ Your usage is stable.")

        print("=" * 50)

    return 0


if __name__ == "__main__":
    sys.exit(main())
