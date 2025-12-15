# Debug Claude.ai Scraping

## Step 1: Run This on claude.ai/settings/usage

1. Visit https://claude.ai/settings/usage (make sure you're logged in)
2. Wait for the page to fully load
3. Press F12 to open Developer Console
4. Paste this code and press Enter:

```javascript
// Debug script to find usage data on Claude page
console.log('=== CLAUDE PAGE DEBUG ===');

// 1. Check all text content
console.log('\n--- Page Text ---');
console.log(document.body.innerText);

// 2. Look for specific elements
console.log('\n--- Searching for usage-related elements ---');

// Try to find by common selectors
const selectors = [
  'div[data-testid*="usage"]',
  'div[class*="usage"]',
  'div[class*="limit"]',
  'span:contains("messages")',
  '[data-testid]',
  'p', 'span', 'div'
];

selectors.forEach(selector => {
  try {
    const elements = document.querySelectorAll(selector);
    if (elements.length > 0) {
      console.log(`Found ${elements.length} elements for: ${selector}`);
      elements.forEach((el, i) => {
        const text = el.innerText || el.textContent;
        if (text && text.toLowerCase().includes('message')) {
          console.log(`  [${i}] ${text.substring(0, 100)}`);
        }
      });
    }
  } catch(e) {}
});

// 3. Check for React data
console.log('\n--- Looking for React data ---');
const root = document.querySelector('#__next') || document.querySelector('[data-reactroot]');
if (root) {
  console.log('React root found:', root);
  const reactKey = Object.keys(root).find(key => key.startsWith('__react'));
  if (reactKey) {
    console.log('React data available:', reactKey);
  }
}

// 4. Look for API calls in Network
console.log('\n--- Check Network Tab ---');
console.log('Go to Network tab, filter by "Fetch/XHR", refresh page');
console.log('Look for requests to:');
console.log('  - /api/organizations');
console.log('  - /api/usage');
console.log('  - /api/account');

// 5. Check window object for data
console.log('\n--- Window object ---');
if (window.__INITIAL_STATE__ || window.__NEXT_DATA__) {
  console.log('Found initial state:', window.__INITIAL_STATE__ || window.__NEXT_DATA__);
}

console.log('\n=== END DEBUG ===');
console.log('\nShare the output above!');
```

## Step 2: Alternative - Inspect Element

1. Visit https://claude.ai/settings/usage
2. Right-click on the usage text (e.g., "25 of 45 messages")
3. Click "Inspect"
4. Copy the HTML structure and share it

## Step 3: Check Network Requests

1. Visit https://claude.ai/settings/usage
2. Open DevTools (F12) → Network tab
3. Filter by "Fetch/XHR"
4. Refresh the page
5. Look for API calls that contain usage data
6. Share the endpoint URLs and responses

## What to Look For

We need to find ONE of these:

1. **Text Pattern**: Something like "25 of 45 messages" or "25/45"
2. **HTML Element**: A specific div/span with usage data
3. **API Endpoint**: A fetch request that returns usage JSON
4. **React State**: Usage data stored in window.__NEXT_DATA__ or similar

## Common Issues

### 403 Error
- This means the API endpoint requires authentication
- We might need to use a different endpoint
- Or scrape from the page DOM instead

### Google Sign-On
- Should work fine with the extension
- The extension runs in the page context, so it has your cookies
- Make sure you're fully logged in before testing

## Next Steps

Run the debug script above and share:
1. The console output
2. Any HTML structure around the usage numbers
3. Any API endpoints you see in Network tab

This will help me fix the scraping logic!
