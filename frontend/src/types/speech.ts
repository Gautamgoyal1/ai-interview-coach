export type InterviewInputMode = "text" | "voice";

export type VoiceInterviewState =
  | "ready"
  | "starting"
  | "stopping"
  | "ai_speaking"
  | "listening"
  | "review"
  | "submitting";

export interface SpeechTokenResponse {
  token: string;
  region: string;
  expires_in: number;
}

export interface SpeechVoiceInfo {
  name: string;
  display_name: string;
  gender: string;
  locale: string;
  description: string;
}
