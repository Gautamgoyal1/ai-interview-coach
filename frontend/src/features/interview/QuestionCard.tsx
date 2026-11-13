import type { InterviewQuestion } from "../../types/interview";

interface QuestionCardProps {
  question: InterviewQuestion;
  questionIndex: number;
  maxQuestions: number;
}

function formatQuestionNumber(index: number, total: number): string {
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${pad(Math.max(1, index))} / ${pad(Math.max(1, total))}`;
}

function formatLabel(raw: string): string {
  if (!raw) return "";
  return raw
    .replace(/_/g, " ")
    .replace(/\b\w/g, (ch) => ch.toUpperCase());
}

export default function QuestionCard({
  question,
  questionIndex,
  maxQuestions,
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
          <span className="iv-meta-item">{question.topic}</span>
          {difficultyLabel && (
            <>
              <span className="iv-meta-dot" aria-hidden="true">
                ·
              </span>
              <span className="iv-meta-item">{difficultyLabel}</span>
            </>
          )}
          {typeLabel && (
            <>
              <span className="iv-meta-dot" aria-hidden="true">
                ·
              </span>
              <span className="iv-meta-item">{typeLabel}</span>
            </>
          )}
        </div>

        <h2 className="iv-question-text">{question.question_text}</h2>
      </div>

      <p className="iv-question-guidance">
        {question.is_follow_up
          ? "Clarify or expand on your previous response in your own words."
          : "Take your time. Explain your reasoning clearly with a concrete example where helpful."}
      </p>
    </section>
  );
}
