
"""Tests for the LLM provider factory."""

import pytest

from app.integrations.llm.base import LLMError
from app.integrations.llm.factory import get_llm_provider


def test_azure_provider_is_selected(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "azure_openai")

    provider = get_llm_provider()

    assert provider.name == "azure_openai"


def test_gemini_provider_is_selected(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "gemini")

    provider = get_llm_provider()

    assert provider.name == "gemini"


def test_explicit_provider_name_overrides_environment(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "gemini")

    provider = get_llm_provider("azure_openai")

    assert provider.name == "azure_openai"


def test_unsupported_provider_raises_error(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "unsupported_provider")

    with pytest.raises(
        LLMError,
        match="Unsupported LLM provider",
    ):
        get_llm_provider()
