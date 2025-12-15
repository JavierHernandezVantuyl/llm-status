# TOS-Compliant Version - DOM-Only Scraping

## What Changed

Claude was blocking API calls with **403 errors** because they have rate limiting and TOS protection. The new version **completely removes all API calls** and only reads what's visible on the page.

## ✅ TOS-Compliant Approach

**What the extension does now:**
1. ✅ Reads visible text from the page (just like a human would see)
2. ✅ Finds "X% used" pattern in the text
3. ✅ Detects plan type from visible "Pro Plan" or "Free Plan" text
4. ✅ Extracts reset time from visible "Resets in X hr Y min" text
5. ✅ Uses MutationObserver to auto-detect when usage changes on the page

**What it does NOT do:**
- ❌ No API calls to `/api/organizations`
- ❌ No API calls to `/api/usage`
- ❌ No rate limit bypassing
- ❌ No hidden data access

**This is 100% TOS-compliant** - it's exactly the same as you opening the page and reading the numbers yourself!

## 🎯 New Features

### 1. Smart Page Load Detection
The scraper now **waits for the page to fully load** before trying to scrape:
- Checks every 500ms for "% used" text to appear
- Max 10 attempts (5 seconds total)
- Prevents "no data found" errors from scraping too early

### 2. Auto-Refresh with MutationObserver
The extension now **automatically detects** when Claude updates the usage percentage:
- Uses browser's MutationObserver API
- Watches for DOM changes containing "% used"
- Instantly updates when you send a new message and usage changes
- No manual refresh needed!

### 3. Multiple Percentage Detection
Since Claude shows multiple limits (Current session + Weekly):
- Finds ALL percentages on the page
- Uses the **maximum** (most restrictive) one
- Example: If "Current session: 96%" and "Weekly: 86%", uses **96%**

### 4. Better Logging
Easy to debug - you can see exactly what's happening:
```
[LLM Tracker] ━━━━━ REFRESH START ━━━━━
[LLM Tracker] ✓ Found percentages: [96, 86]
[LLM Tracker] → Using maximum: 96%
[LLM Tracker] ✓ Reset time: 3 hr 5 min
[LLM Tracker] ✓ Final data: {percentage: "96.0", status: "critical", ...}
[LLM Tracker] ━━━━━ REFRESH END ━━━━━
```

## 🧪 Testing Instructions

### 1. Reload the Extension
```
Chrome: chrome://extensions/ → Click ↻ on "LLM Usage Tracker"
```

### 2. Visit Claude Settings
```
https://claude.ai/settings/usage
```

### 3. Check Console (F12)
You should see:
```
[LLM Tracker] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[LLM Tracker] Claude content script loaded
[LLM Tracker] Version: DOM-only (TOS-compliant)
[LLM Tracker] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[LLM Tracker] ✓ Page loaded, usage data visible
[LLM Tracker] ✓ Found percentages: [96, 86]
[LLM Tracker] → Using maximum: 96%
[LLM Tracker] ✓ Data sent to background
[LLM Tracker] ✓ MutationObserver active
```

### 4. Check Extension Badge
Should show: **96%** with red/amber/green color

### 5. Click Extension Popup
Should show:
- **96% usage**
- **Status**: Critical/Warning/Good
- **Plan**: Pro Plan (detected from page text)
- **Reset**: in 3 hr 5 min

### 6. Test Auto-Refresh
1. Send a message to Claude (usage goes up)
2. The extension should **automatically detect** the change
3. Badge and popup update **without clicking refresh**!

## 🐛 Troubleshooting

### "No X% used pattern found"
- Make sure you're on `claude.ai/settings/usage`
- Wait for page to fully load (should see usage bars)
- Check console for "Page text sample" - does it contain your usage?

### Still showing old percentage
- Check if MutationObserver is active: look for "✓ MutationObserver active"
- Try manual refresh button
- Check console for "⚡ Usage changed detected"

### No data in popup
- Check console on claude.ai page (not background console)
- Look for "✓ Data sent to background"
- If you see errors, share them

## 📊 What You'll See

**Badge tooltip** (hover over icon):
```
CLAUDE: 96% usage • Resets in 3 hr 5 min
```

**Popup display:**
```
┌─────────────────────────────┐
│ Claude              Warning │
│                             │
│ 96% usage    ⚠️ High usage  │
│ ████████████████████░░░░░░  │
│                             │
│ Pro Plan    Resets in 3 hr  │
│                             │
│ [Refresh Claude]            │
└─────────────────────────────┘
```

**Console output:**
```
[LLM Tracker] ━━━━━ REFRESH START ━━━━━
[LLM Tracker] ✓ Found percentages: [96, 86]
[LLM Tracker] → Using maximum: 96%
[LLM Tracker] ✓ Reset time: 3 hr 5 min
[LLM Tracker] ✓ Final data: {percentage: "96.0", status: "warning", planType: "pro", resetTime: "3 hr 5 min"}
[LLM Tracker] ✓ Data sent to background
[LLM Tracker] ━━━━━ REFRESH END ━━━━━
```

## ✨ Benefits

1. **TOS-Compliant** - No API calls, just reads visible page
2. **No 403 Errors** - Doesn't trigger rate limits
3. **Faster** - No API roundtrips, instant scraping
4. **Auto-Updates** - MutationObserver detects changes automatically
5. **Simpler** - Less code, easier to maintain
6. **Future-Proof** - Works even if Claude changes their API

## 🎉 Ready to Test!

The extension is now **100% TOS-compliant** and should work perfectly without any 403 errors. It only reads what's visible on the page - nothing more, nothing less.

Test it out and let me know:
- Does the badge show your correct percentage?
- Does it auto-update when usage changes?
- Do you see clean console logs without API errors?
