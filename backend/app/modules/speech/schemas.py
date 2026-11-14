from typing import Literal

from pydantic import BaseModel, Field, field_validator


SUPPORTED_VOICE_NAMES = frozenset({
    "en-US-JennyNeural", "en-US-AndrewNeural", "en-US-AriaNeural", "en-US-GuyNeural",
})


class SpeechTokenResponse(BaseModel):
    token: str = Field(..., description="Short-lived Azure Speech authorization token")
    region: str = Field(..., description="Azure resource region, e.g. eastasia")
    expires_in: int = Field(default=600, description="Token validity in seconds (10 minutes)")


class SpeechSynthesisRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="Text to synthesize")
    voice_name: str | None = Field(default=None, description="Optional Azure Neural Voice identifier")
    interview_type: Literal["technical", "hr"] | None = Field(default="technical", description="Interview type: technical or hr")

    @field_validator("voice_name")
    @classmethod
    def supported_voice(cls, value: str | None) -> str | None:
        if value is not None and value not in SUPPORTED_VOICE_NAMES:
            raise ValueError("Unsupported speech voice.")
        return value


class SpeechVoiceInfo(BaseModel):
    name: str
    display_name: str
    gender: str
    locale: str
    description: str
