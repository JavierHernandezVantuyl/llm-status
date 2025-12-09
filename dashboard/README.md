# LLM Chat Usage Dashboard

**Branch:** `claude-usage-tracker`

A lightweight web dashboard to track your **CHAT usage** across LLMs (NOT API usage).

## What This Tracks

✅ **CHAT Usage** - Conversation limits (claude.ai, Claude Code, chatgpt.com)
❌ **NOT API Usage** - Developer API calls (Anthropic API, OpenAI API)

For Claude, this is the same quota shown by:
- `/usage` command in Claude Code
- https://claude.ai/settings/usage

## Quick Start

### 1. Start the Dashboard

```bash
cd dashboard
python3 server.py
```

You'll see:
```
============================================================
  🤖 LLM Chat Usage Dashboard
============================================================

✅ Dashboard running at: http://localhost:8000

📋 Instructions:
   1. Make sure you're logged into claude.ai in your browser
   2. Open http://localhost:8000 in your browser
   3. Click 'Refresh Usage' to fetch your Claude chat usage
```

### 2. Open in Browser

Go to: **http://localhost:8000**

### 3. Refresh Claude Usage

Click "🔄 Refresh Usage" on the Claude card.

It will automatically fetch your current chat usage!

## How It Works

1. **You log into claude.ai** in your browser (like normal)
2. **Dashboard uses your session** to fetch usage data
3. **Displays it cleanly** with warnings when running low
4. **Auto-refreshes** every 5 minutes

## Features

### ✅ Automatic Fetching
- No manual logging/pasting needed
- Uses your existing browser session
- One click to refresh

### ✅ Lightweight
- Pure Python stdlib + HTML/JS
- No heavy frameworks
- Runs on weak machines
- ~100KB total

### ✅ Real-Time Status
- See usage percentage
- Visual progress bars
- Color-coded warnings (OK/Warning/Critical)
- Shows reset time

### ✅ Privacy
- Runs locally (localhost:8000)
- No external servers
- Data stays in your browser
- Uses claude.ai session you already have

### ✅ Extensible
- Built to add ChatGPT, Gemini, etc.
- Modular API design
- Easy to customize

## Dashboard Screenshot

```
🤖 LLM Chat Usage Dashboard
Track your conversation limits across all LLMs

┌─────────────────────────────────────┐
│ Claude                   ✓ OK       │
│                                     │
│ ████████████████░░░░░░  75.6%      │
│ 34 / 45 messages     11 remaining  │
│ Resets in 2 hours 15 minutes       │
│ Plan: FREE                         │
│                                     │
│ [🔄 Refresh Usage]                 │
│ View on Claude →                   │
└─────────────────────────────────────┘

Last updated: 2025-12-08 19:45:30
```

## Adding More LLMs

To add ChatGPT, Gemini, etc:

1. **Add to HTML** - Add provider config in `index.html`:
```javascript
{
    id: 'chatgpt',
    name: 'ChatGPT',
    type: 'chat',
    fetchUrl: '/api/chatgpt-usage',
    settingsUrl: 'https://chatgpt.com/settings'
}
```

2. **Add API endpoint** in `server.py`:
```python
elif path == '/api/chatgpt-usage':
    self.fetch_chatgpt_usage()
```

3. **Implement fetcher** - Fetch from chatgpt.com using session

Done! New LLM appears in dashboard.

## Deployment Options

### Option 1: Local (Current)
Run on your machine at `localhost:8000`

**Pros:**
- Private, secure
- No deployment needed
- Works immediately

**Cons:**
- Only accessible from your computer
- Server must be running

### Option 2: Cloud (Future)
Deploy to Vercel/Netlify/etc.

**Pros:**
- Access from anywhere
- Always running
- Share with team

**Cons:**
- Need to handle auth securely
- Slightly more complex

**For now, local is perfect!**

## Troubleshooting

**Q: "Not logged in" error?**
A: Log into claude.ai in the same browser, then refresh

**Q: "Session expired" error?**
A: Log out and back into claude.ai

**Q: Can't access localhost:8000?**
A: Make sure server.py is running

**Q: Want to use different port?**
A: Edit `PORT = 8000` in server.py

## Files

```
dashboard/
├── server.py      # Python server (lightweight)
├── index.html     # Dashboard UI
└── README.md      # This file
```

**Total size:** ~30KB

## Next Steps

### Phase 1 (Current): Claude ✓
- Automatic Claude chat usage fetching
- Clean web dashboard
- Lightweight local server

### Phase 2 (Next): More LLMs
- ChatGPT web usage
- Gemini usage
- OpenAI API usage (separate)
- Anthropic API usage (separate)

### Phase 3 (Later): Enhancements
- Historical tracking
- Usage trends/charts
- Desktop notifications
- Browser extension for auto-refresh

## Why This Approach?

### vs. Manual Tracking
❌ Manual: Run `/usage`, copy numbers, log somewhere
✅ Dashboard: Click refresh, see usage instantly

### vs. API Scraping
❌ API: Different quotas, complex auth
✅ Dashboard: Uses your existing session, shows CHAT usage

### vs. Heavy Frameworks
❌ Heavy: React, Node.js, database, complex setup
✅ Dashboard: Pure Python + HTML, runs immediately

## Summary

You get:
- ✅ **Automatic** Claude chat usage tracking
- ✅ **Web dashboard** at localhost:8000
- ✅ **Lightweight** (30KB, Python stdlib)
- ✅ **Privacy** (runs locally)
- ✅ **Extensible** (easy to add LLMs)
- ✅ **Chat vs API** clarity (tracks CHAT usage)

**Start now:**
```bash
cd dashboard
python3 server.py
```

Then open: http://localhost:8000
