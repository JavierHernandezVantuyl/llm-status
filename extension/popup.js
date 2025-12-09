/**
 * Popup Script
 * Displays usage data from all enabled providers
 */

// Get DOM elements
const providersContainer = document.getElementById('providers-container');
const refreshAllBtn = document.getElementById('refresh-all');
const lastUpdatedEl = document.getElementById('last-updated');

/**
 * Create a provider card element
 */
function createProviderCard(provider, usageData) {
  const card = document.createElement('div');
  card.className = `provider-card ${!provider.enabled ? 'disabled' : ''}`;
  card.dataset.provider = provider.id;

  // Determine status class
  let statusClass = 'status-unknown';
  let statusText = 'No Data';

  if (usageData && usageData.success) {
    statusClass = `status-${usageData.status || 'ok'}`;
    statusText = usageData.status === 'critical' ? 'Critical' :
                 usageData.status === 'warning' ? 'Warning' : 'OK';
  } else if (usageData && usageData.error) {
    statusClass = 'status-unknown';
    statusText = 'Error';
  }

  // Build the card HTML
  card.innerHTML = `
    <div class="provider-header">
      <div class="provider-name">
        <span class="provider-dot" style="background-color: ${provider.color}"></span>
        <span>${provider.name}</span>
      </div>
      <span class="provider-status ${statusClass}">${statusText}</span>
    </div>

    ${usageData && usageData.success ? `
      <div class="usage-stats">
        <div class="usage-numbers">
          <span class="usage-count">${usageData.messagesUsed} / ${usageData.messagesLimit} messages</span>
          <span class="usage-percentage">${usageData.percentage}%</span>
        </div>
        <div class="progress-bar">
          <div class="progress-fill progress-${usageData.status || 'ok'}"
               style="width: ${usageData.percentage}%"></div>
        </div>
      </div>

      <div class="meta-info">
        ${usageData.planType ? `<span class="plan-type">${usageData.planType} Plan</span>` : '<span></span>'}
        ${usageData.resetTime ? `<span class="reset-time">Resets ${usageData.resetTime}</span>` : '<span></span>'}
      </div>
    ` : usageData && usageData.error ? `
      <div class="error-message">
        ${usageData.error}
      </div>
    ` : `
      <div class="empty-state">
        <p>No usage data available</p>
        <p><a href="${provider.urls.settings}" target="_blank">Visit ${provider.name} Settings</a></p>
      </div>
    `}

    <div class="provider-actions">
      <button class="btn btn-refresh" data-provider="${provider.id}">
        Refresh ${provider.name}
      </button>
    </div>
  `;

  return card;
}

/**
 * Load and display all providers
 */
async function loadAllProviders() {
  providersContainer.innerHTML = '<div class="loading">Loading usage data</div>';

  try {
    // Get all usage data from background script
    const response = await chrome.runtime.sendMessage({ type: 'GET_ALL_USAGE' });
    const allUsageData = response.data || {};

    // Clear loading state
    providersContainer.innerHTML = '';

    // Create cards for all providers
    for (const [providerId, provider] of Object.entries(LLM_PROVIDERS)) {
      if (!provider.enabled) continue;

      const usageData = allUsageData[providerId];
      const card = createProviderCard(provider, usageData);
      providersContainer.appendChild(card);
    }

    // If no providers enabled
    if (providersContainer.children.length === 0) {
      providersContainer.innerHTML = `
        <div class="empty-state">
          <p>No providers enabled</p>
        </div>
      `;
    }

    // Update last updated time
    updateLastUpdatedTime(allUsageData);

    // Add refresh button listeners
    document.querySelectorAll('.btn-refresh').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const providerId = e.target.dataset.provider;
        if (providerId) {
          refreshProvider(providerId);
        }
      });
    });

  } catch (error) {
    console.error('[LLM Tracker Popup] Error loading providers:', error);
    providersContainer.innerHTML = `
      <div class="error-message">
        Failed to load usage data: ${error.message}
      </div>
    `;
  }
}

/**
 * Refresh a specific provider
 */
async function refreshProvider(providerId) {
  console.log('[LLM Tracker Popup] Refreshing provider:', providerId);

  try {
    // Request refresh from background script
    await chrome.runtime.sendMessage({
      type: 'REFRESH_USAGE',
      provider: providerId
    });

    // Wait a bit for the content script to respond
    setTimeout(() => {
      loadAllProviders();
    }, 1500);

  } catch (error) {
    console.error('[LLM Tracker Popup] Error refreshing provider:', error);
  }
}

/**
 * Update the "last updated" timestamp
 */
function updateLastUpdatedTime(allUsageData) {
  let latestTimestamp = 0;

  for (const usageData of Object.values(allUsageData)) {
    if (usageData && usageData.timestamp > latestTimestamp) {
      latestTimestamp = usageData.timestamp;
    }
  }

  if (latestTimestamp > 0) {
    const date = new Date(latestTimestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) {
      lastUpdatedEl.textContent = 'Updated just now';
    } else if (diffMins < 60) {
      lastUpdatedEl.textContent = `Updated ${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    } else {
      const diffHours = Math.floor(diffMins / 60);
      lastUpdatedEl.textContent = `Updated ${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    }
  } else {
    lastUpdatedEl.textContent = 'Never updated';
  }
}

/**
 * Initialize popup
 */
function init() {
  console.log('[LLM Tracker Popup] Initializing...');

  // Load all providers on open
  loadAllProviders();

  // Refresh all button
  refreshAllBtn.addEventListener('click', () => {
    for (const [providerId, provider] of Object.entries(LLM_PROVIDERS)) {
      if (provider.enabled) {
        refreshProvider(providerId);
      }
    }
  });
}

// Start when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
