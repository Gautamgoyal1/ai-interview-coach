import asyncio
import json

import httpx
import pytest

from app.integrations.llm import gemini


@pytest.mark.parametrize("json_mode", [False, True])
def test_output_is_bounded_in_text_and_json_modes(monkeypatch, json_mode):
    monkeypatch.setattr(gemini.settings, "gemini_api_key", "offline-test-key")
    payloads = []

    def handler(request):
        payloads.append(json.loads(request.content))
        return httpx.Response(200, json={"candidates": [{"content": {"parts": [{"text": "{}"}]}}]})

    real_client = httpx.AsyncClient
    monkeypatch.setattr(gemini.httpx, "AsyncClient", lambda **kwargs: real_client(transport=httpx.MockTransport(handler), **kwargs))
    result = asyncio.run(gemini.GeminiProvider().generate("bounded question", json_mode=json_mode))
    assert result == "{}"
    assert payloads[0]["generationConfig"]["maxOutputTokens"] == 4000
    assert payloads[0]["generationConfig"].get("responseMimeType") == ("application/json" if json_mode else None)
