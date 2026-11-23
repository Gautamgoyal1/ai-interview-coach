import type { VoiceInterviewState } from "../../types/speech";
import { useLayoutEffect, useRef, useSyncExternalStore } from "react";
import type { VoiceActivity } from "./voiceActivity";
import HumanPortrait from "./HumanPortrait";
import "./ActiveSpeakerStage.css";

export type AvatarState = "idle" | "speaking" | "listening" | "thinking" | "muted" | "error";
interface ParticipantState {
  state: AvatarState;
  label: string;
}
const METER_THRESHOLDS = [0.08, 0.2, 0.4, 0.6, 0.8];
export interface ActiveSpeakerStageProps {
  voiceState: VoiceInterviewState;
  isMuted: boolean;
  isAudioLoading: boolean;
  processing?: boolean;
  voiceError?: string | null;
  microphoneLevel?: number | null;
  playbackLevel?: number | null;
  microphoneActivity?: VoiceActivity;
  playbackActivity?: VoiceActivity;
}

// Presentation only: no audio resources, timers, callbacks or interview actions.
export function getAvatarStates({
  voiceState, isMuted, isAudioLoading, processing, voiceError, microphoneLevel, playbackLevel,
}: ActiveSpeakerStageProps): { interviewer: ParticipantState; candidate: ParticipantState } {
  const interviewerReady: ParticipantState = isMuted
    ? { state: "muted", label: "Question audio muted" }
    : { state: "idle", label: "Ready when you are" };
  if (processing || voiceState === "submitting") {
    return {
      interviewer: { state: "thinking", label: "Processing your response" },
      candidate: { state: "thinking", label: "Please wait" },
    };
  }
  if (voiceState === "listening") {
    return {
      interviewer: { state: "listening", label: "Listening to you" },
      candidate: microphoneLevel != null && microphoneLevel >= 0.08
        ? { state: "speaking", label: "Voice activity · recording" }
        : { state: "listening", label: microphoneLevel == null ? "Recording · activity unavailable" : "Recording · waiting for speech" },
    };
  }
  if (voiceState === "starting" || voiceState === "stopping") {
    return {
      interviewer: { state: "listening", label: "Waiting for your answer" },
      candidate: {
        state: "thinking",
        label: voiceState === "starting" ? "Connecting microphone" : "Finalizing transcript",
      },
    };
  }
  // The hook exposes a shared voice error, not separate STT/TTS errors.
  // Avoid attributing a failure to a particular service or claiming a mic is active.
  if (voiceError) {
    return {
      interviewer: { state: "error", label: "Voice needs attention" },
      candidate: { state: "error", label: "Check voice controls below" },
    };
  }
  if (voiceState === "ai_speaking" && !isMuted) {
    return {
      interviewer: playbackLevel != null && playbackLevel >= 0.08
        ? { state: "speaking", label: "Speaking question" }
        : { state: "listening", label: "Question audio playing" },
      candidate: { state: "listening", label: "Listening to question" },
    };
  }
  if (isAudioLoading && !isMuted) {
    return {
      interviewer: { state: "thinking", label: "Preparing question audio" },
      candidate: { state: "idle", label: "Microphone off" },
    };
  }
  return {
    interviewer: interviewerReady,
    candidate: voiceState === "review"
      ? { state: "idle", label: "Review your transcript" }
      : { state: "idle", label: "Microphone off" },
  };
}

function Participant({ role, state, label, prominence, level, activity, canSpeak }: ParticipantState & {
  role: "interviewer" | "candidate";
  prominence: "main" | "secondary";
  level: number;
  activity?: VoiceActivity;
  canSpeak: boolean;
}) {
  const name = role === "interviewer" ? "AI interviewer" : "You";
  const meter = useRef<HTMLSpanElement>(null);
  const fallbackLevel = activity ? 0 : level;
  useLayoutEffect(() => {
    const marks = meter.current?.querySelectorAll("i");
    const paint = (sample: number | null) => {
      marks?.forEach((mark, index) => {
        const lit = String(canSpeak && sample != null && sample >= METER_THRESHOLDS[index]);
        if (mark.dataset.lit !== lit) mark.dataset.lit = lit;
      });
    };
    paint(activity ? activity.getLevel() : fallbackLevel);
    const unsubscribe = activity?.subscribeFrames(paint);
    return () => { unsubscribe?.(); paint(0); };
  }, [activity, fallbackLevel, canSpeak]);
  return (
    <div className="iv-avatar-person" role="group" aria-label={name}
      data-avatar-role={role} data-state={state} data-active={state === "speaking"}
      data-prominence={prominence}>
      <div className="iv-avatar-frame">
        <HumanPortrait role={role} />
      </div>
      <div className="iv-avatar-copy">
        <span className="iv-avatar-name">{name}</span>
        <span className="iv-avatar-status">{label}</span>
        {prominence === "main" && (
          <span ref={meter} className="iv-avatar-meter" aria-hidden="true" data-live={state === "speaking"}>
            {METER_THRESHOLDS.map(threshold => <i key={threshold} data-lit={!activity && state === "speaking" && level >= threshold} />)}
          </span>
        )}
      </div>
    </div>
  );
}

const noSubscription = () => () => {};
function useActivityStatus(activity: VoiceActivity | undefined, fallback: number | null | undefined) {
  return useSyncExternalStore(activity?.subscribe ?? noSubscription,
    activity?.getStatus ?? (() => fallback ?? null), activity?.getStatus ?? (() => fallback ?? null));
}

export default function ActiveSpeakerStage(props: ActiveSpeakerStageProps) {
  const microphoneLevel = useActivityStatus(props.microphoneActivity, props.microphoneLevel);
  const playbackLevel = useActivityStatus(props.playbackActivity, props.playbackLevel);
  const states = getAvatarStates({ ...props, microphoneLevel, playbackLevel });
  // Derived from the same lifecycle, never stored as separate speaker state.
  // Keep the candidate in focus while their final transcript is drained and reviewed.
  const candidateHasFloor = ["starting", "listening", "stopping", "review"].includes(props.voiceState);
  const interviewerHasFloor = states.interviewer.state === "speaking" || states.interviewer.state === "thinking";
  const mainRole = interviewerHasFloor || !candidateHasFloor ? "interviewer" : "candidate";
  const secondaryRole = mainRole === "interviewer" ? "candidate" : "interviewer";
  return (
    <div className="iv-avatar-stage" role="group" aria-label="Voice interview participants"
      data-main-speaker={mainRole}>
      <div className="iv-speaker-stage-heading"><span>Conversation</span><span>Avatar view</span></div>
      <div className="iv-speaker-stage-main">
        <Participant key={mainRole} role={mainRole} prominence="main" {...states[mainRole]}
          level={(mainRole === "interviewer" ? playbackLevel : microphoneLevel) ?? 0}
          activity={mainRole === "interviewer" ? props.playbackActivity : props.microphoneActivity}
          canSpeak={!props.processing && props.voiceState !== "submitting" && states[mainRole].state !== "error" &&
            (mainRole === "interviewer" ? props.voiceState === "ai_speaking" && !props.isMuted : props.voiceState === "listening")} />
      </div>
      <div className="iv-speaker-stage-secondary">
        <Participant key={secondaryRole} role={secondaryRole} prominence="secondary" {...states[secondaryRole]} level={0} canSpeak={false} />
      </div>
      <p className="iv-speaker-stage-caption">Static portraits · your camera is not in use</p>
    </div>
  );
}
