# LLM Usage Dashboard

**Branch:** `claude-usage-tracker`

A lightweight, modular dashboard to see usage across ALL your LLM providers in one place.

## What You Get

```
================================================================================
  LLM Usage Dashboard
================================================================================
Provider  Used  Limit  Remaining      %  Status
--------------------------------------------------------------------------------
CLAUDE      25     45         20   55.6%  ✓ OK
OPENAI     N/A    N/A        N/A    N/A%  ? UNKNOWN
GEMINI     N/A    N/A        N/A    N/A%  ? UNKNOWN
================================================================================
```

**One command to see everything.**

## Quick Start

### 1. Check Claude Usage

In Claude Code, run:
```
/usage
```

You'll see something like:
```
You have used 25 of your 45 messages in the current 5-hour window.
The window resets in 2 hours and 15 minutes.
```

### 2. Run the Dashboard

```bash
./llm-dashboard claude
```

It will prompt you to paste the `/usage` output:
```
============================================================
  Claude Usage - Quick Check
============================================================

📋 In Claude Code, run: /usage
   Or visit: https://claude.ai/settings/usage

Then paste the output here (or press Enter to skip):
------------------------------------------------------------
```

Paste the output and press Enter twice.

### 3. See Your Usage

```
============================================================
  CLAUDE Usage
============================================================
Last Updated    : 2025-12-08 19:45:30
Plan Type       : FREE
Messages Used   : 25/45 (55.6%)
Remaining       : 20 messages
Resets In       : 2 hours and 15 minutes
Status          : ✓ OK - Plenty remaining
============================================================
```

## All Commands

```bash
# Check all LLMs
./llm-dashboard

# Check specific LLM
./llm-dashboard claude

# List available LLMs
./llm-dashboard --list

# Get help
./llm-dashboard --help
```

## Current Status

### ✅ Supported
- **Claude** - Parses `/usage` output or claude.ai/settings/usage

### 🚧 Coming Soon
- **OpenAI** - Scrape platform.openai.com/usage
- **ChatGPT Web** - Browser extension or scraper
- **Gemini** - Scrape aistudio.google.com
- **DeepSeek** - API or scraper

## Architecture

The dashboard is **modular** - adding new LLMs is easy:

```
llm-dashboard/
├── fetchers/
│   ├── base.py           # Base fetcher interface
│   ├── claude.py         # Claude fetcher ✓
│   ├── openai.py         # OpenAI fetcher (coming)
│   └── ...
├── display.py            # Terminal display
└── llm-dashboard         # Main command
```

### How to Add a New LLM

1. **Create a fetcher** in `llm_dashboard/fetchers/your_llm.py`:

```python
from .base import BaseFetcher, LLMUsage
from datetime import datetime

class YourLLMFetcher(BaseFetcher):
    @property
    def provider_name(self) -> str:
        return "your_llm"

    def fetch_usage(self) -> LLMUsage:
        # Fetch usage from API or scrape web page
        # Return LLMUsage object
        return LLMUsage(
            provider="your_llm",
            messages_used=30,
            messages_limit=100,
            messages_remaining=70,
            reset_time="3 hours",
            plan_type="free",
            last_updated=datetime.now(),
            status="ok"
        )
```

2. **Register it** in `llm_dashboard/fetchers/__init__.py`:

```python
from .your_llm import YourLLMFetcher

FETCHERS = {
    "claude": ClaudeFetcher,
    "your_llm": YourLLMFetcher,  # Add this line
}
```

3. **Done!** Now `./llm-dashboard your_llm` works.

## Design Principles

### ✅ Lightweight
- Pure Python stdlib (no heavy dependencies)
- Terminal-first (can add web UI later)
- Fast execution

### ✅ Zero Cost
- No additional API calls
- Scrapes existing dashboards or parses command output
- No token usage

### ✅ Modular
- Each LLM is a separate fetcher
- Easy to add new providers
- Clean separation of concerns

### ✅ Flexible Deployment
- **Terminal**: What you have now
- **Web**: Could add a simple Flask/FastAPI server later
- **Cloud**: Could deploy to serverless function
- **Local**: Runs entirely on your machine

All options stay lightweight!

## Future Enhancements

### Phase 1: More LLMs (Next)
- OpenAI usage fetcher
- ChatGPT web scraper
- Gemini fetcher
- DeepSeek fetcher

### Phase 2: Better Automation
- Browser extension to auto-capture web usage
- Claude Code hook to auto-refresh
- Scheduled auto-refresh in background

### Phase 3: Optional Web UI
- Simple dashboard at `localhost:8000`
- Real-time updates
- Historical charts
- Still lightweight!

### Phase 4: Smarts
- Usage predictions ("You'll hit limit in 2 hours")
- Cost tracking
- Alerts/notifications

## Deployment Options

### Option 1: Terminal (Current)
**Pros:** Instant, lightweight, no setup
**Cons:** Manual refresh

```bash
./llm-dashboard
```

### Option 2: Simple Web UI (Future)
**Pros:** Auto-refresh, charts, share with team
**Cons:** Needs server running

```bash
./llm-dashboard --serve --port 8000
# Opens at http://localhost:8000
```

### Option 3: Cloud Dashboard (Future)
**Pros:** Access anywhere, always on
**Cons:** Need to deploy somewhere

```bash
# Deploy to Vercel/Netlify/etc
# Still lightweight - just a few KB
```

**Your choice!** Start with terminal, upgrade later if needed.

## Why This Design?

### vs. Manual Logging
❌ Manual: You run `/usage`, then log it manually
✅ This: You run `/usage`, paste once, get formatted output

### vs. Heavy Dashboards
❌ Heavy: Node.js server, React frontend, database
✅ This: Single Python script, terminal output

### vs. API-Only Solutions
❌ API-only: Wast tokens, costs money, APIs don't exist
✅ This: Parse existing dashboards, zero cost

## Examples

### Example 1: Daily Check

```bash
# Morning check
./llm-dashboard

# See all LLMs at once
# Takes 10 seconds total
```

### Example 2: Before Big Project

```bash
# Check Claude before starting
./llm-dashboard claude

# See: "20 messages remaining"
# Decide: Continue or wait for reset
```

### Example 3: Multi-LLM Project

```bash
# Working across multiple LLMs
./llm-dashboard

# See which has most quota left
# Use that one for heavy work
```

## Tips

1. **Bookmark dashboards** - Keep browser tabs open for quick copy-paste
2. **Run before heavy use** - Check limits before starting big tasks
3. **Add shell aliases** - Make it even faster:

```bash
alias llms='./llm-dashboard'
alias claude-usage='./llm-dashboard claude'
```

Then just:
```bash
llms              # Check all
claude-usage      # Check Claude
```

## Data Storage

Currently: **No storage** - Just parses and displays
Future: Can add optional SQLite storage for history/trends

## Privacy

- All data stays local (no external servers)
- Only fetches from official LLM dashboards you already access
- No tracking, no analytics

## Troubleshooting

**Q: Can't parse /usage output?**
A: Make sure you paste the exact output. File an issue with the format you're seeing.

**Q: Want auto-fetch without pasting?**
A: Coming soon! Browser extension or local scraper.

**Q: How to add my own LLM?**
A: See "How to Add a New LLM" section above.

## Summary

You get:
- ✅ **Cross-platform view** of ALL your LLMs
- ✅ **Lightweight** terminal dashboard
- ✅ **Zero cost** (no API calls)
- ✅ **Modular** (easy to add LLMs)
- ✅ **Flexible** (terminal now, web later)

All in **~500 lines of Python** with **zero dependencies**.

Start using it:
```bash
./llm-dashboard claude
```

Then add more LLMs as you need them!
