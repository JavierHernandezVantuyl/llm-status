## Troubleshooting Dashboard

### Step 1: Check Browser Console

1. Open the dashboard at http://localhost:8000
2. Press F12 or right-click → Inspect
3. Go to "Console" tab
4. Click "Refresh Usage" on Claude card
5. Look at what's logged

### What You Might See:

#### ✅ Success
```
Organizations: [...]
Conversations: [...]
Organization details: {...}
```
→ It worked! If data looks wrong, share the console output

#### ❌ CORS Error
```
Access to fetch at 'https://claude.ai/api/organizations' from origin 'http://localhost:8000'
has been blocked by CORS policy
```
→ Claude.ai is blocking cross-origin requests

**Fix:** We need to use a different approach (see Option 2 below)

#### ❌ 401/403 Error
```
Error: Not logged in to claude.ai
```
→ You're not logged into claude.ai in THIS browser

**Fix:**
1. Open https://claude.ai in a new tab
2. Log in
3. Go back to localhost:8000 and refresh

#### ❌ Network Error
```
TypeError: Failed to fetch
```
→ Can't reach claude.ai

**Fix:** Check internet connection

---

## Alternative Approaches

### Option 1: Browser Extension (Best)
If CORS is blocking us, we need a browser extension that runs in claude.ai's context.

I can build a lightweight extension that:
- Monitors claude.ai/settings/usage
- Shows usage in a popup/badge
- No CORS issues
- Works everywhere

**Want me to build this?**

### Option 2: Iframe Embed
We could iframe claude.ai/settings/usage directly:

```html
<iframe src="https://claude.ai/settings/usage"></iframe>
```

But Claude probably blocks iframing for security.

### Option 3: Manual Check Script
A simple bookmarklet you run while on claude.ai:

```javascript
javascript:(function(){
  // Scrape usage from the page
  alert('Usage: ...');
})();
```

---

## Debug Steps

**Run this in console while on claude.ai:**

```javascript
// Check if logged in
fetch('https://claude.ai/api/organizations', {
    credentials: 'include'
})
.then(r => r.json())
.then(d => console.log('Orgs:', d))
.catch(e => console.error('Error:', e));
```

If this works on claude.ai but NOT on localhost:8000, it's definitely CORS.

---

## Next Steps Based on Error

1. **CORS Error** → Build browser extension
2. **Auth Error** → Log into claude.ai
3. **Success but wrong data** → Share console output so I can parse correctly
4. **Other error** → Share full error message

**What error do you see?**
