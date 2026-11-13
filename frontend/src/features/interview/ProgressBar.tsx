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
    <div
      className="iv-progress-track"
      role="progressbar"
      aria-label={`Question ${clamped} of ${safeMax}${isFollowUp ? " (Follow-up)" : ""}`}
      aria-valuenow={clamped}
      aria-valuemin={1}
      aria-valuemax={safeMax}
      title={`${answeredCount} answered · ${percent}% complete`}
    >
      <div className="iv-progress-fill" style={{ width: `${percent}%` }} />
    </div>
  );
}
