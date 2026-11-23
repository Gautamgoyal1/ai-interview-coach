import { type FormEvent, type KeyboardEvent, useEffect, useRef } from "react";
import {
  ArrowRightIcon,
  CodeIcon,
  MicIcon,
  SquareIcon,
  XIcon,
} from "../../components/Icons";
import type {
  InterviewInputMode,
  VoiceInterviewState,
} from "../../types/speech";

interface AnswerBoxProps {
  questionId: string;
  answer: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  submitting: boolean;
  disabled: boolean;
  // Voice Interview controls
  inputMode?: InterviewInputMode;
  onSwitchMode?: (mode: InterviewInputMode) => void;
  voiceState?: VoiceInterviewState;
  interimText?: string;
  voiceError?: string | null;
  onClearVoiceError?: () => void;
  onStartRecording?: () => void;
  onStopRecording?: () => void;
}

export default function AnswerBox({
  questionId,
  answer,
  onChange,
  onSubmit,
  submitting,
  disabled,
  inputMode = "text",
  onSwitchMode,
  voiceState = "ready",
  interimText = "",
  voiceError,
  onClearVoiceError,
  onStartRecording,
  onStopRecording,
}: AnswerBoxProps) {
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  useEffect(() => {
    if (!disabled && textareaRef.current && inputMode === "text") {
      textareaRef.current.focus({ preventScroll: true });
    }
  }, [questionId, disabled, inputMode]);

  const trimmedLength = answer.trim().length;
  const wordCount = trimmedLength === 0 ? 0 : answer.trim().split(/\s+/).length;
  const isListening = voiceState === "listening";
  const isAiSpeaking = voiceState === "ai_speaking";
  const isTransitioning =
    voiceState === "starting" || voiceState === "stopping";

  function canSubmit() {
    return (
      !disabled &&
      !submitting &&
      !isListening &&
      !isTransitioning &&
      trimmedLength > 0
    );
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (isListening && onStopRecording) {
      onStopRecording();
      return;
    }
    if (!canSubmit()) return;
    onSubmit();
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
      event.preventDefault();
      if (canSubmit()) {
        onSubmit();
      }
    }
  }

  return (
    <form
      className="iv-answer-panel"
      data-voice-state={inputMode === "voice" ? voiceState : "text"}
      onSubmit={handleSubmit}
      aria-busy={submitting}
    >
      <div className="iv-response-heading">
        <h2>{inputMode === "voice" ? "Your transcript" : "Your response"}</h2>
        <span>Draft - not saved until submitted</span>
      </div>
      {/* Header with Mode Toggle & Status Indicator */}
      <div className="iv-answer-header">
        <div className="iv-answer-mode-toggle">
          {onSwitchMode ? (
            <div
              className="iv-mode-pill-group"
              role="group"
              aria-label="Input Mode"
            >
              <button
                type="button"

                aria-pressed={inputMode === "voice"}
                className={`iv-mode-pill ${inputMode === "voice" ? "active" : ""}`}
                onClick={() => onSwitchMode("voice")}
              >
                <MicIcon size={14} />
                <span>Voice</span>
              </button>
              <button
                type="button"

                aria-pressed={inputMode === "text"}
                className={`iv-mode-pill ${inputMode === "text" ? "active" : ""}`}
                onClick={() => onSwitchMode("text")}
              >
                <CodeIcon size={14} />
                <span>Text</span>
              </button>
            </div>
          ) : (
            <label htmlFor="interview-answer" className="iv-answer-label">
              Your response
            </label>
          )}
        </div>

        {/* State Badge for Voice Mode */}
        {inputMode === "voice" && (
          <div className="iv-voice-state-indicator" role="status">
            {isTransitioning && (
              <span className="badge badge-neutral">
                {voiceState === "starting"
                  ? "Connecting microphone"
                  : "Processing final transcript"}
              </span>
            )}
            {isAiSpeaking && (
              <span className="badge badge-accent">
                <span className="iv-status-dot ai-speaking" />
                <span>Listening to question</span>
              </span>
            )}
            {isListening && (
              <span className="badge badge-recording">
                <span className="iv-status-dot listening" />
                <span>Recording answer</span>
              </span>
            )}
            {voiceState === "review" && (
              <span className="badge badge-success">
                <span>Transcript Review</span>
              </span>
            )}
            {voiceState === "ready" && (
              <span className="badge badge-neutral">
                <span>Ready to speak</span>
              </span>
            )}
            {voiceState === "submitting" && (
              <span className="badge badge-accent">
                <span className="pm-spinner iv-badge-spinner" />
                <span>Submitting</span>
              </span>
            )}
          </div>
        )}
      </div>

      {/* Voice Error Banner */}
      {inputMode === "voice" && voiceError && (
        <div className="pm-alert-error iv-voice-alert" role="alert">
          <span>{voiceError}</span>
          <div className="iv-voice-alert-actions">
            {onSwitchMode && (
              <button
                type="button"
                className="btn btn-sm btn-ghost"
                onClick={() => onSwitchMode("text")}
              >
                Switch to Text Mode
              </button>
            )}
            {onClearVoiceError && (
              <button
                type="button"
                className="banner-dismiss"
                onClick={onClearVoiceError}
                aria-label="Dismiss error"
              >
                <XIcon size={14} />
              </button>
            )}
          </div>
        </div>
      )}

      {/* Primary Voice Action Bar (when in Voice Mode) */}
      {inputMode === "voice" && (
        <div className="iv-voice-action-bar">
          {isTransitioning ? (
            <div role="status">
              <p>
                {voiceState === "starting"
                  ? "Connecting microphone..."
                  : "Finishing transcription. Please wait..."}
              </p>
              {voiceState === "starting" && (
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={onStopRecording}
                >
                  Cancel microphone
                </button>
              )}
            </div>
          ) : isAiSpeaking ? (
            <div className="iv-voice-speaking-notice">
              <span className="pm-spinner iv-audio-spinner" />
              <span>
                AI is reading the question. Recording is disabled until
                finished.
              </span>
            </div>
          ) : isListening ? (
            <button
              type="button"
              className="btn iv-record-btn active"
              onClick={onStopRecording}
              aria-label="Stop recording answer"
            >
              <SquareIcon size={16} />
              <span>Stop & Review Transcript</span>
            </button>
          ) : (
            <button
              type="button"
              className={`btn ${answer.trim() ? "btn-secondary" : "btn-primary"} iv-record-btn idle`}
              onClick={onStartRecording}
              disabled={disabled || submitting}
              aria-label="Start recording answer"
            >
              <MicIcon size={18} />
              <span>
                {answer.trim()
                  ? "Record More (Continue Answer)"
                  : "Start Speaking Answer"}
              </span>
            </button>
          )}

          <p className="iv-voice-help-text">
            {isListening
              ? "Speak continuously at a natural pace. Sentences transcribe automatically in real-time."
              : isAiSpeaking
                ? "Listen to the question, or stop playback above when you are ready."
                : "Start recording when ready. Stop to review the final transcript, then submit separately."}
          </p>
        </div>
      )}

      {/* Live Interim Speech Preview (shown while user is actively speaking) */}
      {inputMode === "voice" && isListening && interimText && (
        <div className="iv-interim-preview" aria-live="polite">
          <span className="iv-interim-tag">Live:</span>
          <span className="iv-interim-body">{interimText}</span>
        </div>
      )}

      {/* Main Answer Area (Transcribed or Typed) */}
      <div className="iv-textarea-wrap">
        <textarea
          ref={textareaRef}
          id="interview-answer"
          aria-label="Your answer"
          className="iv-answer-textarea"
          value={answer}
          onChange={(event) => onChange(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={
            inputMode === "voice"
              ? "Your spoken answer will appear here in real time. You can edit, format, or type changes directly..."
              : "Write your answer here..."
          }
          disabled={disabled || submitting || isTransitioning || isListening}
          maxLength={10000}
          aria-describedby="interview-answer-status interview-draft-note"
        />
        {inputMode === "voice" && answer.trim().length > 0 && (
          <div className="iv-transcript-edit-notice">
            <span>
              Review the final words and edit your transcript before submitting.
            </span>
          </div>
        )}
      </div>

      <p id="interview-draft-note" className="iv-draft-note">
        {inputMode === "voice" && isListening
          ? "Recording in progress. Stop & Review to edit your answer."
          : inputMode === "voice" && voiceState === "stopping"
            ? "Waiting for final speech segments. Your answer will be editable when ready."
            : "Your answer stays on this page only until you submit. Leaving or refreshing discards it."}
      </p>
      {/* Footer with Word Count and Submit Button */}
      <div className="iv-answer-footer">
        <div className="iv-answer-footer-left">
          <span
            id="interview-answer-status"
            className="iv-answer-status tabular-nums"
            aria-live="polite"
          >
            {submitting
              ? "Evaluating response..."
              : wordCount > 0
                ? `${wordCount} ${wordCount === 1 ? "word" : "words"}`
                : ""}
          </span>
          <span className="iv-answer-shortcut">
            {inputMode === "voice"
              ? "Ctrl/Cmd + Enter to submit"
              : "Ctrl/Cmd + Enter to submit"}
          </span>
        </div>

        <button
          type="submit"
          className="btn btn-primary iv-submit-btn"
          disabled={!canSubmit()}
        >
          {submitting && (
            <span className="pm-spinner iv-btn-spinner" aria-hidden="true" />
          )}
          <span>{submitting ? "Submitting..." : "Submit answer"}</span>
          {!submitting && <ArrowRightIcon size={15} />}
        </button>
      </div>
    </form>
  );
}
