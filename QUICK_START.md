# Quick Start Guide

## Installation

```bash
cd llm-status
pip3 install -e .
chmod +x llm-status
```

## All Commands (Quick Reference)

### 1. Setup (First Time)

```bash
./llm-status setup
```

**What it does:**
- Walks you through adding API keys for each provider
- Shows you where to get each key
- **Just press Enter to skip providers you don't use**
- Type 'q' to quit at any time

**Example:**
```
OpenAI
  Get your API key from: https://platform.openai.com/api-keys

  Enter API key (or Enter to skip, 'q' to quit): [paste key here or press Enter]
  ✓ API key saved for OpenAI

[continues for Anthropic, Gemini, DeepSeek...]
```

---

### 2. View Status (All Providers)

```bash
# Simple view (no cost)
./llm-status status

# With cost estimates
./llm-status status --show-cost

# Force refresh from API
./llm-status status --force-refresh
```

**Output:**
```
+-----------+-------------+---------------------+--------+
| Provider  | Tokens Used | Last Updated        | Status |
+-----------+-------------+---------------------+--------+
| OPENAI    | 197,000     | 2025-12-08 17:05:29 | OK     |
| ANTHROPIC | 123,000     | 2025-12-08 17:05:29 | OK     |
+-----------+-------------+---------------------+--------+
```

---

### 3. View Detailed Usage (One Provider)

```bash
# Simple view
./llm-status usage anthropic

# With cost estimate
./llm-status usage anthropic --show-cost

# Force refresh
./llm-status usage openai --force-refresh
```

**Output:**
```
Detailed Usage: ANTHROPIC
==================================================
Provider          : ANTHROPIC
Period            : month
Total Tokens      : 123,000
Prompt Tokens     : 89,000
Completion Tokens : 34,000
Tokens Remaining  : N/A
Last Updated      : 2025-12-08 17:05:29
Quota Available   : Yes
==================================================
```

---

### 4. Add/Update API Key

```bash
# Interactive (will prompt for key)
./llm-status add-cred openai

# Direct
./llm-status add-cred anthropic --api-key sk-ant-xxxxx
```

**Providers:** `openai`, `anthropic`, `gemini`, `deepseek`

---

### 5. Clear Cache

```bash
# Clear all providers
./llm-status clear-cache

# Clear specific provider
./llm-status clear-cache openai
```

**When to use:**
- After adding/updating an API key
- To force fresh data from providers

---

### 6. Manual Tracking (ChatGPT Web, etc.)

**Note:** Manual tracking is available but a browser extension is planned for Step 2.

```bash
# Track a prompt
./llm-status track chatgpt-web

# Track multiple
./llm-status track chatgpt-web --count 5

# View status
./llm-status track-status chatgpt-web

# View all tracked services
./llm-status track-status

# Set custom limit (e.g., for ChatGPT Plus)
./llm-status set-limit chatgpt-web 80 3

# Reset counter
./llm-status reset-tracker chatgpt-web
```

See `CHATGPT_TRACKING.md` for details.

---

## Common Workflows

### First Time Using

```bash
# 1. Run setup
./llm-status setup

# 2. View your usage
./llm-status status
```

### Daily Check

```bash
# Quick status check
./llm-status status

# Detailed view for one provider
./llm-status usage anthropic
```

### Adding a New Provider Later

```bash
# Option 1: Run setup again (skip others)
./llm-status setup

# Option 2: Add just one
./llm-status add-cred gemini
```

### Troubleshooting

```bash
# Not seeing updated data?
./llm-status clear-cache
./llm-status status --force-refresh

# Want to see costs?
./llm-status status --show-cost
```

---

## Tips

- **Skipping providers:** Just press Enter when prompted
- **No cost by default:** Add `--show-cost` if you want to see estimates
- **All commands work:** Both `./llm-status` and `python3 -m llm_status.cli`
- **Data location:** `~/.llm-status/` (config + cache)
- **Mock data:** Shows "MOCK" status until you add real API keys

---

## Getting Help

```bash
# General help
./llm-status --help

# Command-specific help
./llm-status status --help
./llm-status setup --help
./llm-status usage --help
```

---

## All Available Commands

| Command | Description |
|---------|-------------|
| `setup` | Interactive setup wizard |
| `status` | Show all providers |
| `usage <provider>` | Show details for one provider |
| `add-cred <provider>` | Add/update API key |
| `clear-cache [provider]` | Clear cached data |
| `track <provider>` | Manual tracking (web services) |
| `track-status [provider]` | View tracking status |
| `set-limit <provider> <limit> <hours>` | Set tracking limit |
| `reset-tracker <provider>` | Reset tracking counter |

All commands work! If you're having trouble, make sure you're using `./llm-status` or `python3 -m llm_status.cli`.
