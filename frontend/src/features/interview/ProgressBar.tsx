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
  const completed = Math.max(0, clamped - 1);
  const percent = Math.round((completed / safeMax) * 100);

  return (
    <div
      className="iv-progress-track"
      role="progressbar"
      aria-label={`Question ${clamped} of ${safeMax}${isFollowUp ? " (Follow-up)" : ""}`}
      aria-valuenow={completed}
      aria-valuemin={0}
      aria-valuemax={safeMax}
      aria-valuetext={`Primary question ${clamped} of ${safeMax}${isFollowUp ? ", follow-up" : ""}. ${answeredCount} responses submitted.`}
      title={`${answeredCount} responses submitted / Primary question ${clamped} of ${safeMax}`}
    >
      <div className="iv-progress-fill" style={{ width: `${percent}%` }} />
    </div>
  );
}
