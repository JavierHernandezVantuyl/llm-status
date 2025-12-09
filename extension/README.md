# LLM Usage Tracker - Browser Extension

A lightweight browser extension that automatically tracks your chat usage across Claude and other LLM providers.

## Features

- **Automatic Usage Tracking**: Scrapes usage data directly from claude.ai/settings/usage
- **Live Badge Updates**: Shows usage percentage in extension badge with color-coded status
  - 🟢 Green: < 80% used (OK)
  - 🟡 Amber: 80-95% used (Warning)
  - 🔴 Red: ≥ 95% used (Critical)
- **Clean Popup UI**: View detailed usage stats for all providers
- **Modular Design**: Easy to add support for ChatGPT, Gemini, OpenAI API, and more
- **Privacy First**: All data stored locally in your browser

## Current Support

- ✅ **Claude** (claude.ai) - Fully implemented
- 🔜 **ChatGPT** (chatgpt.com) - Coming soon
- 🔜 **Gemini** (gemini.google.com) - Coming soon
- 🔜 **OpenAI API** (platform.openai.com) - Coming soon

## Installation

### Option 1: Load Unpacked (Development)

1. **Add Icons** (required before loading):
   ```bash
   cd extension/icons
   # Add three PNG files:
   # - icon16.png (16x16)
   # - icon48.png (48x48)
   # - icon128.png (128x128)
   ```
   You can create simple placeholder icons or use any LLM-themed icons.

2. **Chrome/Edge**:
   - Open `chrome://extensions/`
   - Enable "Developer mode" (top right)
   - Click "Load unpacked"
   - Select the `extension` folder

3. **Firefox**:
   - Open `about:debugging#/runtime/this-firefox`
   - Click "Load Temporary Add-on"
   - Select `manifest.json` from the `extension` folder

### Option 2: Install from ZIP (Coming Soon)

Pre-packaged ZIP file with icons will be available for easy installation.

## Usage

### First Time Setup

1. Navigate to https://claude.ai/settings/usage
2. The extension will automatically detect and scrape your usage
3. Click the extension icon to view your usage stats

### Viewing Usage

- **Badge**: Shows current usage percentage with color-coded status
- **Popup**: Click the extension icon for detailed stats including:
  - Messages used / total limit
  - Percentage and progress bar
  - Plan type (Free/Pro)
  - Reset time
  - Last updated timestamp

### Refreshing Data

- **Auto-refresh**: Checks every 5 minutes when Claude tabs are open
- **Manual refresh**: Click "Refresh" button in popup
- **Page navigation**: Updates when you visit claude.ai/settings/usage

## How It Works

### Architecture

```
┌─────────────────┐
│   claude.ai     │
│  (Content Script)│──┐
└─────────────────┘  │
                     ▼
┌─────────────────┐  ┌──────────────┐
│  Background     │◄─┤  Chrome      │
│  Service Worker │  │  Storage     │
└─────────────────┘  └──────────────┘
         │
         ▼
┌─────────────────┐
│  Popup UI       │
│  (Badge + Panel)│
└─────────────────┘
```

1. **Content Script** (`content-scripts/claude.js`):
   - Runs on claude.ai pages
   - Scrapes usage from page text (e.g., "25 of 45 messages")
   - Falls back to API calls if scraping fails
   - Sends data to background script

2. **Background Script** (`background.js`):
   - Stores usage data in chrome.storage.local
   - Updates extension badge with percentage and color
   - Coordinates between content scripts and popup
   - Triggers periodic refreshes every 5 minutes

3. **Popup** (`popup.html`, `popup.js`, `popup.css`):
   - Displays detailed usage stats for all providers
   - Allows manual refresh
   - Shows last updated time

### Data Format

```javascript
{
  provider: 'claude',
  timestamp: 1234567890,
  success: true,
  messagesUsed: 25,
  messagesLimit: 45,
  messagesRemaining: 20,
  percentage: '55.6',
  status: 'ok',  // 'ok' | 'warning' | 'critical'
  planType: 'free',  // 'free' | 'pro'
  resetTime: 'in 5 hours'
}
```

## Adding New Providers

The extension is designed to make adding new LLM providers easy:

1. **Add provider config** to `providers.js`:
   ```javascript
   chatgpt: {
     id: 'chatgpt',
     name: 'ChatGPT',
     type: 'chat',
     color: '#10A37F',
     urls: {
       settings: 'https://chatgpt.com/settings',
       base: 'https://chatgpt.com'
     },
     defaultLimit: 40,
     enabled: true
   }
   ```

2. **Create content script** at `content-scripts/chatgpt.js`:
   ```javascript
   // Scrape usage from chatgpt.com
   // Send to background script
   ```

3. **Update manifest.json**:
   ```json
   {
     "content_scripts": [
       {
         "matches": ["https://chatgpt.com/*"],
         "js": ["providers.js", "content-scripts/chatgpt.js"]
       }
     ]
   }
   ```

That's it! The popup and background script will automatically pick up the new provider.

## Development

### Project Structure

```
extension/
├── manifest.json          # Extension configuration
├── providers.js           # Provider configs (modular!)
├── background.js          # Service worker
├── popup.html            # Popup UI
├── popup.js              # Popup logic
├── popup.css             # Popup styling
├── content-scripts/
│   └── claude.js         # Claude scraper
└── icons/
    ├── icon16.png        # 16x16 badge icon
    ├── icon48.png        # 48x48 toolbar icon
    └── icon128.png       # 128x128 store icon
```

### Debugging

**Content Script**:
- Open claude.ai
- Press F12 → Console tab
- Look for `[LLM Tracker]` logs

**Background Script**:
- Open `chrome://extensions/`
- Click "Service worker" under the extension
- View logs in console

**Popup**:
- Right-click extension icon → "Inspect popup"
- View console logs

### Testing

1. Visit https://claude.ai/settings/usage
2. Check browser console for `[LLM Tracker]` logs
3. Verify usage data is scraped correctly
4. Check extension badge shows percentage
5. Open popup and verify UI displays data
6. Test refresh button
7. Wait 5 minutes and verify auto-refresh works

## Privacy & Security

- **No external servers**: All data stays in your browser
- **No tracking**: Extension doesn't send any data to third parties
- **Local storage only**: Uses chrome.storage.local
- **Open source**: All code is visible and auditable

## Troubleshooting

### Badge shows "?" or is gray
- Extension couldn't fetch usage data
- Make sure you're logged into claude.ai
- Check console for errors

### "No usage data available"
- Visit https://claude.ai/settings/usage to trigger scraping
- Click "Refresh" button in popup
- Check browser console for scraping errors

### Scraping patterns don't match
If Claude changes their UI, you may need to update the regex patterns in `content-scripts/claude.js`:

```javascript
const patterns = [
  /(\d+)\s*(?:of|\/)\s*(\d+)\s*messages?/i,
  // Add new patterns here
];
```

### API method fails
The extension first tries page scraping, then falls back to API calls. If both fail:
- Check Network tab for failed requests
- Verify you're logged into claude.ai
- Check console for detailed error messages

## Roadmap

- [ ] Add ChatGPT support
- [ ] Add Gemini support
- [ ] Add OpenAI API usage tracking
- [ ] Add notification when near limit
- [ ] Add usage history/trends
- [ ] Export usage data to CSV
- [ ] Dark mode
- [ ] Custom refresh intervals
- [ ] Multi-account support

## License

GNU AGPLv3

## Contributing

This extension is designed to be modular and easy to extend. Contributions for new provider support are welcome!

1. Fork the repo
2. Add provider config and content script
3. Test thoroughly
4. Submit PR

## Credits

Built for tracking chat usage across multiple LLM providers, starting with Claude.
