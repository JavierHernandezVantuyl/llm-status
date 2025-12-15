# 🐛 Debug Mode - Let's Find Out What's Wrong!

I've created a debug version that will tell us exactly what's on your Claude page.

## Quick Debug Steps

### 1. Reload the Extension with Debug Mode

The extension is now in DEBUG mode. If you already loaded it:

**Chrome/Edge:**
1. Go to `chrome://extensions/`
2. Find "LLM Usage Tracker"
3. Click the refresh icon (↻) to reload it
4. OR click "Remove" and re-load it with "Load unpacked"

**Firefox:**
1. Go to `about:debugging#/runtime/this-firefox`
2. Click "Reload" next to the extension
3. OR remove and re-load it

### 2. Visit Claude and Check Console

1. Go to https://claude.ai/settings/usage (make sure you're logged in)
2. Press **F12** to open Developer Tools
3. Go to the **Console** tab
4. Look for messages starting with `[LLM Tracker DEBUG]`
5. You should see a LOT of debug output

### 3. Copy the Debug Output

At the end of the console output, you'll see:

```
[LLM Tracker DEBUG] ========================================
[LLM Tracker DEBUG] COPY THE RESULTS BELOW:
[LLM Tracker DEBUG] ========================================
{
  ... lots of JSON data ...
}
[LLM Tracker DEBUG] ========================================
```

**Copy everything between the === lines and share it with me!**

## Alternative: Run Manual Debug Script

If the extension isn't loading, you can also:

1. Visit https://claude.ai/settings/usage
2. Press F12 → Console
3. Open `DEBUG_CLAUDE.md`
4. Copy and paste that entire JavaScript code into the console
5. Press Enter
6. Share the output

## What I'm Looking For

The debug script will try to find your usage data using:

1. ✅ **Text patterns** - "25 of 45 messages", "25/45", etc.
2. ✅ **DOM elements** - Specific divs, spans, paragraphs with usage info
3. ✅ **React state** - Data stored in window.__NEXT_DATA__
4. ✅ **API calls** - Trying different endpoints (will probably fail with 403)

## Common Scenarios

### Scenario 1: Debug script finds data
```
[LLM Tracker DEBUG] ✓ MATCH FOUND: ["25 of 45 messages", "25", "45"]
success: true
```
→ Great! I'll update the scraper to use that pattern.

### Scenario 2: No pattern matches
```
[LLM Tracker DEBUG] Relevant lines: [...]
success: false
```
→ Share those "relevant lines" - I'll create a new pattern.

### Scenario 3: Page structure is different
```
[LLM Tracker DEBUG] Found __NEXT_DATA__: {...}
```
→ The data might be in React state instead of DOM text.

### Scenario 4: 403 on all API calls
```
[LLM Tracker DEBUG] Response status: 403
```
→ Expected! We'll use DOM scraping instead.

## Next Steps

Once you share the debug output, I'll:

1. See exactly what your Claude page looks like
2. Update the scraper to match YOUR specific page structure
3. Test with the new pattern
4. Switch back to production mode

## Quick Screenshot Alternative

If you prefer, you can also:

1. Visit https://claude.ai/settings/usage
2. Take a screenshot showing your usage (blur any personal info if needed)
3. Right-click on the usage text → "Inspect"
4. Screenshot the HTML in the inspector

This will also help me understand the page structure!

---

**Ready when you are! Just share the console output or screenshots.**
