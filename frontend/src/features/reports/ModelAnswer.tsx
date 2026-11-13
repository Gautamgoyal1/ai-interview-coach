import { ChevronDownIcon } from "../../components/Icons";
import type { QuestionFeedbackItem } from "../../types/report";

interface ModelAnswerProps {
  items: QuestionFeedbackItem[];
}

export default function ModelAnswer({ items }: ModelAnswerProps) {
  const primaries = items.filter((item) => !item.is_follow_up);
  const followUpsByParent = new Map<string, QuestionFeedbackItem[]>();

  for (const item of items) {
    if (item.is_follow_up) {
      const key = item.parent_question_id || `idx_${item.question_index}`;
      const existing = followUpsByParent.get(key) ?? [];
      existing.push(item);
      followUpsByParent.set(key, existing);
    }
  }

  return (
    <section className="pm-card report-card">
      <div className="report-card-header">
        <div>
          <h3>Question-by-Question Feedback</h3>
          <p>Expand any question to review your answer and rubric breakdown</p>
        </div>
      </div>

      {items.length === 0 ? (
        <p className="report-empty-note">No answered questions recorded.</p>
      ) : (
        <div className="qfb-list">
          {primaries.map((item, idx) => {
            const followUps =
              followUpsByParent.get(item.question_id) ??
              followUpsByParent.get(`idx_${item.question_index}`) ??
              [];

            return (
              <div key={item.question_id} className="qfb-group">
                <QuestionFeedbackCard item={item} defaultOpen={idx === 0} />
                {followUps.map((fu) => (
                  <div key={fu.question_id} className="qfb-follow-up">
                    <QuestionFeedbackCard item={fu} defaultOpen={false} />
                  </div>
                ))}
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}

function QuestionFeedbackCard({
  item,
  defaultOpen,
}: {
  item: QuestionFeedbackItem;
  defaultOpen: boolean;
}) {
  const scoreClass =
    item.overall_score === null
      ? "badge-neutral"
      : item.overall_score >= 75
        ? "badge-success"
        : item.overall_score >= 50
          ? "badge-warning"
          : "badge-danger";

  return (
    <details className="qfb-details" open={defaultOpen}>
      <summary className="qfb-summary">
        <div className="qfb-summary-left">
          <div className="qfb-meta">
            <span className="badge badge-neutral tabular-nums">
              Q{item.question_index}
              {item.is_follow_up ? " · Follow-up" : ""}
            </span>
            <span className="badge badge-accent">{item.topic}</span>
            <span className="badge badge-neutral">{item.difficulty}</span>
          </div>
          <p className="qfb-question">{item.question_text}</p>
        </div>

        <div className="qfb-summary-right">
          <span className={`badge ${scoreClass} tabular-nums`}>
            {item.grading_status === "completed" && item.overall_score !== null
              ? `${item.overall_score.toFixed(1)} / 100`
              : "Unavailable"}
          </span>
          <ChevronDownIcon size={16} className="qfb-chevron" />
        </div>
      </summary>

      <div className="qfb-body">
        <p className="qfb-answer">
          <strong>Your answer:</strong> {item.answer_text || "—"}
        </p>

        {item.grading_status === "completed" && (
          <div className="qfb-dimensions">
            {Object.entries(item.dimension_scores).map(([dim, detail]) => (
              <div key={dim} className="qfb-dim-row">
                <strong className="tabular-nums">
                  {dim.replace(/_/g, " ")} ({detail.score}/5):
                </strong>{" "}
                <span>{detail.explanation}</span>
              </div>
            ))}
          </div>
        )}

        {item.missing_concepts.length > 0 && (
          <p className="qfb-notes">
            <strong>Missing concepts:</strong> {item.missing_concepts.join(", ")}
          </p>
        )}
        {item.improvement_suggestions.length > 0 && (
          <p className="qfb-notes">
            <strong>Suggestions:</strong>{" "}
            {item.improvement_suggestions.join(" ")}
          </p>
        )}
      </div>
    </details>
  );
}
