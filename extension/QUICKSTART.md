# LLM Usage Tracker - Quick Start

Your browser extension is ready! Here's what to do next:

## ⚡ Quick Setup (3 Steps)

### 1. Generate Icons (30 seconds)
```bash
# Open this file in your browser:
open icons/GENERATE_ICONS.html

# Click "Download All Icons"
# Save all 3 files to the icons/ folder
```

### 2. Load Extension (1 minute)
**Chrome/Edge:**
1. Go to `chrome://extensions/`
2. Enable "Developer mode" (top right)
3. Click "Load unpacked"
4. Select this `extension` folder

**Firefox:**
1. Go to `about:debugging#/runtime/this-firefox`
2. Click "Load Temporary Add-on"
3. Select `manifest.json`

### 3. Test It!
1. Visit https://claude.ai/settings/usage
2. Click the extension icon
3. See your usage stats!

## 📁 What's Included

```
extension/
├── manifest.json              ✅ Extension config
├── providers.js               ✅ Provider settings (modular!)
├── background.js              ✅ Storage & badge updates
├── popup.html/js/css          ✅ UI interface
├── content-scripts/
│   └── claude.js              ✅ Claude scraper
├── icons/
│   └── GENERATE_ICONS.html    ⚠️  Run this to create icons
├── README.md                  📖 Full documentation
├── INSTALL.md                 📖 Detailed install guide
└── QUICKSTART.md             📖 You are here!
```

## ✨ Features

- **Auto-scrapes** usage from claude.ai/settings/usage
- **Live badge** shows percentage with color-coded status
- **Clean popup** with detailed stats
- **Auto-refresh** every 5 minutes
- **Privacy-first** - all data stays local

## 🎯 Current Status

- ✅ Claude support (fully implemented)
- 🔜 ChatGPT (config ready, needs content script)
- 🔜 Gemini (config ready, needs content script)
- 🔜 OpenAI API (config ready, needs content script)

## 🐛 Debugging

If something doesn't work:

1. **Check console logs**:
   - Visit claude.ai
   - Press F12 → Console
   - Look for `[LLM Tracker]` messages

2. **Check background logs**:
   - Go to `chrome://extensions/`
   - Click "Service worker"
   - View console

3. **Common issues**:
   - Badge shows "?": Visit claude.ai/settings/usage
   - No data: Make sure you're logged into claude.ai
   - Can't load extension: Generate icons first!

## 📚 Next Steps

- Read [README.md](README.md) for full documentation
- See [INSTALL.md](INSTALL.md) for detailed setup
- Check `providers.js` to see how to add new LLMs

## 🚀 Adding More Providers

It's super easy! Just:
1. Add config to `providers.js`
2. Create `content-scripts/{provider}.js`
3. Update `manifest.json`

See README.md for detailed instructions.

## 🎉 You're All Set!

The extension is ready to track your Claude usage. Once you generate the icons and load it, you'll have automatic usage tracking right in your browser!

Questions? Check README.md for troubleshooting and detailed docs.
