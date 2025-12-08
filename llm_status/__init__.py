"""LLM Status & Usage Checker - Track token usage across multiple LLM providers."""

__version__ = "0.1.0"
__author__ = "LLM Status Contributors"
__license__ = "AGPL-3.0"

from .cli import CLI, main

__all__ = ["CLI", "main", "__version__"]
