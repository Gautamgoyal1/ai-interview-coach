
import os

from .base import LLMError


def get_llm_provider(provider_name: str | None = None):
    """Return the configured LLM provider."""

    name = (
        provider_name
        or os.getenv("LLM_PROVIDER", "gemini")
    ).strip().lower()

    if name == "azure_openai":
        from .azure_openai import AzureOpenAIProvider
        return AzureOpenAIProvider()

    if name == "gemini":
        from .gemini import GeminiProvider
        return GeminiProvider()

    raise LLMError(f"Unsupported LLM provider: {name}")
