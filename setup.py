"""Setup script for llm-status."""
from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="llm-status",
    version="0.1.0",
    description="LLM Status & Usage Checker - Track token usage across multiple LLM providers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="LLM Status Contributors",
    author_email="",
    url="https://github.com/yourusername/llm-status",
    license="AGPL-3.0",
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=3.8",
    install_requires=[
        # Zero external dependencies for core functionality
        # All features work with Python standard library only
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
        "api": [
            # Optional: for real API implementations
            # "requests>=2.28.0",
            # "openai>=1.0.0",
            # "anthropic>=0.8.0",
            # "google-generativeai>=0.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "llm-status=llm_status.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    keywords="llm ai tokens usage tracking openai anthropic claude gemini deepseek",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/llm-status/issues",
        "Source": "https://github.com/yourusername/llm-status",
    },
)
