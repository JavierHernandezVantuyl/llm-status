# Test the Updated Version

## What I Fixed

Based on your debug output, I discovered:

1. ✅ **Claude changed their UI** - They now show "90% used" instead of "X of Y messages"
2. ✅ **The API works!** - We can call `https://claude.ai/api/organizations` successfully
3. ✅ **You have Claude Pro** - Your account shows `["claude_pro", "chat"]` capabilities

## Updated Scraper Features

The new scraper now:
- ✅ Parses "90% used" format from the page
- ✅ Detects your plan type (Pro) from the API
- ✅ Tries multiple API endpoints to get actual message counts
- ✅ Falls back to estimated counts if API doesn't provide exact numbers
- ✅ Extracts reset time ("Resets in 3 hr 5 min")

## Test Steps

### 1. Reload the Extension
```
Chrome: chrome://extensions/ → Click ↻ on "LLM Usage Tracker"
```

### 2. Visit Claude Settings
```
https://claude.ai/settings/usage
```

### 3. Check the Console
Press F12 → Console, you should see:
```
[LLM Tracker] Claude content script loaded
[LLM Tracker] Checking Claude usage...
[LLM Tracker] ✓ Scraped percentage: {percentage: "90.0", status: "warning", ...}
[LLM Tracker] Found chat org: jh2402815@gmail.com's Organization ...
[LLM Tracker] Trying endpoint: https://claude.ai/api/organizations/.../usage
[LLM Tracker] Final combined data: {...}
[LLM Tracker] Sending usage data: {...}
```

### 4. Check the Extension Badge
Look at the extension icon in your toolbar - it should show "90%" with an amber/orange background (since you're at 90% = warning status).

### 5. Open the Popup
Click the extension icon. You should see:
- **Provider**: Claude
- **Status**: Warning (amber/yellow)
- **Usage**: Estimated based on 90% of Pro plan limit
- **Progress bar**: 90% filled, amber color
- **Reset time**: "Resets in 3 hr 5 min"

## What to Share

Once you test, let me know:

1. **Badge**: What does the badge show? (Should be "90%" with amber color)
2. **Popup**: Does the popup show your usage?
3. **Console**: Copy any errors if they appear
4. **API Endpoints**: Did any of the usage endpoints work? Look for:
   ```
   [LLM Tracker] ✓ Got data from https://claude.ai/api/organizations/.../usage
   ```

## Expected Behavior

Since Claude's API might not expose exact message counts, the extension will:
- Show the percentage (90%) ✅ Accurate
- Estimate message counts based on Pro plan limit (e.g., "900 of 1000") ⚠️ Estimated
- Show your plan type (Pro) ✅ Accurate
- Show reset time ✅ Accurate from page scraping

If the API endpoints work, we'll get exact counts. If not, estimates are still useful!

## Debugging

If it still doesn't work, check console for:
- Any errors in red
- What the "Final combined data" looks like
- Whether the API endpoints returned any data

Then share those logs with me!
