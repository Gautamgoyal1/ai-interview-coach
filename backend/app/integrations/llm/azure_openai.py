
from openai import (
    AsyncOpenAI,
    APIConnectionError,
    APIStatusError,
    RateLimitError as OpenAIRateLimitError,
)

from app.core.config import settings
from .base import LLMProvider, LLMError, RateLimitError


class AzureOpenAIProvider(LLMProvider):
    """LLM provider using Azure AI Foundry's OpenAI Responses API."""

    name = "azure_openai"

    def __init__(self):
        if not settings.azure_openai_api_key:
            raise LLMError("AZURE_OPENAI_API_KEY is not configured")

        if not settings.azure_openai_endpoint:
            raise LLMError("AZURE_OPENAI_ENDPOINT is not configured")

        if not settings.azure_openai_model or not settings.azure_openai_model.strip():
            raise LLMError("AZURE_OPENAI_MODEL is not configured")

        # Accept either the base URL or the full /responses endpoint.
        endpoint = settings.azure_openai_endpoint.strip().rstrip("/")

        if endpoint.endswith("/openai/v1/responses"):
            endpoint = endpoint[:-len("/responses")]
        elif not endpoint.endswith("/openai/v1"):
            endpoint += "/openai/v1"

        self.client = AsyncOpenAI(
            api_key=settings.azure_openai_api_key,
            base_url=endpoint + "/",
            timeout=settings.llm_timeout_seconds,
            max_retries=0,
        )

    async def generate(
        self,
        prompt: str,
        system: str | None = None,
        json_mode: bool = False,
    ) -> str:
        instructions = system or None

        if json_mode:
            instructions = (
                (instructions + "\n\n") if instructions else ""
            ) + "Return valid JSON only, without Markdown fences."

        try:
            response = await self.client.responses.create(
                model=settings.azure_openai_model,
                instructions=instructions,
                input=prompt,
                max_output_tokens=4000,
            )
            return response.output_text

        except OpenAIRateLimitError as exc:
            raise RateLimitError(
                "Azure OpenAI rate limit or quota reached"
            ) from exc

        except APIConnectionError as exc:
            raise LLMError(
                f"Network problem talking to Azure OpenAI: {exc}"
            ) from exc

        except APIStatusError as exc:
            raise LLMError(
                f"Azure OpenAI returned HTTP {exc.status_code}: "
                f"{str(exc)[:300]}"
            ) from exc
