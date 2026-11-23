import httpx

from app.core.config import settings
from .base import LLMProvider, LLMError, RateLimitError


class GeminiProvider(LLMProvider):
    name = "gemini"

    async def generate(self, prompt, system=None, json_mode=False):
        if not settings.gemini_api_key:
            raise LLMError("GEMINI_API_KEY is not set")

        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{settings.gemini_model}:generateContent"
        )
        body = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": 4000},
        }
        if system:
            body["systemInstruction"] = {"parts": [{"text": system}]}
        if json_mode:
            body["generationConfig"]["responseMimeType"] = "application/json"

        try:
            async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds) as client:
                r = await client.post(
                    url, json=body, headers={"x-goog-api-key": settings.gemini_api_key}
                )
        except httpx.HTTPError as e:
            raise LLMError(f"Network problem talking to Gemini: {e}") from e

        if r.status_code == 429:
            raise RateLimitError("Gemini rate limit or quota reached")
        if r.status_code != 200:
            raise LLMError(f"Gemini returned {r.status_code}: {r.text[:300]}")

        try:
            return r.json()["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, ValueError) as e:
            raise LLMError("Unexpected response shape from Gemini") from e
