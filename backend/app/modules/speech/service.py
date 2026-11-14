import time
from collections import defaultdict, deque
import xml.sax.saxutils as saxutils

import httpx
from fastapi import HTTPException, status

from app.core.config import settings
from app.modules.speech.schemas import SUPPORTED_VOICE_NAMES, SpeechTokenResponse, SpeechVoiceInfo


# Recommended Azure Neural voices calibrated for technical & HR interview scenarios
RECOMMENDED_VOICES: list[SpeechVoiceInfo] = [
    SpeechVoiceInfo(
        name="en-US-JennyNeural",
        display_name="Jenny (Natural & Clear)",
        gender="Female",
        locale="en-US",
        description="Warm, clear, and professional tone suitable for both technical and behavioral prompts.",
    ),
    SpeechVoiceInfo(
        name="en-US-AndrewNeural",
        display_name="Andrew (Authoritative Tech Lead)",
        gender="Male",
        locale="en-US",
        description="Calm, articulate engineering lead voice ideal for system design and architecture questions.",
    ),
    SpeechVoiceInfo(
        name="en-US-AriaNeural",
        display_name="Aria (Conversational HR)",
        gender="Female",
        locale="en-US",
        description="Empathetic, engaging conversational voice ideal for HR and behavioral STAR scenarios.",
    ),
    SpeechVoiceInfo(
        name="en-US-GuyNeural",
        display_name="Guy (Executive Interviewer)",
        gender="Male",
        locale="en-US",
        description="Structured, measured pace suited for executive and senior technical interviews.",
    ),
]


class SpeechService:
    def __init__(self):
        # In-memory sliding window rate limiter: user_id -> deque of timestamps
        self._user_requests: dict[int, deque[float]] = defaultdict(deque)
        self._rate_limit_window = 60.0  # seconds
        self._max_requests_per_window = 30
        self._synthesis_requests: dict[int, deque[float]] = defaultdict(deque)
        self._max_synthesis_requests_per_window = 20
        self._last_pruned = 0.0

        # Azure tokens are resource-scoped; cache by region, never by browser user.
        self._token_cache: dict[str, tuple[str, float]] = {}

    def _check_rate_limit(self, user_id: int, *, synthesis: bool = False) -> None:
        now = time.monotonic()
        if now - self._last_pruned >= self._rate_limit_window:
            for buckets in (self._user_requests, self._synthesis_requests):
                for uid, requests in list(buckets.items()):
                    if not requests or requests[-1] <= now - self._rate_limit_window:
                        buckets.pop(uid, None)
            self._last_pruned = now
        buckets = self._synthesis_requests if synthesis else self._user_requests
        limit = self._max_synthesis_requests_per_window if synthesis else self._max_requests_per_window
        timestamps = buckets[user_id]
        while timestamps and timestamps[0] <= now - self._rate_limit_window:
            timestamps.popleft()

        if len(timestamps) >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many speech requests. Please wait before trying again.",
                headers={"Retry-After": str(max(1, int(self._rate_limit_window - (now - timestamps[0])) + 1))},
            )
        timestamps.append(now)

    def _get_credentials(self) -> tuple[str, str]:
        key = settings.azure_speech_key.strip()
        region = settings.azure_speech_region.strip() or "eastasia"
        if not key:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Azure AI Speech service is not configured on the backend.",
            )
        return key, region

    async def get_speech_token(self, user_id: int) -> SpeechTokenResponse:
        self._check_rate_limit(user_id)
        key, region = self._get_credentials()

        # Check in-memory cache (reuse token if > 120s remaining of its 600s lifetime)
        now = time.monotonic()
        cached = self._token_cache.get(region)
        if cached:
            cached_token, expire_at = cached
            if now < expire_at - 120:
                remaining = int(expire_at - now)
                return SpeechTokenResponse(token=cached_token, region=region, expires_in=remaining)

        token_url = f"https://{region}.api.cognitive.microsoft.com/sts/v1.0/issueToken"
        headers = {
            "Ocp-Apim-Subscription-Key": key,
            "Content-Type": "application/x-www-form-urlencoded",
        }

        async with httpx.AsyncClient(timeout=12.0) as client:
            try:
                response = await client.post(token_url, headers=headers)
            except httpx.HTTPError as exc:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Speech authorization is temporarily unavailable. Please try again.",
                ) from exc

        if response.status_code != 200 or not response.text.strip():
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Speech authorization is temporarily unavailable. Please try again.",
            )

        token = response.text.strip()
        # Azure STS tokens are valid for 10 minutes (600 seconds)
        expire_at = now + 600
        self._token_cache[region] = (token, expire_at)

        return SpeechTokenResponse(token=token, region=region, expires_in=600)

    async def synthesize_speech(
        self,
        *,
        user_id: int,
        text: str,
        voice_name: str | None = None,
        interview_type: str = "technical",
    ) -> bytes:
        self._check_rate_limit(user_id, synthesis=True)
        key, region = self._get_credentials()

        # Default voice selection based on interview type
        if not voice_name:
            if interview_type.lower() == "hr":
                voice_name = "en-US-AriaNeural"
            else:
                voice_name = "en-US-JennyNeural"

        if voice_name not in SUPPORTED_VOICE_NAMES:
            raise HTTPException(status_code=422, detail="Unsupported speech voice.")

        # Escape XML entities for SSML safety
        escaped_text = saxutils.escape(text)

        ssml = (
            f"<speak version='1.0' xml:lang='en-US'>"
            f"<voice name={saxutils.quoteattr(voice_name)}>"
            f"<prosody rate='0.98' pitch='0%'>{escaped_text}</prosody>"
            f"</voice>"
            f"</speak>"
        )

        tts_url = f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1"
        headers = {
            "Ocp-Apim-Subscription-Key": key,
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "audio-16khz-128kbitrate-mono-mp3",
            "User-Agent": "PrepMateInterviewCoach/1.0",
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            try:
                response = await client.post(tts_url, headers=headers, content=ssml.encode("utf-8"))
            except httpx.HTTPError as exc:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Interviewer audio is temporarily unavailable. Please try again.",
                ) from exc

        if response.status_code != 200 or not response.content:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Interviewer audio is temporarily unavailable. Please try again.",
            )

        return response.content

    def get_available_voices(self) -> list[SpeechVoiceInfo]:
        return RECOMMENDED_VOICES
