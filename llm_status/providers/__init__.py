"""Provider adapters for various LLM services."""
from .base import ProviderAdapter, UsageData
from .openai import OpenAIAdapter
from .anthropic import AnthropicAdapter
from .gemini import GeminiAdapter
from .deepseek import DeepSeekAdapter

# Registry of all available providers
PROVIDERS = {
    "openai": OpenAIAdapter,
    "anthropic": AnthropicAdapter,
    "gemini": GeminiAdapter,
    "deepseek": DeepSeekAdapter,
}

__all__ = [
    "ProviderAdapter",
    "UsageData",
    "OpenAIAdapter",
    "AnthropicAdapter",
    "GeminiAdapter",
    "DeepSeekAdapter",
    "PROVIDERS",
]
