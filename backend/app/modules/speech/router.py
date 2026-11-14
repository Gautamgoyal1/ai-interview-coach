from fastapi import APIRouter, Depends, Response, status

from app.api.dependencies import get_current_user
from app.db.models.user import User
from app.modules.speech.schemas import (
    SpeechSynthesisRequest,
    SpeechTokenResponse,
    SpeechVoiceInfo,
)
from app.modules.speech.service import SpeechService


router = APIRouter(prefix="/speech", tags=["Speech"])
speech_service = SpeechService()


@router.post(
    "/token",
    response_model=SpeechTokenResponse,
    summary="Get short-lived Azure Speech authorization token",
)
async def get_speech_token(
    response: Response,
    current_user: User = Depends(get_current_user),
) -> SpeechTokenResponse:
    """Issue a 10-minute Azure Speech authorization token for browser client SDK.

    Protects master Azure subscription key from client exposure.
    Rate-limited per authenticated user.
    """
    response.headers["Cache-Control"] = "private, no-store"
    return await speech_service.get_speech_token(current_user.id)


@router.get(
    "/token",
    response_model=SpeechTokenResponse,
    summary="Get short-lived Azure Speech authorization token (GET)",
)
async def get_speech_token_get(
    response: Response,
    current_user: User = Depends(get_current_user),
) -> SpeechTokenResponse:
    """Alternative GET endpoint for fetching the short-lived Azure Speech authorization token."""
    response.headers["Cache-Control"] = "private, no-store"
    return await speech_service.get_speech_token(current_user.id)


@router.post(
    "/synthesize",
    summary="Synthesize text to speech using Azure Neural TTS",
)
async def synthesize_speech(
    request: SpeechSynthesisRequest,
    current_user: User = Depends(get_current_user),
) -> Response:
    """Synthesize text into high-fidelity neural MP3 audio on the server.

    Provides reliable, cross-browser audio playback for interview questions.
    """
    audio_content = await speech_service.synthesize_speech(
        user_id=current_user.id,
        text=request.text,
        voice_name=request.voice_name,
        interview_type=request.interview_type or "technical",
    )
    return Response(
        content=audio_content,
        media_type="audio/mpeg",
        headers={
            "Cache-Control": "private, no-store",
            "Content-Disposition": "inline; filename=question_audio.mp3",
        },
    )


@router.get(
    "/voices",
    response_model=list[SpeechVoiceInfo],
    summary="List available calibrated Azure Neural voices",
)
def get_voices(
    current_user: User = Depends(get_current_user),
) -> list[SpeechVoiceInfo]:
    """Return recommended voices for technical and HR interview scenarios."""
    return speech_service.get_available_voices()
