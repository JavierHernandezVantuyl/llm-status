# Claude Usage Tracker

**Branch:** `claude-usage-tracker`

A lightweight, terminal-based tool to track your Claude.ai/Claude Code chat usage over time.

## The Problem It Solves

Both Claude Code (CLI) and claude.ai (web chat) share the same usage quota, but there's no easy way to:
- Track usage over time
- See usage trends
- Get warnings before hitting limits
- Keep a history of your usage patterns

## How It Works

1. **You check your usage** - Run `/usage` in Claude Code or visit https://claude.ai/settings/usage
2. **You log it** - Record the numbers in this tool: `./claude_usage_tracker.py log 30 45`
3. **Track over time** - The tool stores your usage history and shows trends

**Zero API calls, zero token usage, 100% free and lightweight.**

## Quick Start

### 1. Check Your Current Usage

In Claude Code, run:
```
/usage
```

Or visit: https://claude.ai/settings/usage

You'll see something like:
```
Messages: 30/45 used
Resets in: 2 hours
```

### 2. Log It

```bash
./claude_usage_tracker.py log 30 45 --plan free
```

Output:
```
✓ Usage logged: 30/45 messages (66.7%)
```

If you're over 80%:
```
⚠️  WARNING: Over 80% used! 5 messages remaining.
```

### 3. Check Status Anytime

```bash
./claude_usage_tracker.py status
```

Output:
```
==================================================
  Claude Usage Status
==================================================
Last Updated    : 2025-12-08 19:41:13
Plan Type       : FREE
Messages Used   : 40/45 (88.9%)
Remaining       : 5 messages
Status          : ⚠️  WARNING - Running low
==================================================
```

## All Commands

### Log Current Usage

```bash
# Basic
./claude_usage_tracker.py log <used> <limit>

# With plan type
./claude_usage_tracker.py log 30 45 --plan free
./claude_usage_tracker.py log 80 100 --plan pro

# With notes
./claude_usage_tracker.py log 30 45 --notes "Before weekend usage"
```

### Check Status

```bash
./claude_usage_tracker.py status
```

Shows your most recent logged usage.

### View History

```bash
# Last 7 days (default)
./claude_usage_tracker.py history

# Last 30 days
./claude_usage_tracker.py history --days 30
```

Output:
```
======================================================================
  Usage History (Last 7 Days)
======================================================================
Date & Time          Used       Limit      %        Plan
----------------------------------------------------------------------
2025-12-08 19:41:13  40         45           88.9% free
2025-12-08 18:20:05  35         45           77.8% free
2025-12-07 15:30:22  28         45           62.2% free
======================================================================
```

### Analyze Trends

```bash
./claude_usage_tracker.py trend
```

Output:
```
==================================================
  Usage Trend Analysis
==================================================
Current Usage   : 40/45 (88.9%)
Trend           : INCREASING
Days Tracked    : 7
Avg Daily Max   : 35.5 messages

💡 Tip: Your usage is increasing. Consider upgrading to Pro if needed.
==================================================
```

## Typical Workflow

### Daily Check (30 seconds)

```bash
# 1. Check current usage in Claude Code
/usage

# 2. Log it (assuming you see 25/45)
./claude_usage_tracker.py log 25 45 --plan free

# 3. Check status
./claude_usage_tracker.py status
```

### Weekly Review (1 minute)

```bash
# View your week
./claude_usage_tracker.py history

# See trend
./claude_usage_tracker.py trend
```

## Understanding Status Indicators

| Percentage | Status | Meaning |
|------------|--------|---------|
| 0-75% | ✓ OK | Plenty of messages remaining |
| 76-90% | ⚠️ WARNING | Running low, use carefully |
| 91-100% | 🔴 CRITICAL | Very few messages left |

## Plan Types

### Free Plan
- **Limit**: ~45 messages per 5 hours
- **Log command**: `--plan free`

### Pro Plan
- **Limit**: Higher (varies, check your settings)
- **Log command**: `--plan pro`

## Data Storage

All data stored locally in:
```
~/.llm-status/claude_usage.db
```

**Lightweight SQLite database** - typically < 100KB even with months of data.

## Why This Approach?

### ✅ Pros
- **Zero token usage** - No API calls means no costs
- **Lightweight** - Single Python file, SQLite storage
- **Privacy** - All data stored locally
- **Fast** - Instant results, no network delays
- **Simple** - Just log your usage when you check it

### ⚠️ Requires
- **Manual logging** - You need to check and log usage yourself
- **Consistency** - Works best if you log regularly

## Future Enhancements (Optional)

If you want automation later, we can add:
1. **Browser extension** to auto-capture claude.ai usage
2. **Claude Code hook** to auto-log after each conversation
3. **Alerts** via desktop notifications

But for now, this manual approach:
- Costs nothing (no tokens/API calls)
- Works immediately
- Gives you full control

## Tips for Best Results

1. **Log regularly** - Once a day or after heavy usage sessions
2. **Check before big projects** - Know your limits before starting work
3. **Review trends weekly** - Understand your usage patterns
4. **Use notes** - Track what caused high usage (e.g., "Refactoring session")

## Example Usage Session

```bash
# Monday morning - start fresh
./claude_usage_tracker.py log 2 45 --plan free --notes "Start of week"

# Wednesday afternoon - heavy coding
./claude_usage_tracker.py log 28 45 --plan free --notes "Backend refactor"
# ✓ Usage logged: 28/45 messages (62.2%)

# Friday evening - check status
./claude_usage_tracker.py status
# Messages Used   : 28/45 (62.2%)
# Status          : ✓ OK

# Weekend - review week
./claude_usage_tracker.py history
./claude_usage_tracker.py trend
```

## Troubleshooting

**Q: Where is my data stored?**
A: `~/.llm-status/claude_usage.db`

**Q: Can I delete old data?**
A: Yes, just delete the database file. Or manually with SQL.

**Q: Does this work for Claude API usage?**
A: No, this is specifically for chat usage (claude.ai/Claude Code). The API has separate quotas.

**Q: What if I forget to log for a few days?**
A: No problem! The tool shows trends based on whatever data you have. Just start logging again.

## Integration Ideas

### Shell Alias

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
alias claude-log='~/path/to/claude_usage_tracker.py log'
alias claude-status='~/path/to/claude_usage_tracker.py status'
```

Then just:
```bash
claude-log 30 45 --plan free
claude-status
```

### Claude Code Hook (Future)

We could create a hook that automatically logs usage after conversations.

---

## Summary

This tool gives you:
- 📊 **Usage tracking** over time
- 📈 **Trend analysis** to understand patterns
- ⚠️ **Warnings** before hitting limits
- 📝 **History** to review past usage
- 💰 **Zero cost** - no API calls, no tokens

All in a **lightweight, terminal-first tool** that respects your privacy and doesn't waste any resources.

Start tracking now:
```bash
./claude_usage_tracker.py log <your-usage> <your-limit> --plan <free-or-pro>
```
