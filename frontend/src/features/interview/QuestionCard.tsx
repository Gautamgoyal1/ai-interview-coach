import type { InterviewQuestion } from "../../types/interview";
import {
  RotateCcwIcon,
  SquareIcon,
  Volume2Icon,
  VolumeXIcon,
} from "../../components/Icons";

export interface QuestionAudioProps {
  isSpeaking: boolean;
  isLoading: boolean;
  isMuted: boolean;
  onPlay: () => void;
  onStop: () => void;
  onToggleMute: () => void;
}

interface QuestionCardProps {
  question: InterviewQuestion;
  questionIndex: number;
  maxQuestions: number;
  audioProps?: QuestionAudioProps;
  voiceMode?: boolean;
}

function formatQuestionNumber(index: number, total: number): string {
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${pad(Math.max(1, index))} / ${pad(Math.max(1, total))}`;
}

function formatLabel(raw: string): string {
  if (!raw) return "";
  return raw.replace(/_/g, " ").replace(/\b\w/g, (ch) => ch.toUpperCase());
}

export default function QuestionCard({
  question,
  questionIndex,
  maxQuestions,
  audioProps,
}: QuestionCardProps) {
  const typeLabel = question.is_follow_up
    ? "Follow-up"
    : formatLabel(question.question_type);
  const difficultyLabel = formatLabel(question.difficulty);

  return (
    <section className="iv-question-panel" aria-live="polite">
      <div className="iv-question-body">
        <div className="iv-question-meta">
          <span className="iv-qnum-pill tabular-nums">
            {formatQuestionNumber(questionIndex, maxQuestions)}
          </span>
          <span className="iv-meta-topic">{question.topic}</span>
          {difficultyLabel && (
            <>
              <span className="iv-meta-dot" aria-hidden="true">
                ·
              </span>
              <span className="iv-meta-difficulty">{difficultyLabel}</span>
            </>
          )}
          {typeLabel && typeLabel !== difficultyLabel && (
            <>
              <span className="iv-meta-dot" aria-hidden="true">
                ·
              </span>
              <span className="iv-meta-type">{typeLabel}</span>
            </>
          )}
        </div>

        <h2 className="iv-question-text">{question.question_text}</h2>

        {audioProps && (
          <div className="iv-question-audio-bar">
            <div className="iv-audio-status">
              {audioProps.isLoading ? (
                <span className="iv-audio-pill loading">
                  <span
                    className="pm-spinner iv-audio-spinner"
                    aria-hidden="true"
                  />
                  <span>Preparing question audio...</span>
                </span>
              ) : audioProps.isSpeaking ? (
                <span className="iv-audio-pill active">
                  <span className="iv-audio-wave-bars" aria-hidden="true">
                    <span />
                    <span />
                    <span />
                  </span>
                  <span>Reading question</span>
                </span>
              ) : (
                <span className="iv-audio-pill idle">
                  <Volume2Icon size={14} />
                  <span>Question playback</span>
                </span>
              )}
            </div>

            <div className="iv-audio-actions">
              {audioProps.isSpeaking || audioProps.isLoading ? (
                <button
                  type="button"
                  className="btn btn-ghost btn-sm iv-audio-btn"
                  onClick={audioProps.onStop}
                  title="Stop AI speech"
                  aria-label={
                    audioProps.isLoading
                      ? "Cancel question audio"
                      : "Stop reading question"
                  }
                >
                  <SquareIcon size={13} />
                  <span>Stop</span>
                </button>
              ) : (
                <button
                  type="button"
                  className="btn btn-ghost btn-sm iv-audio-btn"
                  onClick={audioProps.onPlay}
                  disabled={audioProps.isLoading}
                  title="Replay question"
                  aria-label="Replay question"
                >
                  <RotateCcwIcon size={13} />
                  <span>Replay</span>
                </button>
              )}

              <button
                type="button"
                className={`btn btn-ghost btn-sm iv-audio-btn ${
                  audioProps.isMuted ? "muted" : ""
                }`}
                onClick={audioProps.onToggleMute}
                title={audioProps.isMuted ? "Unmute AI Voice" : "Mute AI Voice"}
                aria-label={
                  audioProps.isMuted ? "Unmute AI Voice" : "Mute AI Voice"
                }
                aria-pressed={audioProps.isMuted}
              >
                {audioProps.isMuted ? (
                  <VolumeXIcon size={14} />
                ) : (
                  <Volume2Icon size={14} />
                )}
                <span>{audioProps.isMuted ? "Muted" : "Mute"}</span>
              </button>
            </div>
          </div>
        )}
      </div>

      <p className="iv-question-guidance">
        {question.is_follow_up
          ? "Clarify or expand on your previous response in your own words."
          : "Take your time. Explain your understanding with an example."}
      </p>
    </section>
  );
}
