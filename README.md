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

## Quick Start

### 1. View Status for All Providers

```bash
llm-status status
```

**Example output:**

```
LLM Usage Status
================================================================================
+----------+--------------+------------+--------+---------------------+--------+
| Provider | Tokens Used  | Cost (USD) | Period | Last Updated        | Status |
+----------+--------------+------------+--------+---------------------+--------+
| OPENAI   | 197,000      | $2.01      | month  | 2025-01-15 10:30:45 | STUB   |
| ANTHROPIC| 123,000      | $0.78      | month  | 2025-01-15 10:30:45 | STUB   |
| GEMINI   | 140,000      | $0.69      | month  | 2025-01-15 10:30:45 | STUB   |
| DEEPSEEK | 85,000       | $0.02      | month  | 2025-01-15 10:30:45 | STUB   |
+----------+--------------+------------+--------+---------------------+--------+
```

### 2. View Detailed Usage for One Provider

```bash
llm-status usage openai
```

**Example output:**

```
Detailed Usage: OPENAI
==================================================
Provider           : OPENAI
Period             : month
Total Tokens       : 197,000
Prompt Tokens      : 145,000
Completion Tokens  : 52,000
Tokens Remaining   : N/A
Estimated Cost     : $2.01
Last Updated       : 2025-01-15 10:30:45
Quota Available    : Yes

Note: [STUB] Using mock data. Configure API key for real data.
==================================================
```

### 3. Add API Credentials

```bash
# Interactive mode (secure prompt)
llm-status add-cred openai

# Or provide directly
llm-status add-cred openai --api-key sk-...
```

Credentials are stored in `~/.llm-status/config.json`.

### 4. Force Refresh (Bypass Cache)

```bash
llm-status status --force-refresh
llm-status usage anthropic --force-refresh
```

### 5. Clear Cache

```bash
# Clear specific provider
llm-status clear-cache openai

# Clear all
llm-status clear-cache
```

## Tracking ChatGPT Web Usage

**NEW!** Since ChatGPT web doesn't have an API, `llm-status` can manually track your usage to warn you before hitting limits.

### Track Each Prompt

```bash
./llm-status track chatgpt-web
```

### Check Your Status

```bash
./llm-status track-status chatgpt-web
```

**Example output:**
```
CHATGPT-WEB
  Used:       36/40 prompts (90.0%)
  Remaining:  4 prompts
  Period:     3 hours
  Next Reset: 2025-12-08 19:43:46
  Status:     ⚠ WARNING - Low remaining!
```

### Quick Commands

```bash
# Track multiple prompts at once
./llm-status track chatgpt-web --count 5

# View all tracked services
./llm-status track-status

# Set custom limit (e.g., ChatGPT Plus)
./llm-status set-limit chatgpt-web 80 3

# Reset counter
./llm-status reset-tracker chatgpt-web
```

**See [CHATGPT_TRACKING.md](CHATGPT_TRACKING.md) for detailed guide and tips!**

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

**Step 1 (Current):** Status & Usage Checker
- ✓ Multi-provider support
- ✓ Caching layer
- ✓ CLI interface
- ⧗ Real API integration (stub implementations)

**Step 2 (Future):** Usage Optimizers
- Cost optimization recommendations
- Token usage analytics
- Provider comparison
- Alert system for quota limits

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
