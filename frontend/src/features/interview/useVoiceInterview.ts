import { useCallback, useEffect, useRef, useState } from "react";
import * as SpeechSDK from "microsoft-cognitiveservices-speech-sdk";
import type { InterviewInputMode, VoiceInterviewState } from "../../types/speech";
import { getSpeechToken, invalidateSpeechToken, synthesizeSpeechAudio } from "../../services/speech.service";

interface UseVoiceInterviewOptions {
  questionText?: string;
  questionId?: string;
  interviewType?: "technical" | "hr";
  initialMode?: InterviewInputMode;
  answerText: string;
  onAnswerChange: (text: string) => void;
  submitting?: boolean;
}

interface Recording {
  abort: AbortController;
  stream?: MediaStream;
  audio?: SpeechSDK.AudioConfig;
  recognizer?: SpeechSDK.SpeechRecognizer;
  stopping?: Promise<void>;
  resolveStop?: () => void;
  refreshTimer?: ReturnType<typeof setTimeout>;
  expiryTimer?: ReturnType<typeof setTimeout>;
  stopTimer?: ReturnType<typeof setTimeout>;
  startTimer?: ReturnType<typeof setTimeout>;
}

export function useVoiceInterview({ questionText, questionId, interviewType = "technical",
  initialMode = "text", answerText, onAnswerChange, submitting = false }: UseVoiceInterviewOptions) {
  const [inputMode, setInputMode] = useState<InterviewInputMode>(initialMode);
  const [voiceState, setVoiceState] = useState<VoiceInterviewState>("ready");
  const [interimText, setInterimText] = useState("");
  const [isMuted, setIsMuted] = useState(false);
  const [micPermission, setMicPermission] = useState<"prompt" | "granted" | "denied">("prompt");
  const [voiceError, setVoiceError] = useState<string | null>(null);
  const [isAudioLoading, setIsAudioLoading] = useState(false);
  const recording = useRef<Recording | null>(null);
  const playback = useRef<{ abort: AbortController; audio?: HTMLAudioElement; url?: string } | null>(null);
  const modeRef = useRef(inputMode);
  const mutedRef = useRef(isMuted);
  const mounted = useRef(true);
  const answerRef = useRef(answerText);
  const changeRef = useRef(onAnswerChange);
  const submittingRef = useRef(submitting);
  answerRef.current = answerText;
  changeRef.current = onAnswerChange;
  submittingRef.current = submitting;

  const stopQuestionAudio = useCallback(() => {
    const old = playback.current;
    playback.current = null; // Invalidate callbacks before releasing resources.
    old?.abort.abort();
    if (old?.audio) {
      old.audio.onplay = old.audio.onended = old.audio.onerror = null;
      old.audio.pause();
      old.audio.removeAttribute("src");
      old.audio.load();
    }
    if (old?.url) URL.revokeObjectURL(old.url);
    if (mounted.current) {
      setIsAudioLoading(false);
      setVoiceState(prev => prev === "ai_speaking" ? "ready" : prev);
    }
  }, []);

  const releaseRecording = useCallback((session: Recording) => {
    if (recording.current === session) recording.current = null;
    session.abort.abort();
    clearTimeout(session.refreshTimer);
    clearTimeout(session.expiryTimer);
    clearTimeout(session.stopTimer);
    clearTimeout(session.startTimer);
    // Close this exact recognizer, never whatever a later recording created.
    try { session.recognizer?.close(); } catch { /* Already closed by SDK. */ }
    try { session.audio?.close(); } catch { /* Already closed by SDK. */ }
    session.stream?.getTracks().forEach(track => track.stop());
    session.resolveStop?.();
  }, []);

  const finishRecording = useCallback((session: Recording, error?: string) => {
    if (recording.current !== session) return;
    releaseRecording(session);
    if (mounted.current) {
      setInterimText("");
      setVoiceState("review");
      if (error) setVoiceError(error);
    }
  }, [releaseRecording]);

  const stopRecording = useCallback((): Promise<void> => {
    const session = recording.current;
    if (!session) return Promise.resolve();
    if (session.stopping) return session.stopping;
    if (!session.recognizer) {
      // Token/permission acquisition is still pending; any late stream is closed below.
      finishRecording(session);
      return Promise.resolve();
    }
    setVoiceState("stopping");
    session.stopping = new Promise(resolve => { session.resolveStop = resolve; });
    const completion = session.stopping;
    session.stopTimer = setTimeout(() => finishRecording(session,
      "Speech could not finish. Review your captured answer and add any missing words before submitting."), 15000);
    try {
      // SDK completion waits for final audio and the service turn completion. Keep
      // recognized handlers attached until then; interim text is never submitted.
      session.recognizer.stopContinuousRecognitionAsync(
        () => finishRecording(session),
        () => finishRecording(session, "Speech could not finish. Review your answer before submitting."),
      );
    } catch {
      finishRecording(session, "Speech could not finish. Review your answer before submitting.");
    }
    return completion;
  }, [finishRecording]);

  const playQuestionAudio = useCallback(async (_force = false) => {
    if (!questionText || modeRef.current !== "voice" || mutedRef.current || recording.current || submittingRef.current) return;
    stopQuestionAudio();
    const request = { abort: new AbortController(), audio: undefined as HTMLAudioElement | undefined, url: undefined as string | undefined };
    playback.current = request;
    setIsAudioLoading(true);
    setVoiceError(null);
    try {
      const blob = await synthesizeSpeechAudio(questionText, undefined, interviewType, request.abort.signal);
      if (playback.current !== request || !mounted.current) return;
      request.url = URL.createObjectURL(blob);
      request.audio = new Audio(request.url);
      request.audio.onplay = () => {
        if (playback.current === request) setVoiceState("ai_speaking");
      };
      request.audio.onended = () => { if (playback.current === request) stopQuestionAudio(); };
      request.audio.onerror = () => {
        if (playback.current !== request) return;
        stopQuestionAudio();
        setVoiceError("Unable to play interviewer audio. Replay or use Text Mode.");
      };
      await request.audio.play();
    } catch {
      if (playback.current === request && mounted.current) {
        stopQuestionAudio();
        setVoiceError("Interviewer audio is unavailable. Replay or use Text Mode.");
      }
    } finally {
      if (playback.current === request && mounted.current) setIsAudioLoading(false);
    }
  }, [questionText, interviewType, stopQuestionAudio]);

  const startRecording = useCallback(async () => {
    if (recording.current || modeRef.current !== "voice" || submittingRef.current) return;
    stopQuestionAudio(); // Also abort synthesis that has not returned yet.
    const session: Recording = { abort: new AbortController() };
    recording.current = session; // Guard rapid clicks before the first await.
    setVoiceState("starting");
    setVoiceError(null);
    setInterimText("");
    const current = () => mounted.current && recording.current === session;
    try {
      // Fetch first so token failure never opens the microphone.
      let token = await getSpeechToken(session.abort.signal);
      let tokenReceivedAt = Date.now();
      if (!current()) return;
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      if (!current()) {
        stream.getTracks().forEach(track => track.stop());
        return;
      }
      session.stream = stream;
      setMicPermission("granted");
      if ((Date.now() - tokenReceivedAt) / 1000 >= token.expires_in - 60) {
        token = await getSpeechToken(session.abort.signal);
        tokenReceivedAt = Date.now();
        if (!current()) return;
      }
      const config = SpeechSDK.SpeechConfig.fromAuthorizationToken(token.token, token.region);
      config.speechRecognitionLanguage = "en-US";
      // Reuse the one permission-granted stream; do not open a second microphone.
      session.audio = SpeechSDK.AudioConfig.fromStreamInput(stream);
      const recognizer = new SpeechSDK.SpeechRecognizer(config, session.audio);
      session.recognizer = recognizer;
      recognizer.recognizing = (_sender, event) => {
        if (current()) setInterimText(event.result.text || "");
      };
      recognizer.recognized = (_sender, event) => {
        if (!current() || event.result.reason !== SpeechSDK.ResultReason.RecognizedSpeech) return;
        const phrase = event.result.text.trim();
        if (!phrase) return;
        const updated = [answerRef.current.trim(), phrase].filter(Boolean).join(" ");
        answerRef.current = updated; // Consecutive SDK events can precede a React render.
        changeRef.current(updated);
        setInterimText("");
      };
      recognizer.canceled = () => {
        if (!current()) return;
        invalidateSpeechToken();
        finishRecording(session, "Speech recognition stopped. Review your captured answer or switch to Text Mode.");
      };
      recognizer.sessionStopped = () => {
        // Explicit stop is completed by its callback after final results drain.
        if (current() && !session.stopping) finishRecording(session);
      };
      const scheduleRenewal = (seconds: number) => {
        clearTimeout(session.refreshTimer);
        clearTimeout(session.expiryTimer);
        session.expiryTimer = setTimeout(() => finishRecording(session,
          "Speech authorization expired. Review your answer, then record again if needed."), Math.max(1, seconds) * 1000);
        session.refreshTimer = setTimeout(() => {
          void (async () => {
            try {
              const renewed = await getSpeechToken(session.abort.signal);
              if (!current()) return;
              recognizer.authorizationToken = renewed.token;
              scheduleRenewal(renewed.expires_in);
            } catch {
              if (current()) finishRecording(session,
                "Speech authorization could not be renewed. Review your answer before continuing.");
            }
          })();
        }, Math.max(1, seconds - 60) * 1000);
      };
      // Account for time spent waiting on the permission prompt.
      scheduleRenewal(token.expires_in - (Date.now() - tokenReceivedAt) / 1000);
      session.startTimer = setTimeout(() => finishRecording(session,
        "Speech connection timed out. Try recording again or switch to Text Mode."), 15000);
      recognizer.startContinuousRecognitionAsync(
        () => {
          if (current() && !session.stopping) {
            clearTimeout(session.startTimer);
            setVoiceState("listening");
            scheduleRenewal(token.expires_in - (Date.now() - tokenReceivedAt) / 1000);
          }
        },
        () => finishRecording(session, "Unable to start speech recognition. Try again or use Text Mode."),
      );
    } catch (error) {
      if (!current()) return;
      const denied = error instanceof Error && (error.name === "NotAllowedError" || error.name === "SecurityError");
      if (denied) setMicPermission("denied");
      finishRecording(session, denied
        ? "Microphone access was denied. Allow microphone access or switch to Text Mode."
        : "Speech is unavailable. Check your microphone and connection, or switch to Text Mode.");
    }
  }, [stopQuestionAudio, finishRecording]);

  const switchInputMode = useCallback((mode: InterviewInputMode) => {
    if (mode === modeRef.current) return;
    modeRef.current = mode;
    stopQuestionAudio();
    // Preserve finalized speech while an existing recognizer drains.
    void stopRecording();
    setInputMode(mode);
  }, [stopQuestionAudio, stopRecording]);

  const toggleMute = useCallback(() => {
    mutedRef.current = !mutedRef.current;
    setIsMuted(mutedRef.current);
    if (mutedRef.current) stopQuestionAudio();
  }, [stopQuestionAudio]);

  const prepareSubmission = useCallback(async (): Promise<string | null> => {
    stopQuestionAudio();
    if (recording.current) {
      await stopRecording();
      return null; // First action stops for review; a separate action submits.
    }
    return answerRef.current;
  }, [stopQuestionAudio, stopRecording]);

  useEffect(() => { switchInputMode(initialMode); }, [initialMode, switchInputMode]);
  useEffect(() => {
    // A changed question must never receive callbacks from the previous answer.
    if (recording.current) releaseRecording(recording.current);
    setInterimText("");
    setVoiceState("ready");
    return () => {
      if (recording.current) releaseRecording(recording.current);
      stopQuestionAudio();
    };
  }, [questionId, releaseRecording, stopQuestionAudio]);
  useEffect(() => {
    if (inputMode === "voice" && questionId && !isMuted) void playQuestionAudio();
    return stopQuestionAudio;
  }, [inputMode, questionId, isMuted, playQuestionAudio, stopQuestionAudio]);
  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
      if (recording.current) releaseRecording(recording.current);
      stopQuestionAudio();
    };
  }, [releaseRecording, stopQuestionAudio]);

  return { inputMode, switchInputMode, voiceState: submitting ? "submitting" as const : voiceState,
    interimText, isMuted, toggleMute, micPermission, voiceError, setVoiceError, isAudioLoading,
    playQuestionAudio, replayQuestionAudio: playQuestionAudio, stopQuestionAudio,
    startRecording, stopRecording, prepareSubmission };
}
