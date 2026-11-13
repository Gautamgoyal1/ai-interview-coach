interface ProgressBarProps {
  questionIndex: number;
  maxQuestions: number;
  isFollowUp: boolean;
  answeredCount: number;
}

export default function ProgressBar({
  questionIndex,
  maxQuestions,
  isFollowUp,
  answeredCount,
}: ProgressBarProps) {
  const safeMax = Math.max(maxQuestions, 1);
  const clamped = Math.max(1, Math.min(safeMax, questionIndex));
  const percent = Math.round((clamped / safeMax) * 100);

  return (
    <section className="iv-progress" aria-label="Interview progress">
      <div className="iv-progress-top">
        <div className="iv-progress-left">
          <span className="iv-progress-title tabular-nums">
            Question <strong>{clamped}</strong> of <strong>{safeMax}</strong>
          </span>
          <span className="iv-progress-sep" aria-hidden="true">
            ·
          </span>
          <span className="iv-progress-stage">
            {isFollowUp
              ? `Follow-up to Question ${clamped}`
              : "Technical round"}
          </span>
        </div>

        <span className="iv-progress-meta tabular-nums">
          {answeredCount} answered · {percent}%
        </span>
      </div>

      <div
        className="iv-progress-track"
        role="progressbar"
        aria-label={`Question ${clamped} of ${safeMax}`}
        aria-valuenow={clamped}
        aria-valuemin={1}
        aria-valuemax={safeMax}
      >
        <span style={{ width: `${percent}%` }} />
      </div>
    </section>
  );
}
