/**
 * LLM Provider Configurations
 *
 * This file defines all supported LLM providers.
 * Adding a new LLM is as simple as:
 * 1. Add config here
 * 2. Create content-scripts/{provider}.js
 * 3. Add to manifest.json content_scripts
 */

const LLM_PROVIDERS = {
  claude: {
    id: 'claude',
    name: 'Claude',
    type: 'chat',  // 'chat' or 'api'
    color: '#D97706',  // Amber
    urls: {
      settings: 'https://claude.ai/settings/usage',
      base: 'https://claude.ai'
    },
    defaultLimit: 45,  // Free tier default
    enabled: true
  },

  chatgpt: {
    id: 'chatgpt',
    name: 'ChatGPT',
    type: 'chat',
    color: '#10A37F',  // ChatGPT green
    urls: {
      settings: 'https://chatgpt.com/settings',
      base: 'https://chatgpt.com'
    },
    defaultLimit: 40,
    enabled: true,
    features: ['token-tracking', 'fetch-interception']  // Advanced tracking
  },

  openai: {
    id: 'openai',
    name: 'OpenAI API',
    type: 'api',
    color: '#412991',  // OpenAI purple
    urls: {
      settings: 'https://platform.openai.com/usage',
      base: 'https://platform.openai.com'
    },
    enabled: false  // Enable when ready
  },

  gemini: {
    id: 'gemini',
    name: 'Google Gemini',
    type: 'chat',
    color: '#4285F4',  // Google blue
    urls: {
      settings: 'https://gemini.google.com/settings',
      base: 'https://gemini.google.com'
    },
    defaultLimit: 50,
    enabled: false  // Enable when ready
  }
};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { LLM_PROVIDERS };
}
