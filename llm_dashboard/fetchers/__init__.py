"""LLM usage fetchers."""
from .base import BaseFetcher, LLMUsage
from .claude import ClaudeFetcher

# Registry of all available fetchers
FETCHERS = {
    "claude": ClaudeFetcher,
    # Future fetchers:
    # "openai": OpenAIFetcher,
    # "chatgpt-web": ChatGPTWebFetcher,
    # "gemini": GeminiFetcher,
}

__all__ = ["BaseFetcher", "LLMUsage", "ClaudeFetcher", "FETCHERS"]
