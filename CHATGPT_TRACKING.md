# ChatGPT Web Usage Tracking Guide

Since ChatGPT web version doesn't have an API to check your usage, `llm-status` provides **manual tracking** to help you avoid running out of prompts.

## How It Works

ChatGPT Free tier limits:
- **~40 messages per 3 hours** for GPT-4o
- Resets every 3 hours after your first message
- No official API to check remaining prompts

`llm-status` tracks this locally by counting when you tell it you've sent a prompt.

## Quick Start

### 1. Track Each Prompt You Send

Every time you send a prompt to ChatGPT, run:

```bash
./llm-status track chatgpt-web
```

Or use the shorthand with your shell:

```bash
# Add to your shell profile (~/.bashrc or ~/.zshrc)
alias gpt-track='./llm-status track chatgpt-web'

# Then just run:
gpt-track
```

### 2. Check Your Status

```bash
./llm-status track-status chatgpt-web
```

**Example output:**
```
CHATGPT-WEB
  Used:       36/40 prompts (90.0%)
  Remaining:  4 prompts
  Period:     3 hours
  Next Reset: 2025-12-08 19:43:46
  Status:     ⚠ WARNING - Low remaining!
```

### 3. Get Warnings

When you have less than 20% remaining (8 prompts out of 40), you'll see:

```
⚠ WARNING: Less than 20% remaining!
```

This gives you a heads-up before you run out completely.

## Advanced Usage

### Track Multiple Prompts at Once

If you forgot to track and sent 5 prompts:

```bash
./llm-status track chatgpt-web --count 5
```

### Adjust Limits

If you have ChatGPT Plus or the limits change:

```bash
# Example: ChatGPT Plus with 80 messages per 3 hours
./llm-status set-limit chatgpt-web 80 3
```

### Reset Counter

If the timer resets or you want to start fresh:

```bash
./llm-status reset-tracker chatgpt-web
```

### View All Tracked Services

```bash
./llm-status track-status
```

Shows all manually tracked services (ChatGPT, Claude web, etc.)

## Tips for Accurate Tracking

1. **Track immediately after sending** - Don't forget!
2. **Create a habit** - Track every prompt, even simple ones
3. **Use aliases** - Make it quick: `gpt-track` instead of the full command
4. **Check before long sessions** - Run `track-status` before starting work

## Setting Up Automatic Tracking (Advanced)

You can create a wrapper script that tracks automatically:

```bash
#!/bin/bash
# Save as ~/bin/gpt
# Usage: gpt "your prompt here"

echo "$1" | pbcopy  # Copy to clipboard (macOS)
open "https://chatgpt.com"  # Open ChatGPT
./llm-status track chatgpt-web  # Track the prompt
./llm-status track-status chatgpt-web  # Show status
```

Make it executable:
```bash
chmod +x ~/bin/gpt
```

Now use:
```bash
gpt "Write a Python function to reverse a string"
```

## Other Services

You can track other web-based LLM services too:

### Claude Web (claude.ai)

```bash
./llm-status track claude-web
./llm-status track-status claude-web
```

Default limits:
- 45 messages per 5 hours (free tier)
- Adjust with `set-limit` if needed

### Custom Services

Track any service:

```bash
# Set up a new tracker
./llm-status set-limit my-service 100 24

# Track usage
./llm-status track my-service

# Check status
./llm-status track-status my-service
```

## Troubleshooting

**Q: I exceeded the limit but still have prompts left**
- Reset the tracker: `./llm-status reset-tracker chatgpt-web`
- Limits may have changed - adjust with `set-limit`

**Q: The timer shows wrong reset time**
- The reset is based on your first tracked prompt in the period
- Reset manually when ChatGPT resets: `./llm-status reset-tracker chatgpt-web`

**Q: Can this automatically track my ChatGPT usage?**
- No, ChatGPT web doesn't provide an API
- You must manually track each prompt
- This is the best alternative without browser extensions

## Data Storage

All tracking data is stored locally in:
```
~/.llm-status/manual_usage.json
```

Your data never leaves your computer.
