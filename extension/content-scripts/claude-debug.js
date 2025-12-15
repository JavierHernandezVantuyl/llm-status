/**
 * Claude Usage Scraper - DEBUG VERSION
 * This version logs everything it tries so we can see what's failing
 */

(function() {
  'use strict';

  const PROVIDER_ID = 'claude';

  console.log('[LLM Tracker DEBUG] ===== STARTING CLAUDE DEBUG =====');
  console.log('[LLM Tracker DEBUG] URL:', window.location.href);
  console.log('[LLM Tracker DEBUG] Timestamp:', new Date().toISOString());

  /**
   * Try multiple scraping strategies
   */
  function debugScrapeUsage() {
    const result = {
      provider: PROVIDER_ID,
      timestamp: Date.now(),
      success: false,
      debugInfo: {}
    };

    console.log('[LLM Tracker DEBUG] --- Strategy 1: Text Pattern Matching ---');

    // Get all page text
    const bodyText = document.body.innerText;
    console.log('[LLM Tracker DEBUG] Page text length:', bodyText.length);
    console.log('[LLM Tracker DEBUG] First 500 chars:', bodyText.substring(0, 500));

    // Log lines that contain "message" or "usage"
    const lines = bodyText.split('\n');
    const relevantLines = lines.filter(line =>
      line.toLowerCase().includes('message') ||
      line.toLowerCase().includes('usage') ||
      line.toLowerCase().includes('limit') ||
      /\d+/.test(line)
    );
    console.log('[LLM Tracker DEBUG] Relevant lines:', relevantLines);
    result.debugInfo.relevantLines = relevantLines;

    // Try different regex patterns
    const patterns = [
      { name: 'Pattern 1: X of Y messages', regex: /(\d+)\s*(?:of|\/)\s*(\d+)\s*messages?/i },
      { name: 'Pattern 2: messages: X/Y', regex: /messages?[:\s]+(\d+)\s*\/\s*(\d+)/i },
      { name: 'Pattern 3: usage: X/Y', regex: /usage[:\s]+(\d+)\s*\/\s*(\d+)/i },
      { name: 'Pattern 4: X / Y', regex: /(\d+)\s*\/\s*(\d+)/i },
      { name: 'Pattern 5: sent X of Y', regex: /sent\s+(\d+)\s+of\s+(\d+)/i },
      { name: 'Pattern 6: X out of Y', regex: /(\d+)\s+out\s+of\s+(\d+)/i }
    ];

    for (const { name, regex } of patterns) {
      console.log(`[LLM Tracker DEBUG] Trying: ${name}`);
      const match = bodyText.match(regex);
      if (match) {
        console.log(`[LLM Tracker DEBUG] ✓ MATCH FOUND:`, match);
        result.messagesUsed = parseInt(match[1]);
        result.messagesLimit = parseInt(match[2]);
        result.messagesRemaining = result.messagesLimit - result.messagesUsed;
        result.percentage = (result.messagesUsed / result.messagesLimit * 100).toFixed(1);
        result.success = true;
        result.debugInfo.matchedPattern = name;
        result.debugInfo.matchedText = match[0];
        break;
      }
    }

    console.log('[LLM Tracker DEBUG] --- Strategy 2: DOM Element Search ---');

    // Look for common class names and data attributes
    const searchSelectors = [
      { name: 'data-testid with usage', selector: '[data-testid*="usage"]' },
      { name: 'class with usage', selector: '[class*="usage"]' },
      { name: 'class with limit', selector: '[class*="limit"]' },
      { name: 'class with message', selector: '[class*="message"]' },
      { name: 'all paragraphs', selector: 'p' },
      { name: 'all spans', selector: 'span' },
      { name: 'all divs with text', selector: 'div' }
    ];

    searchSelectors.forEach(({ name, selector }) => {
      try {
        const elements = document.querySelectorAll(selector);
        console.log(`[LLM Tracker DEBUG] ${name}: ${elements.length} elements`);

        elements.forEach((el, i) => {
          const text = (el.innerText || el.textContent || '').trim();
          if (text && (text.includes('message') || text.includes('usage') || /\d+.*\d+/.test(text))) {
            console.log(`[LLM Tracker DEBUG]   [${i}] ${text.substring(0, 100)}`);

            // Try to extract numbers from this element
            if (!result.success) {
              for (const { regex } of patterns) {
                const match = text.match(regex);
                if (match && match[1] && match[2]) {
                  console.log(`[LLM Tracker DEBUG]   ✓ FOUND IN ELEMENT:`, match);
                  result.messagesUsed = parseInt(match[1]);
                  result.messagesLimit = parseInt(match[2]);
                  result.messagesRemaining = result.messagesLimit - result.messagesUsed;
                  result.percentage = (result.messagesUsed / result.messagesLimit * 100).toFixed(1);
                  result.success = true;
                  result.debugInfo.foundInElement = selector;
                  result.debugInfo.elementText = text;
                  break;
                }
              }
            }
          }
        });
      } catch (e) {
        console.log(`[LLM Tracker DEBUG] Error with ${name}:`, e);
      }
    });

    console.log('[LLM Tracker DEBUG] --- Strategy 3: React State Check ---');

    // Check for React Next.js data
    if (window.__NEXT_DATA__) {
      console.log('[LLM Tracker DEBUG] Found __NEXT_DATA__:', window.__NEXT_DATA__);
      result.debugInfo.nextData = JSON.stringify(window.__NEXT_DATA__).substring(0, 500);
    }

    if (window.__INITIAL_STATE__) {
      console.log('[LLM Tracker DEBUG] Found __INITIAL_STATE__:', window.__INITIAL_STATE__);
      result.debugInfo.initialState = JSON.stringify(window.__INITIAL_STATE__).substring(0, 500);
    }

    // Determine status if we found data
    if (result.success && result.percentage) {
      const pct = parseFloat(result.percentage);
      if (pct >= 95) {
        result.status = 'critical';
      } else if (pct >= 80) {
        result.status = 'warning';
      } else {
        result.status = 'ok';
      }

      // Determine plan type
      if (result.messagesLimit) {
        result.planType = result.messagesLimit <= 50 ? 'free' : 'pro';
      }
    }

    console.log('[LLM Tracker DEBUG] --- FINAL RESULT ---');
    console.log('[LLM Tracker DEBUG] Success:', result.success);
    console.log('[LLM Tracker DEBUG] Result:', result);
    console.log('[LLM Tracker DEBUG] ===== END DEBUG =====');

    return result;
  }

  /**
   * Try API approach (will likely fail with 403, but let's try)
   */
  async function debugFetchAPI() {
    console.log('[LLM Tracker DEBUG] --- Strategy 4: API Fetch ---');

    const endpoints = [
      'https://claude.ai/api/organizations',
      'https://claude.ai/api/account',
      'https://claude.ai/api/auth/current_account'
    ];

    for (const url of endpoints) {
      try {
        console.log(`[LLM Tracker DEBUG] Trying: ${url}`);
        const response = await fetch(url, { credentials: 'include' });
        console.log(`[LLM Tracker DEBUG] Response status: ${response.status}`);

        if (response.ok) {
          const data = await response.json();
          console.log(`[LLM Tracker DEBUG] ✓ Success! Data:`, data);
          return { success: true, apiData: data, endpoint: url };
        } else {
          console.log(`[LLM Tracker DEBUG] ✗ Failed with status ${response.status}`);
        }
      } catch (error) {
        console.log(`[LLM Tracker DEBUG] ✗ Error:`, error.message);
      }
    }

    return { success: false };
  }

  /**
   * Send results to background
   */
  function sendToBackground(data) {
    console.log('[LLM Tracker DEBUG] Sending to background:', data);
    try {
      chrome.runtime.sendMessage({
        type: 'USAGE_UPDATE',
        data: data
      }, (response) => {
        console.log('[LLM Tracker DEBUG] Background response:', response);
      });
    } catch (error) {
      console.log('[LLM Tracker DEBUG] Error sending to background:', error);
    }
  }

  /**
   * Main debug function
   */
  async function runDebug() {
    console.log('[LLM Tracker DEBUG] Starting debug sequence...');

    // Try scraping first
    const scrapeResult = debugScrapeUsage();

    // Try API (will probably fail but worth trying)
    const apiResult = await debugFetchAPI();

    // Combine results
    const finalResult = {
      ...scrapeResult,
      apiDebug: apiResult
    };

    // Send to background
    sendToBackground(finalResult);

    // Also log to console for user
    console.log('[LLM Tracker DEBUG] ========================================');
    console.log('[LLM Tracker DEBUG] COPY THE RESULTS BELOW:');
    console.log('[LLM Tracker DEBUG] ========================================');
    console.log(JSON.stringify(finalResult, null, 2));
    console.log('[LLM Tracker DEBUG] ========================================');
  }

  /**
   * Initialize
   */
  function init() {
    console.log('[LLM Tracker DEBUG] Content script loaded');

    // Run after page loads
    if (document.readyState === 'complete') {
      setTimeout(runDebug, 2000);
    } else {
      window.addEventListener('load', () => {
        setTimeout(runDebug, 2000);
      });
    }

    // Also run on message from popup
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
      if (request.type === 'REQUEST_USAGE_UPDATE') {
        console.log('[LLM Tracker DEBUG] Refresh requested from popup');
        runDebug();
        sendResponse({ status: 'debugging' });
      }
    });
  }

  init();

})();
