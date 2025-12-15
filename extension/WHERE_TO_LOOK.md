# 🔍 Where to Find the Debug Output

## The Problem

You're seeing errors in the **background script** console, but we need the **page content script** console!

The error "Could not establish connection. Receiving end does not exist" means the content script isn't loading on the claude.ai page.

## ✅ Correct Way to See Debug Output

### Step 1: Open Claude.ai Settings
1. Open a NEW tab
2. Go to: https://claude.ai/settings/usage
3. Make sure you're logged in (wait for the page to fully load)

### Step 2: Open Console on THAT Tab
1. Stay on the claude.ai tab
2. Press **F12** (or right-click → Inspect)
3. Click the **Console** tab
4. Look for messages starting with `[LLM Tracker DEBUG]`

### Step 3: What You Should See

If the content script is working, you'll see:
```
[LLM Tracker DEBUG] ===== STARTING CLAUDE DEBUG =====
[LLM Tracker DEBUG] URL: https://claude.ai/settings/usage
[LLM Tracker DEBUG] --- Strategy 1: Text Pattern Matching ---
[LLM Tracker DEBUG] Page text length: ...
[LLM Tracker DEBUG] Relevant lines: [...]
```

### Step 4: If You See NOTHING

If you don't see ANY `[LLM Tracker DEBUG]` messages on the claude.ai page, the content script isn't loading. This could be because:

1. **Extension not loaded correctly** - Reload it:
   - Go to `chrome://extensions/`
   - Click ↻ (reload) on "LLM Usage Tracker"
   - Check for errors

2. **Content script has errors** - Check extension page:
   - Go to `chrome://extensions/`
   - Look for errors under "LLM Usage Tracker"
   - Click "Errors" if you see any

3. **Page already loaded before extension** - Refresh:
   - Refresh the claude.ai/settings/usage page
   - Check console again

## 🆘 Alternative: Manual Debug Script

If the extension content script won't load, run this directly:

1. Visit https://claude.ai/settings/usage
2. Press F12 → Console
3. Paste this code and press Enter:

```javascript
console.log('=== PAGE TEXT ===');
console.log(document.body.innerText);
console.log('\n=== LOOKING FOR USAGE ===');

// Find all text with numbers
const allText = document.body.innerText;
const lines = allText.split('\n');
lines.forEach((line, i) => {
  if (line.match(/\d+/) && (
    line.toLowerCase().includes('message') ||
    line.toLowerCase().includes('usage') ||
    line.toLowerCase().includes('limit')
  )) {
    console.log(`Line ${i}: ${line}`);
  }
});

console.log('\n=== END ===');
```

This will show me what text is on your Claude settings page!

## 📸 Even Simpler: Screenshot

If all else fails, just:

1. Visit https://claude.ai/settings/usage
2. Take a screenshot showing your usage info
3. Blur out any personal information
4. Share it with me

I can see the text format and update the scraper to match!

---

**The key difference:**
- ❌ Background console (chrome://extensions/ → Service worker) = NOT what we need
- ✅ Claude.ai page console (claude.ai → F12) = WHERE THE DEBUG OUTPUT IS
