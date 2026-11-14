import { apiRequest, ApiError } from "./api";
import { getAccessToken } from "../utils/storage";
import type { SpeechTokenResponse, SpeechVoiceInfo } from "../types/speech";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000";

let cachedToken: SpeechTokenResponse | null = null;
let tokenExpiresAtMs = 0;
let tokenOwner: string | null = null;

/**
 * Fetch a short-lived Azure Speech authorization token.
 * Tokens are cached in-memory and proactively refreshed when < 60 seconds remain.
 */
export async function getSpeechToken(signal?: AbortSignal): Promise<SpeechTokenResponse> {
  const now = Date.now();
  const owner = getAccessToken();
  // If we have a cached token with > 60 seconds of validity remaining, reuse it
  if (cachedToken && tokenOwner === owner && now < tokenExpiresAtMs - 60_000) {
    return { ...cachedToken, expires_in: Math.floor((tokenExpiresAtMs - now) / 1000) };
  }

  const response = await apiRequest<SpeechTokenResponse>("/speech/token", {
    method: "POST",
    signal,
    cache: "no-store",
  });

  if (getAccessToken() !== owner || signal?.aborted) {
    throw new ApiError("Speech authorization changed. Please try again.", 401);
  }
  cachedToken = response;
  tokenOwner = owner;
  // expires_in is in seconds (typically 600s = 10 mins)
  tokenExpiresAtMs = now + response.expires_in * 1000;
  return response;
}

/**
 * Synthesize speech audio using Azure Neural TTS through the backend.
 * Returns an audio Blob (audio/mpeg) ready for native HTML5 Audio playback.
 */
export async function synthesizeSpeechAudio(
  text: string,
  voiceName?: string,
  interviewType?: "technical" | "hr",
  signal?: AbortSignal,
): Promise<Blob> {
  const token = getAccessToken();
  const headers = new Headers({
    "Content-Type": "application/json",
  });
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}/speech/synthesize`, {
    method: "POST",
    signal,
    cache: "no-store",
    headers,
    body: JSON.stringify({
      text,
      voice_name: voiceName,
      interview_type: interviewType,
    }),
  });

  if (!response.ok) {
    let message = `Speech synthesis failed (${response.status})`;
    try {
      const errData = await response.json();
      message = errData.detail || message;
    } catch {
      // fallback
    }
    throw new ApiError(message, response.status);
  }

  return response.blob();
}

/**
 * Get available Azure Speech neural voices.
 */
export async function getSpeechVoices(): Promise<SpeechVoiceInfo[]> {
  return apiRequest<SpeechVoiceInfo[]>("/speech/voices");
}

/**
 * Clear cached token (e.g. on logout or error).
 */
export function invalidateSpeechToken(): void {
  cachedToken = null;
  tokenExpiresAtMs = 0;
  tokenOwner = null;
}
