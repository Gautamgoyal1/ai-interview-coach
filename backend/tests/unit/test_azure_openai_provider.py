
import anyio
import pytest

from app.integrations.llm import azure_openai as azure_module
from app.integrations.llm.base import LLMError, RateLimitError


class FakeResponses:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.last_call = None

    async def create(self, **kwargs):
        self.last_call = kwargs

        if self.error is not None:
            raise self.error

        return self.response


class FakeClient:
    def __init__(self, responses):
        self.responses = responses


def configure_settings(
    monkeypatch,
    *,
    key="test-key",
    endpoint="https://example.services.ai.azure.com/openai/v1",
    model="test-model",
):
    monkeypatch.setattr(
        azure_module.settings,
        "azure_openai_api_key",
        key,
    )
    monkeypatch.setattr(
        azure_module.settings,
        "azure_openai_endpoint",
        endpoint,
    )
    monkeypatch.setattr(
        azure_module.settings,
        "azure_openai_model",
        model,
    )
    monkeypatch.setattr(
        azure_module.settings,
        "llm_timeout_seconds",
        12.0,
    )


def test_missing_api_key_raises_llm_error(monkeypatch):
    configure_settings(monkeypatch, key="")

    with pytest.raises(LLMError, match="API_KEY is not configured"):
        azure_module.AzureOpenAIProvider()


def test_missing_endpoint_raises_llm_error(monkeypatch):
    configure_settings(monkeypatch, endpoint="")

    with pytest.raises(LLMError, match="ENDPOINT is not configured"):
        azure_module.AzureOpenAIProvider()


@pytest.mark.parametrize("model", ["", "   "])
def test_missing_model_raises_llm_error(monkeypatch, model):
    configure_settings(monkeypatch, model=model)

    with pytest.raises(
        LLMError,
        match="AZURE_OPENAI_MODEL is not configured",
    ):
        azure_module.AzureOpenAIProvider()


@pytest.mark.parametrize(
    ("configured_endpoint", "expected_base_url"),
    [
        (
            "https://example.services.ai.azure.com/openai/v1",
            "https://example.services.ai.azure.com/openai/v1/",
        ),
        (
            "https://example.services.ai.azure.com/openai/v1/responses",
            "https://example.services.ai.azure.com/openai/v1/",
        ),
        (
            "https://example.services.ai.azure.com/",
            "https://example.services.ai.azure.com/openai/v1/",
        ),
    ],
)
def test_endpoint_normalization(
    monkeypatch,
    configured_endpoint,
    expected_base_url,
):
    configure_settings(monkeypatch, endpoint=configured_endpoint)
    captured = {}

    class Client:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr(azure_module, "AsyncOpenAI", Client)

    azure_module.AzureOpenAIProvider()

    assert captured["base_url"] == expected_base_url
    assert captured["api_key"] == "test-key"
    assert captured["timeout"] == 12.0
    assert captured["max_retries"] == 0


def test_generate_success_and_json_mode(monkeypatch):
    configure_settings(monkeypatch)

    responses = FakeResponses(
        response=type(
            "Response",
            (),
            {"output_text": '{"ok": true}'},
        )(),
    )

    monkeypatch.setattr(
        azure_module,
        "AsyncOpenAI",
        lambda **kwargs: FakeClient(responses),
    )

    provider = azure_module.AzureOpenAIProvider()

    result = anyio.run(
        provider.generate,
        "Return a JSON object",
        "You are a test assistant.",
        True,
    )

    assert result == '{"ok": true}'
    assert responses.last_call["model"] == "test-model"
    assert responses.last_call["input"] == "Return a JSON object"
    assert responses.last_call["instructions"] == (
        "You are a test assistant.\n\n"
        "Return valid JSON only, without Markdown fences."
    )
    assert responses.last_call["max_output_tokens"] == 4000


def test_rate_limit_is_translated_to_rate_limit_error(monkeypatch):
    configure_settings(monkeypatch)

    class FakeRateLimitError(Exception):
        pass

    monkeypatch.setattr(
        azure_module,
        "OpenAIRateLimitError",
        FakeRateLimitError,
    )

    responses = FakeResponses(
        error=FakeRateLimitError("rate limited"),
    )

    monkeypatch.setattr(
        azure_module,
        "AsyncOpenAI",
        lambda **kwargs: FakeClient(responses),
    )

    provider = azure_module.AzureOpenAIProvider()

    with pytest.raises(RateLimitError, match="rate limit or quota"):
        anyio.run(provider.generate, "Hello")


def test_connection_error_is_translated_to_llm_error(monkeypatch):
    configure_settings(monkeypatch)

    class FakeConnectionError(Exception):
        pass

    monkeypatch.setattr(
        azure_module,
        "APIConnectionError",
        FakeConnectionError,
    )

    responses = FakeResponses(
        error=FakeConnectionError("connection failed"),
    )

    monkeypatch.setattr(
        azure_module,
        "AsyncOpenAI",
        lambda **kwargs: FakeClient(responses),
    )

    provider = azure_module.AzureOpenAIProvider()

    with pytest.raises(LLMError, match="Network problem"):
        anyio.run(provider.generate, "Hello")


def test_http_status_error_is_translated_to_llm_error(monkeypatch):
    configure_settings(monkeypatch)

    class FakeStatusError(Exception):
        def __init__(self, status_code, message):
            super().__init__(message)
            self.status_code = status_code

    monkeypatch.setattr(
        azure_module,
        "APIStatusError",
        FakeStatusError,
    )

    responses = FakeResponses(
        error=FakeStatusError(500, "simulated server error"),
    )

    monkeypatch.setattr(
        azure_module,
        "AsyncOpenAI",
        lambda **kwargs: FakeClient(responses),
    )

    provider = azure_module.AzureOpenAIProvider()

    with pytest.raises(LLMError, match="HTTP 500"):
        anyio.run(provider.generate, "Hello")
