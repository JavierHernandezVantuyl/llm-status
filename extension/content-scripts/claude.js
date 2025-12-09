/**
 * Claude Usage Scraper
 * Runs on claude.ai to extract chat usage information
 */

(function() {
  'use strict';

  const PROVIDER_ID = 'claude';
  const CHECK_INTERVAL = 5000; // Check every 5 seconds when on settings page

  /**
   * Scrape usage from claude.ai/settings/usage page
   */
  function scrapeUsageFromPage() {
    // Look for usage information on the page
    // This will depend on the actual HTML structure of claude.ai/settings/usage

    const result = {
      provider: PROVIDER_ID,
      timestamp: Date.now(),
      success: false
    };

    try {
      // Method 1: Try to find usage text patterns
      const bodyText = document.body.innerText;

      // Look for patterns like "25 of 45 messages" or "25/45"
      const patterns = [
        /(\d+)\s*(?:of|\/)\s*(\d+)\s*messages?/i,
        /messages?[:\s]+(\d+)\s*\/\s*(\d+)/i,
        /usage[:\s]+(\d+)\s*\/\s*(\d+)/i
      ];

      for (const pattern of patterns) {
        const match = bodyText.match(pattern);
        if (match) {
          result.messagesUsed = parseInt(match[1]);
          result.messagesLimit = parseInt(match[2]);
          result.messagesRemaining = result.messagesLimit - result.messagesUsed;
          result.percentage = (result.messagesUsed / result.messagesLimit * 100).toFixed(1);
          result.success = true;
          break;
        }
      }

      // Look for reset time
      const resetPatterns = [
        /resets?\s+in[:\s]+([^.\n]+)/i,
        /window\s+resets?\s+in[:\s]+([^.\n]+)/i
      ];

      for (const pattern of resetPatterns) {
        const match = bodyText.match(pattern);
        if (match) {
          result.resetTime = match[1].trim();
          break;
        }
      }

      // Determine plan type based on limit
      if (result.messagesLimit) {
        result.planType = result.messagesLimit <= 50 ? 'free' : 'pro';
      }

      // Determine status
      if (result.percentage) {
        const pct = parseFloat(result.percentage);
        if (pct >= 95) {
          result.status = 'critical';
        } else if (pct >= 80) {
          result.status = 'warning';
        } else {
          result.status = 'ok';
        }
      }

    } catch (error) {
      console.error('[LLM Tracker] Error scraping Claude usage:', error);
      result.error = error.message;
    }

    return result;
  }

  /**
   * Fetch usage from Claude API (if scraping doesn't work)
   */
  async function fetchUsageFromAPI() {
    try {
      const orgResponse = await fetch('https://claude.ai/api/organizations', {
        credentials: 'include'
      });

      if (!orgResponse.ok) {
        throw new Error(`API returned ${orgResponse.status}`);
      }

      const orgs = await orgResponse.json();
      if (!orgs || orgs.length === 0) {
        throw new Error('No organizations found');
      }

      const orgId = orgs[0].uuid;

      // Fetch organization details
      const detailsResponse = await fetch(`https://claude.ai/api/organizations/${orgId}`, {
        credentials: 'include'
      });

      if (!detailsResponse.ok) {
        throw new Error(`Failed to fetch org details: ${detailsResponse.status}`);
      }

      const orgDetails = await detailsResponse.json();

      // Parse API response
      const result = {
        provider: PROVIDER_ID,
        timestamp: Date.now(),
        success: false,
        rawData: orgDetails
      };

      // TODO: Parse actual usage from API response
      // The structure will depend on what Claude's API returns
      // For now, mark as needing implementation
      console.log('[LLM Tracker] Claude API response:', orgDetails);

      return result;

    } catch (error) {
      console.error('[LLM Tracker] Error fetching from Claude API:', error);
      return {
        provider: PROVIDER_ID,
        timestamp: Date.now(),
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Send usage data to background script
   */
  function sendUsageData(usageData) {
    chrome.runtime.sendMessage({
      type: 'USAGE_UPDATE',
      data: usageData
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
    console.log('[LLM Tracker] Checking Claude usage...');

    // First try scraping the page
    let usageData = scrapeUsageFromPage();

    // If scraping didn't work, try API
    if (!usageData.success) {
      console.log('[LLM Tracker] Page scraping failed, trying API...');
      usageData = await fetchUsageFromAPI();
    }

    // Send data to background script
    if (usageData.success || usageData.error) {
      console.log('[LLM Tracker] Sending usage data:', usageData);
      sendUsageData(usageData);
    }
  }

  /**
   * Initialize
   */
  function init() {
    console.log('[LLM Tracker] Claude content script loaded');

    // Check usage when page loads
    if (document.readyState === 'complete') {
      setTimeout(checkAndReportUsage, 2000);
    } else {
      window.addEventListener('load', () => {
        setTimeout(checkAndReportUsage, 2000);
      });
    }

    // If on settings page, check periodically
    if (isOnUsagePage()) {
      setInterval(checkAndReportUsage, CHECK_INTERVAL);
    }

    // Listen for messages from popup requesting fresh data
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
      if (request.type === 'REQUEST_USAGE_UPDATE' && request.provider === PROVIDER_ID) {
        checkAndReportUsage();
        sendResponse({ status: 'checking' });
      }
    });
  }

  // Start
  init();

})();
