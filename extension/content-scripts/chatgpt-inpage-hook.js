/**
 * ChatGPT In-Page Hook
 * Runs in page context to intercept network requests
 * Minimal capture layer - only metadata by default
 */

(function() {
  'use strict';

  console.log('[ChatGPT Hook] Initializing in-page interceptor...');

  // Configuration
  const CAPTURE_ENDPOINTS = {
    conversation: '/backend-api/conversation',
    completions: '/v1/chat/completions',
    moderations: '/backend-api/moderations'
  };

  const FALLBACK_CHARS_PER_TOKEN = 4;
  let captureCount = 0;

  /**
   * Fallback token estimation (chars / 4)
   * Will be replaced by tiktoken when loaded
   */
  function estimateTokensFallback(text) {
    if (!text || typeof text !== 'string') return 0;
    return Math.ceil(text.length / FALLBACK_CHARS_PER_TOKEN);
  }

  /**
   * Generate event hash for deduplication
   */
  function generateEventHash(data) {
    const str = JSON.stringify(data);
    let hash = 0;
    for (let i = 0; i < Math.min(str.length, 100); i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32bit integer
    }
    return Math.abs(hash).toString(36);
  }

  /**
   * Send captured data to content script
   */
  function sendToContentScript(eventType, data) {
    window.postMessage({
      type: 'CHATGPT_USAGE_EVENT',
      source: 'chatgpt-inpage-hook',
      eventType,
      data,
      timestamp: Date.now(),
      captureId: ++captureCount,
      tabId: window.name || 'unknown', // Will be set by content script
      eventHash: generateEventHash(data)
    }, '*');
  }

  /**
   * Extract message text from request body
   */
  function extractMessageFromRequest(body) {
    try {
      let bodyObj;

      if (typeof body === 'string') {
        bodyObj = JSON.parse(body);
      } else if (body instanceof FormData) {
        return null; // Skip FormData for now
      } else {
        bodyObj = body;
      }

      let messageText = '';

      // ChatGPT API structure
      if (bodyObj.messages && Array.isArray(bodyObj.messages)) {
        const lastMessage = bodyObj.messages[bodyObj.messages.length - 1];
        if (lastMessage && lastMessage.content) {
          if (typeof lastMessage.content === 'string') {
            messageText = lastMessage.content;
          } else if (Array.isArray(lastMessage.content)) {
            messageText = lastMessage.content.map(part => {
              if (typeof part === 'string') return part;
              if (part.text) return part.text;
              return '';
            }).join(' ');
          }
        }
      } else if (bodyObj.prompt) {
        messageText = bodyObj.prompt;
      }

      return messageText;

    } catch (error) {
      console.warn('[ChatGPT Hook] Failed to extract message:', error);
      return null;
    }
  }

  /**
   * Sanitize data - only keep metadata by default
   */
  function sanitizeCapture(messageText, model, conversationId) {
    const metadata = {
      conversationId: conversationId || 'unknown',
      model: model || 'gpt-3.5-turbo',
      timestamp: Date.now(),
      // Metadata only - no raw text unless opt-in
      promptLength: messageText ? messageText.length : 0,
      promptTokens: estimateTokensFallback(messageText || ''),
      // Will be updated with actual tiktoken count if available
    };

    return metadata;
  }

  /**
   * Monkey-patch fetch
   */
  const originalFetch = window.fetch;
  window.fetch = async function(...args) {
    const [resource, config] = args;
    const url = typeof resource === 'string' ? resource : resource.url;

    let shouldCapture = false;
    let endpoint = null;

    // Check if this is a chat endpoint
    for (const [key, path] of Object.entries(CAPTURE_ENDPOINTS)) {
      if (url.includes(path)) {
        shouldCapture = true;
        endpoint = key;
        break;
      }
    }

    // Call original fetch
    const response = await originalFetch.apply(this, args);

    // Capture if relevant
    if (shouldCapture && config && config.body) {
      try {
        const messageText = extractMessageFromRequest(config.body);

        if (messageText) {
          // Extract metadata
          let bodyObj;
          try {
            bodyObj = typeof config.body === 'string' ? JSON.parse(config.body) : config.body;
          } catch (e) {
            bodyObj = {};
          }

          const conversationId = bodyObj.conversation_id || bodyObj.conversationId || null;
          const model = bodyObj.model || 'gpt-3.5-turbo';

          const metadata = sanitizeCapture(messageText, model, conversationId);

          console.log('[ChatGPT Hook] Captured prompt:', {
            endpoint,
            model,
            tokens: metadata.promptTokens,
            length: metadata.promptLength
          });

          sendToContentScript('PROMPT_SENT', {
            endpoint,
            metadata,
            // Include raw text only if explicitly opted in (will be filtered by content script)
            _rawText: messageText
          });
        }
      } catch (error) {
        console.warn('[ChatGPT Hook] Capture error (non-critical):', error);
      }
    }

    // Handle streaming responses
    if (shouldCapture && response.body) {
      try {
        const reader = response.body.getReader();
        const stream = new ReadableStream({
          async start(controller) {
            let buffer = '';
            let totalResponseTokens = 0;

            while (true) {
              const { done, value } = await reader.read();

              if (done) {
                // Send final streaming stats
                if (totalResponseTokens > 0) {
                  sendToContentScript('STREAM_COMPLETE', {
                    endpoint,
                    responseTokens: totalResponseTokens
                  });
                }
                controller.close();
                break;
              }

              // Pass through the chunk
              controller.enqueue(value);

              // Parse SSE chunks for token counting
              const text = new TextDecoder().decode(value);
              buffer += text;

              const lines = buffer.split('\n');
              buffer = lines.pop() || '';

              for (const line of lines) {
                if (line.startsWith('data: ')) {
                  const data = line.substring(6);
                  if (data === '[DONE]') continue;

                  try {
                    const parsed = JSON.parse(data);
                    if (parsed.choices && parsed.choices[0]) {
                      const delta = parsed.choices[0].delta;
                      if (delta && delta.content) {
                        const tokens = estimateTokensFallback(delta.content);
                        totalResponseTokens += tokens;

                        // Send incremental update
                        sendToContentScript('STREAM_CHUNK', {
                          endpoint,
                          chunkTokens: tokens,
                          totalTokens: totalResponseTokens
                        });
                      }
                    }
                  } catch (e) {
                    // Skip invalid JSON
                  }
                }
              }
            }
          }
        });

        // Return modified response with new stream
        return new Response(stream, {
          status: response.status,
          statusText: response.statusText,
          headers: response.headers
        });

      } catch (error) {
        console.warn('[ChatGPT Hook] Stream capture error:', error);
      }
    }

    return response;
  };

  /**
   * Monkey-patch XMLHttpRequest
   */
  const originalXHRSend = XMLHttpRequest.prototype.send;
  XMLHttpRequest.prototype.send = function(body) {
    const xhr = this;

    // Check if this is a chat endpoint
    let shouldCapture = false;
    for (const path of Object.values(CAPTURE_ENDPOINTS)) {
      if (xhr._url && xhr._url.includes(path)) {
        shouldCapture = true;
        break;
      }
    }

    if (shouldCapture && body) {
      try {
        const messageText = extractMessageFromRequest(body);
        if (messageText) {
          console.log('[ChatGPT Hook] XHR captured:', messageText.substring(0, 50));
          sendToContentScript('XHR_PROMPT', {
            promptLength: messageText.length,
            promptTokens: estimateTokensFallback(messageText)
          });
        }
      } catch (error) {
        console.warn('[ChatGPT Hook] XHR capture error:', error);
      }
    }

    return originalXHRSend.apply(this, arguments);
  };

  // Store URL on XHR open
  const originalXHROpen = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function(method, url) {
    this._url = url;
    return originalXHROpen.apply(this, arguments);
  };

  /**
   * Monkey-patch WebSocket (for potential future use)
   */
  const originalWebSocket = window.WebSocket;
  window.WebSocket = function(url, protocols) {
    const ws = new originalWebSocket(url, protocols);

    // Intercept WebSocket messages if needed
    const originalSend = ws.send;
    ws.send = function(data) {
      // Could capture WebSocket data here if ChatGPT uses it
      return originalSend.apply(this, arguments);
    };

    return ws;
  };

  console.log('[ChatGPT Hook] ✓ Interceptors installed (fetch, XHR, WebSocket)');

  // Notify content script that hook is ready
  sendToContentScript('HOOK_READY', {
    version: '2.0',
    features: ['fetch', 'xhr', 'websocket', 'streaming']
  });

})();
