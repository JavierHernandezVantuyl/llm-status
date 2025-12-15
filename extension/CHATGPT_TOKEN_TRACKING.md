# ChatGPT Token Tracking - Feature Documentation

## 🎯 Overview

The ChatGPT integration adds **advanced token tracking** to the LLM Usage Tracker extension. Unlike Claude (which only shows percentages), ChatGPT tracking includes:

✅ **Message count** tracking (e.g., 12 / 40 messages)
✅ **Token estimation** based on character count
✅ **"Heaviness" metric** showing cumulative token load
✅ **Floating UI overlay** on chatgpt.com
✅ **3-hour rolling window** for usage tracking

## 🏗️ Architecture

### 1. Fetch Interception (Step 2)

The extension intercepts ChatGPT API requests using a **fetch proxy**:

```javascript
window.fetch = async function(...args) {
  const [resource, config] = args;
  const response = await originalFetch.apply(this, args);

  if (resource.includes('/backend-api/conversation')) {
    // Extract and analyze the request
  }

  return response;
}
```

**Key Implementation Details:**
- Runs in `"world": "MAIN"` context (manifest.json:37) to access page's fetch
- Executes at `"document_start"` (before page JavaScript loads)
- Non-blocking - doesn't interfere with chat functionality
- Wrapped in try/catch for safety (Step 5)

### 2. Token Estimation (Step 2)

Tokens are estimated using the **character count / 4** formula:

```javascript
function estimateTokens(text) {
  if (!text || typeof text !== 'string') return 0;
  return Math.ceil(text.length / TOKEN_ESTIMATE_DIVISOR); // divisor = 4
}
```

**Why divide by 4?**
- GPT tokenization averages ~4 characters per token for English text
- Examples:
  - "Hello world" (11 chars) → ~3 tokens
  - "How are you doing today?" (25 chars) → ~6 tokens
  - Long paragraph (400 chars) → ~100 tokens

**Accuracy:**
- ✅ Reasonably accurate for English text
- ⚠️ Less accurate for code, special characters, non-English
- Good enough for usage estimation without needing OpenAI's tokenizer

### 3. Enhanced Data Structure (Step 1)

Storage format changed from simple timestamp array to **object array with tokens**:

**Old format:**
```json
[1715123456789, 1715123567890, ...]
```

**New format:**
```json
[
  { "timestamp": 1715123456789, "tokens": 45 },
  { "timestamp": 1715123567890, "tokens": 128 },
  ...
]
```

**Storage key:** `chatgpt_usage_history`

### 4. Usage Calculation (Step 3)

Two metrics are tracked:

**A. Message Count:**
- Counts entries in the 3-hour window
- `messagesUsed / messagesLimit` (e.g., 12 / 40)
- Percentage: `(12 / 40) * 100 = 30%`

**B. Token Load:**
- Sums all tokens in the 3-hour window
- Example: `45 + 128 + 67 + ... = 850 tokens`
- Color-coded threshold:
  - 🟢 Green: < 1600 tokens
  - 🟡 Yellow: 1600-2000 tokens
  - 🔴 Red: > 2000 tokens

**Code:**
```javascript
async function calculateUsage() {
  const history = await getUsageHistory();

  const messageCount = history.length;
  const totalTokens = history.reduce((sum, entry) => sum + entry.tokens, 0);

  return {
    messageCount,
    totalTokens,
    percentage: ((messageCount / MESSAGE_LIMIT) * 100).toFixed(1),
    status: /* determined by thresholds */
  };
}
```

### 5. "Heaviness" UI (Step 4)

Two displays are created:

**A. Floating Overlay (on chatgpt.com):**
- Fixed position: top-right corner
- Two progress bars:
  1. Messages: 12 / 40 (visual bar)
  2. Est. Load: ~850 tokens (color-coded)
- Auto-updates when you send messages
- Closeable with × button

**B. Extension Popup:**
- Shows usage for all providers
- ChatGPT card includes token section:
  ```
  ┌────────────────────────────┐
  │ ChatGPT         Warning ⚠️  │
  │ 30% usage     High usage    │
  │ ████████░░░░░░░░░░░░░░░     │
  │ ─────────────────────────── │
  │ Token Load (3h window):     │
  │ ~850 tokens        [green]  │
  │ Free Plan    12 messages    │
  └────────────────────────────┘
  ```

### 6. Safety Handling (Step 5)

All critical operations are wrapped in try/catch:

```javascript
try {
  const bodyJson = JSON.parse(config.body);
  const messageText = extractMessage(bodyJson);
  const tokens = estimateTokens(messageText);
  await saveUsageEntry(tokens);
} catch (error) {
  // CRITICAL: Don't break chat!
  console.warn('[ChatGPT Tracker] Parse failed (non-critical):', error.message);
  // Fallback: save message with 0 tokens
  await saveUsageEntry(0);
}
```

**Why this matters:**
- If OpenAI changes their API structure, the extension won't crash the chat
- Users can still use ChatGPT normally
- We just miss one message's token count (not a big deal)

## 📊 Data Flow

```
User sends message to ChatGPT
        ↓
Fetch interceptor catches /backend-api/conversation request
        ↓
Extract message text from request body
        ↓
Estimate tokens (length / 4)
        ↓
Save to chrome.storage.local: { timestamp, tokens }
        ↓
Update floating UI overlay
        ↓
Send aggregated data to background script
        ↓
Update extension badge + popup
```

## 🧪 Testing Instructions

### 1. Install/Reload Extension
```bash
Chrome: chrome://extensions/ → Reload
```

### 2. Visit ChatGPT
```bash
https://chatgpt.com
```

### 3. Check Console (F12)
You should see:
```
[ChatGPT Tracker] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[ChatGPT Tracker] Content script loaded
[ChatGPT Tracker] Version: Fetch interception + Token tracking
[ChatGPT Tracker] ✓ Fetch interceptor installed
[ChatGPT Tracker] ✓ Floating UI created
```

### 4. Send a Test Message
Type something like: "Hello, how are you today?"

Check console for:
```
[ChatGPT Tracker] Intercepted conversation request
[ChatGPT Tracker] Message: Hello, how are you today?...
[ChatGPT Tracker] Estimated tokens: 6
[ChatGPT Tracker] Saved usage: 6 tokens
```

### 5. Check Floating UI
Top-right corner should show:
- Messages: 1 / 40
- Est. Load: ~6 tokens (green)

### 6. Send More Messages
Watch the metrics update:
- Message count increases
- Token load accumulates
- Color changes as you approach limits

### 7. Check Extension Popup
Click extension icon - should see:
- ChatGPT card with token metrics
- Token Load section showing cumulative usage

## 🎨 UI Color Coding

### Message Count Status:
- 🟢 **OK**: < 80% (< 32 messages)
- 🟡 **Warning**: 80-95% (32-38 messages)
- 🔴 **Critical**: ≥ 95% (≥ 38 messages)

### Token Load Status:
- 🟢 **OK**: < 1600 tokens
- 🟡 **Warning**: 1600-2000 tokens
- 🔴 **Critical**: > 2000 tokens

### Why these thresholds?
- ChatGPT free tier: 40 messages per 3 hours
- Average message: ~40-80 tokens
- 40 messages × 50 tokens = 2000 tokens (typical limit)
- Heavy usage: 25 messages × 100 tokens = 2500 tokens (warning!)

## 🔧 Configuration

Edit `content-scripts/chatgpt.js` to customize:

```javascript
const WINDOW_HOURS = 3;              // Rolling window size
const TOKEN_ESTIMATE_DIVISOR = 4;    // Characters per token
const HIGH_TOKEN_THRESHOLD = 2000;   // Warning threshold
const MESSAGE_LIMIT = 40;            // Free tier limit
```

## ⚠️ Limitations

1. **Token estimation is approximate**
   - Good for English text (~±10% accuracy)
   - Less accurate for code, special chars
   - Doesn't account for response tokens

2. **Only tracks user messages**
   - ChatGPT's responses aren't counted
   - System prompts aren't counted
   - Context window usage isn't tracked

3. **Rolling window**
   - Old entries auto-delete after 3 hours
   - Doesn't track lifetime usage
   - Resets on browser close (if storage cleared)

4. **API structure dependency**
   - If OpenAI changes API, may need updates
   - Currently works with ChatGPT as of Dec 2024
   - Safety catches prevent breakage

## 🚀 Benefits

1. **Proactive usage awareness** - See token load before hitting limits
2. **Heaviness metric** - Know when you're using complex/long messages
3. **Rolling window** - Focus on recent usage (3 hours)
4. **Non-intrusive** - Floating UI can be closed
5. **Safe** - Won't break ChatGPT functionality

## 📈 Future Enhancements

- [ ] Track ChatGPT Plus (higher limits)
- [ ] Track response tokens (if accessible)
- [ ] Historical usage graphs
- [ ] Per-conversation token tracking
- [ ] Export usage data to CSV
- [ ] Notification when approaching limits
- [ ] More accurate tokenization (use tiktoken library)

## 🎉 Complete!

Your extension now tracks both:
- **Claude**: Percentage-based usage (DOM scraping)
- **ChatGPT**: Message count + Token load (fetch interception)

Both work seamlessly together in the same extension!
