/**
 * Background Service Worker
 * Handles storage, badge updates, and coordination between content scripts and popup
 */

// Storage keys
const STORAGE_KEY_PREFIX = 'llm_usage_';

/**
 * Update extension badge based on usage
 */
function updateBadge(provider, usageData) {
  if (!usageData.success || !usageData.percentage) {
    // No data or error - show gray badge
    chrome.action.setBadgeText({ text: '?' });
    chrome.action.setBadgeBackgroundColor({ color: '#6B7280' });
    return;
  }

  const percentage = parseFloat(usageData.percentage);

  // Set badge text (percentage)
  chrome.action.setBadgeText({ text: Math.round(percentage) + '%' });

  // Set badge color based on status
  let color;
  if (percentage >= 95) {
    color = '#EF4444';  // Red - critical
  } else if (percentage >= 80) {
    color = '#F59E0B';  // Amber - warning
  } else {
    color = '#22C55E';  // Green - ok
  }

  chrome.action.setBadgeBackgroundColor({ color });

  // Set tooltip
  const tooltip = `${usageData.provider.toUpperCase()}: ${usageData.messagesUsed}/${usageData.messagesLimit} messages`;
  chrome.action.setTitle({ title: tooltip });
}

/**
 * Store usage data
 */
async function storeUsageData(provider, usageData) {
  const key = STORAGE_KEY_PREFIX + provider;

  try {
    await chrome.storage.local.set({ [key]: usageData });
    console.log('[LLM Tracker Background] Stored usage for', provider, usageData);

    // Update badge
    updateBadge(provider, usageData);

  } catch (error) {
    console.error('[LLM Tracker Background] Error storing data:', error);
  }
}

/**
 * Get usage data for a provider
 */
async function getUsageData(provider) {
  const key = STORAGE_KEY_PREFIX + provider;

  try {
    const result = await chrome.storage.local.get(key);
    return result[key] || null;
  } catch (error) {
    console.error('[LLM Tracker Background] Error getting data:', error);
    return null;
  }
}

/**
 * Get all usage data
 */
async function getAllUsageData() {
  try {
    const allData = await chrome.storage.local.get(null);
    const usageData = {};

    for (const [key, value] of Object.entries(allData)) {
      if (key.startsWith(STORAGE_KEY_PREFIX)) {
        const provider = key.replace(STORAGE_KEY_PREFIX, '');
        usageData[provider] = value;
      }
    }

    return usageData;
  } catch (error) {
    console.error('[LLM Tracker Background] Error getting all data:', error);
    return {};
  }
}

/**
 * Handle messages from content scripts and popup
 */
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('[LLM Tracker Background] Received message:', request.type);

  if (request.type === 'USAGE_UPDATE') {
    // Content script is sending updated usage data
    const { data } = request;
    storeUsageData(data.provider, data);
    sendResponse({ status: 'stored' });
  }

  else if (request.type === 'GET_USAGE') {
    // Popup is requesting usage data for a specific provider
    getUsageData(request.provider).then(data => {
      sendResponse({ data });
    });
    return true;  // Keep channel open for async response
  }

  else if (request.type === 'GET_ALL_USAGE') {
    // Popup is requesting all usage data
    getAllUsageData().then(data => {
      sendResponse({ data });
    });
    return true;  // Keep channel open for async response
  }

  else if (request.type === 'REFRESH_USAGE') {
    // Popup wants to trigger a refresh
    // Send message to content script if it's active
    chrome.tabs.query({ url: '*://claude.ai/*' }, (tabs) => {
      tabs.forEach(tab => {
        chrome.tabs.sendMessage(tab.id, {
          type: 'REQUEST_USAGE_UPDATE',
          provider: request.provider
        });
      });
    });
    sendResponse({ status: 'requested' });
  }
});

/**
 * Initialize on install
 */
chrome.runtime.onInstalled.addListener((details) => {
  console.log('[LLM Tracker Background] Extension installed/updated');

  // Set initial badge
  chrome.action.setBadgeText({ text: '' });

  if (details.reason === 'install') {
    // First install - open welcome page or settings
    console.log('[LLM Tracker Background] First install!');
  }
});

/**
 * Periodic refresh (every 5 minutes if Claude tab is open)
 */
chrome.alarms.create('periodicRefresh', { periodInMinutes: 5 });

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'periodicRefresh') {
    // Trigger refresh on any open Claude tabs
    chrome.tabs.query({ url: '*://claude.ai/*' }, (tabs) => {
      tabs.forEach(tab => {
        chrome.tabs.sendMessage(tab.id, {
          type: 'REQUEST_USAGE_UPDATE',
          provider: 'claude'
        });
      });
    });
  }
});

console.log('[LLM Tracker Background] Service worker started');
