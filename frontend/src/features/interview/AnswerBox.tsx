import { type FormEvent, type KeyboardEvent, useEffect, useRef } from "react";
import { ArrowRightIcon } from "../../components/Icons";

interface AnswerBoxProps {
  questionId: string;
  answer: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  submitting: boolean;
  disabled: boolean;
}

export default function AnswerBox({
  questionId,
  answer,
  onChange,
  onSubmit,
  submitting,
  disabled,
}: AnswerBoxProps) {
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  useEffect(() => {
    if (!disabled && textareaRef.current) {
      textareaRef.current.focus({ preventScroll: true });
    }
  }, [questionId, disabled]);

  const trimmedLength = answer.trim().length;
  const wordCount = trimmedLength === 0 ? 0 : answer.trim().split(/\s+/).length;

  function canSubmit() {
    return !disabled && !submitting && trimmedLength > 0;
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
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
    <form className="iv-answer-panel" onSubmit={handleSubmit}>
      <div className="iv-answer-header">
        <label htmlFor="interview-answer" className="iv-answer-label">
          Your response
        </label>
        <span className="iv-answer-shortcut">Ctrl/Cmd + Enter to submit</span>
      </div>

      <textarea
        ref={textareaRef}
        id="interview-answer"
        className="iv-answer-textarea"
        value={answer}
        onChange={(event) => onChange(event.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Write your answer here..."
        disabled={disabled || submitting}
        maxLength={10000}
        aria-describedby="interview-answer-status"
      />

      <div className="iv-answer-footer">
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

        <button
          type="submit"
          className="btn btn-primary iv-submit-btn"
          disabled={!canSubmit()}
        >
          {submitting && <span className="pm-spinner iv-btn-spinner" aria-hidden="true" />}
          <span>{submitting ? "Submitting..." : "Submit answer"}</span>
          {!submitting && <ArrowRightIcon size={15} />}
        </button>
      </div>
    </form>
  );
}
