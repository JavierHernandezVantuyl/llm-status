# LLM Status & Usage Checker

A minimal, terminal-first CLI tool to track token usage and costs across multiple LLM providers. Designed to run efficiently on weak computers with aggressive caching and minimal dependencies.

**License:** AGPL-3.0 (Free and Open Source)

## Features

- **Multi-provider support:** OpenAI, Anthropic (Claude), Google Gemini, DeepSeek
- **Manual web tracking:** Track ChatGPT/Claude web usage without APIs
- **Fast & lightweight:** Runs on weak PCs, uses local caching (15min TTL default)
- **Token tracking:** Total tokens, prompt/completion breakdown, remaining quotas
- **Cost estimation:** Automatic cost calculation based on provider pricing
- **Usage warnings:** Get alerts when approaching prompt limits
- **Zero waste:** Never calls model inference for status checks
- **Terminal-friendly:** Clean ASCII table output

## Supported Providers

| Provider | Status | Quota Support | Cost Estimation |
|----------|--------|---------------|-----------------|
| OpenAI   | ✓      | Limited       | ✓               |
| Anthropic| ✓      | Limited       | ✓               |
| Gemini   | ✓      | Limited       | ✓               |
| DeepSeek | ✓      | Limited       | ✓               |

**Note:** Current version (0.1.0) includes stub implementations that return mock data. Real API integration requires adding credentials and implementing provider-specific endpoints (see Implementation Guide below).

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Quick Install

```bash
# Clone the repository
git clone https://github.com/yourusername/llm-status.git
cd llm-status

# Install in development mode (use pip3 if pip is not available)
pip3 install -e .

# Make the CLI script executable
chmod +x llm-status
```

For minimal environments (weak PCs), you can install without optional dependencies:

```bash
pip3 install -e . --no-deps
# Then manually install only required dependencies
pip3 install setuptools  # Only if needed
```

### Running the CLI

You can run the CLI in two ways:

```bash
# Option 1: Direct script (recommended)
./llm-status status

# Option 2: Via Python module
python3 -m llm_status.cli status
```

**📖 See [QUICK_START.md](QUICK_START.md) for all commands and examples!**

## Quick Start

### First Time Setup

Run the interactive setup to add your API keys:

```bash
./llm-status setup
```

This will guide you through adding API keys for OpenAI, Anthropic, Gemini, and DeepSeek. You can skip any provider you don't use.

**Example setup flow:**

```
============================================================
  LLM Status & Usage Checker - Setup
============================================================

Welcome! Let's set up API keys for your LLM providers.
You can skip any provider by pressing Enter without typing.

------------------------------------------------------------

OpenAI
  Get your API key from: https://platform.openai.com/api-keys

  Enter API key (or press Enter to skip): ****
  ✓ API key saved for OpenAI

[... continues for other providers ...]

============================================================
Setup complete! Configured 2 provider(s).
============================================================

Next steps:
  • Run 'llm-status status' to see usage across all providers
  • Run 'llm-status usage <provider>' for detailed stats
```

### View Status for All Providers

```bash
./llm-status status
```

**Example output:**

```
LLM Usage Status
================
+-----------+-------------+---------------------+--------+
| Provider  | Tokens Used | Last Updated        | Status |
+-----------+-------------+---------------------+--------+
| OPENAI    | 197,000     | 2025-12-08 16:47:27 | OK     |
| ANTHROPIC | 123,000     | 2025-12-08 16:47:27 | OK     |
| GEMINI    | 140,000     | 2025-12-08 16:47:27 | OK     |
| DEEPSEEK  | 85,000      | 2025-12-08 16:47:27 | OK     |
+-----------+-------------+---------------------+--------+
```

**Optional:** Add `--show-cost` to see cost estimates:
```bash
./llm-status status --show-cost
```

### View Detailed Usage for One Provider

```bash
./llm-status usage anthropic
```

**Example output:**

```
Detailed Usage: ANTHROPIC
==================================================
Provider          : ANTHROPIC
Period            : month
Total Tokens      : 123,000
Prompt Tokens     : 89,000
Completion Tokens : 34,000
Tokens Remaining  : N/A
Last Updated      : 2025-12-08 16:47:27
Quota Available   : Yes
==================================================
```

**Optional:** Add `--show-cost` to see cost estimate:
```bash
./llm-status usage anthropic --show-cost
```

### Add/Update API Credentials

```bash
# Add a specific provider
./llm-status add-cred openai

# Or provide directly
./llm-status add-cred openai --api-key sk-...

# Or run setup again to update all
./llm-status setup
```

Credentials are stored in `~/.llm-status/config.json`.

### Force Refresh (Bypass Cache)

```bash
./llm-status status --force-refresh
./llm-status usage anthropic --force-refresh
```

### Clear Cache

```bash
# Clear specific provider
./llm-status clear-cache openai

# Clear all
./llm-status clear-cache
```

## Configuration

Configuration is stored in `~/.llm-status/config.json`:

```json
{
  "credentials": {
    "openai": {
      "api_key": "sk-..."
    },
    "anthropic": {
      "api_key": "sk-ant-..."
    }
  },
  "settings": {
    "cache_ttl_minutes": 15,
    "auto_update_hours": 24
  }
}
```

You can manually edit this file to adjust settings:
- `cache_ttl_minutes`: How long to cache usage data (default: 15)
- `auto_update_hours`: Background update frequency (default: 24, not yet implemented)

## Implementation Guide

### Current State (v0.1.0)

The current implementation uses **stub adapters** that return mock data. This allows you to:
- Test the CLI interface
- Understand expected data structures
- See formatting and caching behavior

### Adding Real Provider Integration

To implement real API integration, you need to:

#### 1. **OpenAI**

OpenAI provides usage data, but requires organization-level access. Two approaches:

**Option A: Track locally from API responses**
```python
# Monitor x-ratelimit headers in responses
# Store counts in local database
```

**Option B: Use usage endpoint (org-level)**
```python
# Uncomment code in llm_status/providers/openai.py
# GET https://api.openai.com/v1/usage
```

#### 2. **Anthropic (Claude)**

Anthropic includes usage in response headers but no dedicated billing API:

```python
# Parse x-api-usage header from API responses
# Example: {"input_tokens": 123, "output_tokens": 456}
# Accumulate in local tracker
```

See commented code in `llm_status/providers/anthropic.py`.

#### 3. **Google Gemini**

Gemini returns `usageMetadata` in API responses:

```python
# Parse response.usage_metadata
# Or use Google Cloud Billing API for paid tier
```

#### 4. **DeepSeek**

Check DeepSeek API documentation for usage endpoints:

```python
# Implement based on their API spec
# May have dedicated usage/billing endpoint
```

### Adding Dependencies for Real API Calls

If implementing real integrations, you may need:

```bash
pip install requests  # For HTTP calls (if using raw API)
# Or provider SDKs:
pip install openai anthropic google-generativeai
```

Update `setup.py` to include these as optional dependencies.

## Performance & Resource Usage

Designed for **weak computers**:

- **Memory:** ~20MB baseline (Python + minimal imports)
- **Disk:** <1MB for code, ~10KB for config/cache
- **Network:** Only calls provider APIs when cache expires
- **CPU:** Minimal, completes in <1 second with cached data

## Development

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=llm_status tests/

# Run specific test
python -m pytest tests/test_display.py -v
```

### Project Structure

```
llm-status/
├── llm_status/
│   ├── __init__.py          # Package entry point
│   ├── cli.py               # CLI interface
│   ├── config.py            # Config management
│   ├── cache.py             # Caching layer
│   ├── display.py           # Output formatting
│   └── providers/
│       ├── __init__.py      # Provider registry
│       ├── base.py          # Base adapter interface
│       ├── openai.py        # OpenAI adapter
│       ├── anthropic.py     # Anthropic adapter
│       ├── gemini.py        # Gemini adapter
│       └── deepseek.py      # DeepSeek adapter
├── tests/
│   ├── __init__.py
│   └── test_display.py      # Display tests
├── setup.py                 # Package setup
├── README.md               # This file
├── LICENSE                 # AGPL-3.0
└── .gitignore             # Python gitignore
```

### Adding New Providers

1. Create new adapter in `llm_status/providers/your_provider.py`
2. Inherit from `ProviderAdapter`
3. Implement `get_usage()` method
4. Register in `llm_status/providers/__init__.py`
5. Add tests

Example:

```python
from .base import ProviderAdapter, UsageData

class NewProviderAdapter(ProviderAdapter):
    @property
    def name(self) -> str:
        return "newprovider"

    def get_usage(self) -> UsageData:
        # Implement usage fetching
        return UsageData(...)
```

## Roadmap

**Step 1 (Current):** Status & Usage Checker ✓
- ✓ Multi-provider support (OpenAI, Anthropic, Gemini, DeepSeek)
- ✓ Caching layer with configurable TTL
- ✓ Interactive CLI with setup wizard
- ✓ Simplified, focused display (cost optional)
- ⧗ Real API integration (currently stub implementations)

**Step 2 (Planned):** Web Service Tracking
- Browser extension for automatic ChatGPT/Claude web usage tracking
- Real-time prompt counter in browser
- Alerts before hitting rate limits
- No manual tracking needed

**Step 3 (Future):** Usage Optimizers & Analytics
- Cost optimization recommendations
- Token usage analytics and trends
- Provider comparison and suggestions
- Alert system for quota limits
- Usage reports and insights

## Contributing

This is a free and open-source project under AGPL-3.0. Contributions welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

GNU Affero General Public License v3.0 (AGPL-3.0)

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

See LICENSE file for full details or visit: https://www.gnu.org/licenses/agpl-3.0.html

## Support

- **Issues:** https://github.com/yourusername/llm-status/issues
- **Documentation:** See this README
- **API Docs:** Coming soon

## Acknowledgments

Built for the LLM community to help track and optimize AI usage costs.
