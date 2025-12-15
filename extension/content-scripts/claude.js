/**
 * Claude Usage Scraper
 * Runs on claude.ai to extract chat usage information
 *
 * TOS-COMPLIANT: Only reads visible page content, no API calls
 */

(function() {
  'use strict';

  const PROVIDER_ID = 'claude';
  const CHECK_INTERVAL = 5000; // Check every 5 seconds when on settings page

  /**
   * Wait for page to be ready and percentage to appear
   */
  async function waitForPageLoad(maxAttempts = 10) {
    for (let i = 0; i < maxAttempts; i++) {
      const text = document.body.innerText;
      if (text.includes('% used')) {
        console.log('[LLM Tracker] ✓ Page loaded, usage data visible');
        return true;
      }
      console.log(`[LLM Tracker] Waiting for page to load... (attempt ${i + 1}/${maxAttempts})`);
      await new Promise(resolve => setTimeout(resolve, 500));
    }
    console.log('[LLM Tracker] ⚠️ Page load timeout, proceeding anyway');
    return false;
  }

  /**
   * Scrape usage from visible page content ONLY (TOS-compliant)
   */
  async function scrapeUsageFromPage() {
    const result = {
      provider: PROVIDER_ID,
      timestamp: Date.now(),
      success: false
    };

    try {
      // Wait for page to be ready
      await waitForPageLoad();

      // Re-read the DOM fresh each time
      const bodyText = document.body.innerText;

      console.log('[LLM Tracker] ===== SCRAPING PAGE =====');
      console.log('[LLM Tracker] Timestamp:', new Date().toLocaleTimeString());
      console.log('[LLM Tracker] Looking for usage percentages...');

      // Look for "X% used" pattern
      const percentagePattern = /(\d+)%\s*used/gi;
      const matches = [...bodyText.matchAll(percentagePattern)];

      if (matches.length > 0) {
        // Get all percentages found
        const percentages = matches.map(m => parseInt(m[1]));
        const maxPercentage = Math.max(...percentages);

        console.log('[LLM Tracker] ✓ Found percentages:', percentages);
        console.log('[LLM Tracker] → Using maximum:', maxPercentage + '%');

        result.percentage = maxPercentage.toFixed(1);
        result.success = true;

        // Determine status
        if (maxPercentage >= 95) {
          result.status = 'critical';
        } else if (maxPercentage >= 80) {
          result.status = 'warning';
        } else {
          result.status = 'ok';
        }

        // Look for reset time
        const resetPattern = /Resets?\s+in\s+([^.\n]+)/i;
        const resetMatch = bodyText.match(resetPattern);
        if (resetMatch) {
          result.resetTime = resetMatch[1].trim();
          console.log('[LLM Tracker] ✓ Reset time:', result.resetTime);
        }

        // Detect plan type from visible text
        if (bodyText.toLowerCase().includes('pro plan')) {
          result.planType = 'pro';
        } else if (bodyText.toLowerCase().includes('free plan')) {
          result.planType = 'free';
        } else {
          // Default guess based on URL/context
          result.planType = 'unknown';
        }

        console.log('[LLM Tracker] ✓ Final data:', result);

      } else {
        console.log('[LLM Tracker] ✗ No "X% used" pattern found');
        console.log('[LLM Tracker] Page text sample:', bodyText.substring(0, 500));
        result.error = 'Usage percentage not found on page';
      }

    } catch (error) {
      console.error('[LLM Tracker] Error scraping:', error);
      result.error = error.message;
    }

    console.log('[LLM Tracker] ===== SCRAPING COMPLETE =====');
    return result;
  }

  /**
   * Send usage data to background script
   */
  function sendUsageData(usageData) {
    chrome.runtime.sendMessage({
      type: 'USAGE_UPDATE',
      data: usageData
    }, (response) => {
      if (chrome.runtime.lastError) {
        console.error('[LLM Tracker] Error sending to background:', chrome.runtime.lastError);
      } else if (response) {
        console.log('[LLM Tracker] ✓ Data sent to background:', response);
      }
    });
  }

  /**
   * Check if we're on the settings/usage page
   */
  function isOnUsagePage() {
    return window.location.href.includes('claude.ai/settings/usage') ||
           window.location.href.includes('claude.ai/settings');
  }

  /**
   * Main function to extract and report usage
   */
  async function checkAndReportUsage() {
    console.log('[LLM Tracker] ━━━━━ REFRESH START ━━━━━');
    console.log('[LLM Tracker] Time:', new Date().toLocaleTimeString());
    console.log('[LLM Tracker] URL:', window.location.href);

    const usageData = await scrapeUsageFromPage();

    if (usageData.success) {
      console.log('[LLM Tracker] ✓ Sending usage data:', usageData);
      sendUsageData(usageData);
    } else {
      console.log('[LLM Tracker] ✗ Failed to get usage data');
      console.log('[LLM Tracker] Error:', usageData.error);

      // Send error state so UI knows we tried
      sendUsageData(usageData);
    }

    console.log('[LLM Tracker] ━━━━━ REFRESH END ━━━━━');
  }

  /**
   * Set up MutationObserver to detect when usage updates
   */
  function observeUsageChanges() {
    if (!isOnUsagePage()) return;

    console.log('[LLM Tracker] Setting up MutationObserver for auto-updates...');

    const observer = new MutationObserver((mutations) => {
      // Check if any mutation contains "% used" text
      for (const mutation of mutations) {
        if (mutation.type === 'characterData' || mutation.type === 'childList') {
          const text = mutation.target.textContent || '';
          if (text.includes('% used')) {
            console.log('[LLM Tracker] ⚡ Usage changed detected, refreshing...');
            checkAndReportUsage();
            break;
          }
        }
      }
    });

    // Observe the whole document for changes
    observer.observe(document.body, {
      childList: true,
      subtree: true,
      characterData: true
    });

    console.log('[LLM Tracker] ✓ MutationObserver active');
  }

  /**
   * Initialize
   */
  function init() {
    console.log('[LLM Tracker] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('[LLM Tracker] Claude content script loaded');
    console.log('[LLM Tracker] Version: DOM-only (TOS-compliant)');
    console.log('[LLM Tracker] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

    // Check usage when page loads
    if (document.readyState === 'complete') {
      setTimeout(checkAndReportUsage, 2000);
    } else {
      window.addEventListener('load', () => {
        setTimeout(checkAndReportUsage, 2000);
      });
    }

    // If on settings page, set up auto-detection
    if (isOnUsagePage()) {
      // Periodic check every 5 seconds
      setInterval(checkAndReportUsage, CHECK_INTERVAL);

      // Also observe DOM changes for instant updates
      observeUsageChanges();
    }

    // Listen for manual refresh from popup
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
      console.log('[LLM Tracker] Message received:', request.type);

      if (request.type === 'REQUEST_USAGE_UPDATE' && request.provider === PROVIDER_ID) {
        console.log('[LLM Tracker] 🔄 Manual refresh requested');

        // Trigger immediate refresh
        checkAndReportUsage().then(() => {
          console.log('[LLM Tracker] ✓ Manual refresh completed');
        }).catch(err => {
          console.error('[LLM Tracker] ✗ Manual refresh failed:', err);
        });

        sendResponse({ status: 'refreshing' });
      }

      return true; // Keep channel open
    });
  }

  // Start!
  init();

})();
