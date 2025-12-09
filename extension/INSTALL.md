# Quick Installation Guide

## Step 1: Generate Icons (Required)

1. Open `icons/GENERATE_ICONS.html` in your browser
2. Click "Download All Icons"
3. Save all three PNG files to the `icons/` folder:
   - icon16.png
   - icon48.png
   - icon128.png

**Alternative**: Use any PNG icons you prefer (just name them correctly).

## Step 2: Load Extension in Chrome/Edge

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable **Developer mode** (toggle in top-right corner)
3. Click **Load unpacked**
4. Select the `extension` folder (this folder)
5. Done! You should see "LLM Usage Tracker" in your extensions

## Step 3: Load Extension in Firefox

1. Open Firefox and navigate to `about:debugging#/runtime/this-firefox`
2. Click **Load Temporary Add-on**
3. Navigate to the `extension` folder and select `manifest.json`
4. Done! The extension will stay loaded until you close Firefox

## Step 4: Test It

1. Navigate to https://claude.ai/settings/usage
2. You should see console logs: `[LLM Tracker] Claude content script loaded`
3. Click the extension icon in your toolbar
4. You should see your Claude usage stats!

## Troubleshooting

### Extension won't load
- Make sure all three icon files are in the `icons/` folder
- Check that manifest.json exists in the extension folder
- Look for error messages in chrome://extensions/

### Badge shows "?" or gray
- Make sure you're logged into claude.ai
- Visit https://claude.ai/settings/usage to trigger scraping
- Click "Refresh" in the extension popup
- Check browser console for errors (F12)

### No data showing
- The extension needs you to visit claude.ai/settings/usage at least once
- Make sure you're logged in to claude.ai
- Try clicking "Refresh Claude" in the popup

### Console errors
Open the extension's service worker console:
1. Go to chrome://extensions/
2. Find "LLM Usage Tracker"
3. Click "Service worker" to view background logs

## Uninstalling

**Chrome/Edge**: Go to chrome://extensions/ and click "Remove"

**Firefox**: Extension is automatically removed when you restart the browser (temporary add-on)

## Next Steps

- Set up the extension to auto-refresh every 5 minutes
- Add support for other LLM providers (see README.md)
- Customize refresh intervals in background.js
