/**
 * ChatGPT Content Script
 * Coordinates between in-page hook and extension
 * Handles storage, deduplication, and UI
 */

(function() {
  'use strict';

  const PROVIDER_ID = 'chatgpt';
  const STORAGE_KEYS = {
    DAILY_USAGE: 'chatgpt_daily_usage',
    MONTHLY_USAGE: 'chatgpt_monthly_usage',
    MODEL_USAGE: 'chatgpt_model_usage',
    SETTINGS: 'chatgpt_settings',
    LAST_PROMPTS: 'chatgpt_last_prompts'
  };

  // Deduplication cache
  const seenEvents = new Set();
  const DEDUPE_WINDOW_MS = 5000; // 5 seconds

  // Streaming session tracking
  let currentStreamSession = null;

  // Settings with defaults
  let settings = {
    captureRawText: false, // Privacy: don't store raw text by default
    useTiktoken: true, // Use real tokenizer when available
    lightMode: false, // Skip heavy tokenization
    thresholds: {
      daily: { warning: 0.8, critical: 0.95 },
      monthly: { warning: 0.8, critical: 0.95 }
    },
    limits: {
      daily: 40, // Free tier estimate
      monthly: 1200 // Free tier estimate
    },
    notificationsEnabled: true
  };

  /**
   * Load settings from storage
   */
  async function loadSettings() {
    try {
      const result = await chrome.storage.local.get(STORAGE_KEYS.SETTINGS);
      if (result[STORAGE_KEYS.SETTINGS]) {
        settings = { ...settings, ...result[STORAGE_KEYS.SETTINGS] };
      }
    } catch (error) {
      console.error('[ChatGPT Content] Failed to load settings:', error);
    }
  }

  /**
   * Generate tab ID for deduplication
   */
  function getTabId() {
    if (!window.name) {
      window.name = 'tab_' + Date.now() + '_' + Math.random().toString(36).substring(7);
    }
    return window.name;
  }

  /**
   * Check if event is duplicate
   */
  function isDuplicate(eventHash, conversationId) {
    const key = `${conversationId}_${eventHash}`;

    if (seenEvents.has(key)) {
      return true;
    }

    seenEvents.add(key);

    // Clean up old entries after dedupe window
    setTimeout(() => {
      seenEvents.delete(key);
    }, DEDUPE_WINDOW_MS);

    return false;
  }

  /**
   * Get current date keys for storage
   */
  function getDateKeys() {
    const now = new Date();
    return {
      daily: now.toISOString().split('T')[0], // YYYY-MM-DD
      monthly: now.toISOString().substring(0, 7) // YYYY-MM
    };
  }

  /**
   * Load usage data from storage
   */
  async function loadUsageData() {
    try {
      const keys = getDateKeys();
      const result = await chrome.storage.local.get([
        STORAGE_KEYS.DAILY_USAGE,
        STORAGE_KEYS.MONTHLY_USAGE,
        STORAGE_KEYS.MODEL_USAGE
      ]);

      const dailyData = result[STORAGE_KEYS.DAILY_USAGE] || {};
      const monthlyData = result[STORAGE_KEYS.MONTHLY_USAGE] || {};
      const modelData = result[STORAGE_KEYS.MODEL_USAGE] || {};

      return {
        today: dailyData[keys.daily] || { promptTokens: 0, responseTokens: 0, messageCount: 0 },
        thisMonth: monthlyData[keys.monthly] || { promptTokens: 0, responseTokens: 0, messageCount: 0 },
        byModel: modelData
      };
    } catch (error) {
      console.error('[ChatGPT Content] Failed to load usage:', error);
      return {
        today: { promptTokens: 0, responseTokens: 0, messageCount: 0 },
        thisMonth: { promptTokens: 0, responseTokens: 0, messageCount: 0 },
        byModel: {}
      };
    }
  }

  /**
   * Save usage data to storage
   */
  async function saveUsageData(promptTokens, responseTokens, model, conversationId) {
    try {
      const keys = getDateKeys();
      const usage = await loadUsageData();

      // Update daily
      usage.today.promptTokens += promptTokens;
      usage.today.responseTokens += responseTokens;
      usage.today.messageCount += 1;

      // Update monthly
      usage.thisMonth.promptTokens += promptTokens;
      usage.thisMonth.responseTokens += responseTokens;
      usage.thisMonth.messageCount += 1;

      // Update by model
      if (!usage.byModel[model]) {
        usage.byModel[model] = { promptTokens: 0, responseTokens: 0, messageCount: 0 };
      }
      usage.byModel[model].promptTokens += promptTokens;
      usage.byModel[model].responseTokens += responseTokens;
      usage.byModel[model].messageCount += 1;

      // Save back to storage
      await chrome.storage.local.set({
        [STORAGE_KEYS.DAILY_USAGE]: { [keys.daily]: usage.today },
        [STORAGE_KEYS.MONTHLY_USAGE]: { [keys.monthly]: usage.thisMonth },
        [STORAGE_KEYS.MODEL_USAGE]: usage.byModel
      });

      console.log('[ChatGPT Content] Usage saved:', {
        daily: usage.today,
        monthly: usage.thisMonth
      });

      // Check thresholds
      await checkThresholds(usage);

      // Update UI
      await updateExtensionUI(usage);

    } catch (error) {
      console.error('[ChatGPT Content] Failed to save usage:', error);
    }
  }

  /**
   * Check thresholds and trigger notifications
   */
  async function checkThresholds(usage) {
    if (!settings.notificationsEnabled) return;

    const dailyPercentage = usage.today.messageCount / settings.limits.daily;
    const monthlyPercentage = usage.thisMonth.messageCount / settings.limits.monthly;

    // Check daily thresholds
    if (dailyPercentage >= settings.thresholds.daily.critical) {
      await showNotification('critical', 'Daily limit almost reached!',
        `You've used ${usage.today.messageCount}/${settings.limits.daily} messages today (${Math.round(dailyPercentage * 100)}%)`);
    } else if (dailyPercentage >= settings.thresholds.daily.warning) {
      await showNotification('warning', 'High daily usage',
        `You've used ${usage.today.messageCount}/${settings.limits.daily} messages today (${Math.round(dailyPercentage * 100)}%)`);
    }

    // Check monthly thresholds
    if (monthlyPercentage >= settings.thresholds.monthly.critical) {
      await showNotification('critical', 'Monthly limit almost reached!',
        `You've used ${usage.thisMonth.messageCount}/${settings.limits.monthly} messages this month`);
    }
  }

  /**
   * Show browser notification
   */
  async function showNotification(level, title, message) {
    try {
      await chrome.runtime.sendMessage({
        type: 'SHOW_NOTIFICATION',
        level,
        title,
        message
      });
    } catch (error) {
      console.error('[ChatGPT Content] Failed to show notification:', error);
    }
  }

  /**
   * Update extension UI (badge and popup)
   */
  async function updateExtensionUI(usage) {
    try {
      const dailyPercentage = (usage.today.messageCount / settings.limits.daily) * 100;
      const totalTokens = usage.today.promptTokens + usage.today.responseTokens;

      await chrome.runtime.sendMessage({
        type: 'USAGE_UPDATE',
        data: {
          provider: PROVIDER_ID,
          timestamp: Date.now(),
          success: true,
          messageCount: usage.today.messageCount,
          messagesUsed: usage.today.messageCount,
          messagesLimit: settings.limits.daily,
          messagesRemaining: settings.limits.daily - usage.today.messageCount,
          percentage: dailyPercentage.toFixed(1),
          totalTokens: totalTokens,
          promptTokens: usage.today.promptTokens,
          responseTokens: usage.today.responseTokens,
          status: dailyPercentage >= 95 ? 'critical' : dailyPercentage >= 80 ? 'warning' : 'ok',
          planType: 'free',
          windowHours: 24,
          // Monthly data
          monthlyMessageCount: usage.thisMonth.messageCount,
          monthlyTotalTokens: usage.thisMonth.promptTokens + usage.thisMonth.responseTokens,
          // By model
          byModel: usage.byModel
        }
      });
    } catch (error) {
      console.error('[ChatGPT Content] Failed to update UI:', error);
    }
  }

  /**
   * Handle prompt sent event
   */
  async function handlePromptSent(data) {
    const { metadata, _rawText } = data;

    console.log('[ChatGPT Content] Prompt captured:', {
      model: metadata.model,
      tokens: metadata.promptTokens,
      length: metadata.promptLength
    });

    // Save to last prompts (optional, for UI display)
    if (settings.captureRawText && _rawText) {
      await saveLastPrompt({
        text: _rawText.substring(0, 200), // Only first 200 chars
        tokens: metadata.promptTokens,
        model: metadata.model,
        timestamp: Date.now()
      });
    }

    // Start streaming session
    currentStreamSession = {
      conversationId: metadata.conversationId,
      model: metadata.model,
      promptTokens: metadata.promptTokens,
      responseTokens: 0,
      startTime: Date.now()
    };
  }

  /**
   * Handle stream chunk event
   */
  function handleStreamChunk(data) {
    if (currentStreamSession) {
      currentStreamSession.responseTokens = data.totalTokens;

      // Update UI in real-time
      console.log('[ChatGPT Content] Stream update:', {
        prompt: currentStreamSession.promptTokens,
        response: currentStreamSession.responseTokens
      });
    }
  }

  /**
   * Handle stream complete event
   */
  async function handleStreamComplete(data) {
    if (currentStreamSession) {
      const { promptTokens, responseTokens, model, conversationId } = currentStreamSession;

      console.log('[ChatGPT Content] Stream complete:', {
        prompt: promptTokens,
        response: responseTokens,
        total: promptTokens + responseTokens
      });

      // Save final usage
      await saveUsageData(promptTokens, responseTokens, model, conversationId);

      // Clear session
      currentStreamSession = null;
    }
  }

  /**
   * Save last prompt for UI display
   */
  async function saveLastPrompt(prompt) {
    try {
      const result = await chrome.storage.local.get(STORAGE_KEYS.LAST_PROMPTS);
      const prompts = result[STORAGE_KEYS.LAST_PROMPTS] || [];

      prompts.unshift(prompt);
      if (prompts.length > 10) prompts.pop(); // Keep last 10

      await chrome.storage.local.set({
        [STORAGE_KEYS.LAST_PROMPTS]: prompts
      });
    } catch (error) {
      console.error('[ChatGPT Content] Failed to save last prompt:', error);
    }
  }

  /**
   * Listen for messages from in-page hook
   */
  function listenForHookMessages() {
    window.addEventListener('message', async (event) => {
      // Only accept messages from same origin
      if (event.source !== window) return;

      const message = event.data;
      if (message.type !== 'CHATGPT_USAGE_EVENT') return;
      if (message.source !== 'chatgpt-inpage-hook') return;

      const { eventType, data, eventHash, timestamp } = message;

      // Deduplicate
      const conversationId = data.metadata?.conversationId || 'unknown';
      if (isDuplicate(eventHash, conversationId)) {
        console.log('[ChatGPT Content] Duplicate event ignored:', eventType);
        return;
      }

      // Handle different event types
      switch (eventType) {
        case 'HOOK_READY':
          console.log('[ChatGPT Content] ✓ Hook ready:', data.features);
          break;

        case 'PROMPT_SENT':
          await handlePromptSent(data);
          break;

        case 'STREAM_CHUNK':
          handleStreamChunk(data);
          break;

        case 'STREAM_COMPLETE':
          await handleStreamComplete(data);
          break;

        case 'XHR_PROMPT':
          // Handle XHR-based prompts (fallback)
          console.log('[ChatGPT Content] XHR prompt:', data);
          break;

        default:
          console.warn('[ChatGPT Content] Unknown event type:', eventType);
      }
    });

    console.log('[ChatGPT Content] ✓ Listening for hook messages');
  }

  /**
   * Inject in-page hook script
   */
  function injectHookScript() {
    const script = document.createElement('script');
    script.src = chrome.runtime.getURL('content-scripts/chatgpt-inpage-hook.js');
    script.onload = () => {
      console.log('[ChatGPT Content] ✓ Hook script injected');
      script.remove();
    };
    script.onerror = (error) => {
      console.error('[ChatGPT Content] Failed to inject hook:', error);
    };

    (document.head || document.documentElement).appendChild(script);
  }

  /**
   * Initialize
   */
  async function init() {
    console.log('[ChatGPT Content] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('[ChatGPT Content] Content script loaded');
    console.log('[ChatGPT Content] Version: 2.0 (Production-ready)');
    console.log('[ChatGPT Content] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

    // Set tab ID
    getTabId();

    // Load settings
    await loadSettings();
    console.log('[ChatGPT Content] Settings loaded:', settings);

    // Listen for messages from hook
    listenForHookMessages();

    // Inject hook script
    injectHookScript();

    // Load and send initial usage
    const usage = await loadUsageData();
    await updateExtensionUI(usage);

    // Listen for refresh requests from popup
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
      if (request.type === 'REQUEST_USAGE_UPDATE' && request.provider === PROVIDER_ID) {
        console.log('[ChatGPT Content] Refresh requested');
        loadUsageData().then(updateExtensionUI);
        sendResponse({ status: 'refreshed' });
      }
      return true;
    });
  }

  // Start when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
