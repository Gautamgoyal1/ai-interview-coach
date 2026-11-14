import type { PracticeAttempt } from "../../types/practice";

interface Props {
  attempt: PracticeAttempt;
  previous?: PracticeAttempt;
  onImprove: () => void;
  onNext: () => void;
  busy: boolean;
  generating: boolean;
}
export default function PracticeCoaching({
  attempt,
  previous,
  onImprove,
  onNext,
  busy,
  generating,
}: Props) {
  const feedback = attempt.feedback;
  const available = feedback.evaluation_status === "completed";
  return (
    <aside className="learning-coach" aria-labelledby="coaching-title">
      <div className="learning-section-label">03 / Coaching</div>
      <header className="learning-coach-head">
        <h2 id="coaching-title" tabIndex={-1}>
          Your next improvement
        </h2>
        <span>Attempt {attempt.attempt_number}</span>
      </header>
      <p className="learning-assistance">
        {attempt.assistance_level === "independent"
          ? "Independent attempt"
          : attempt.assistance_level === "hint_assisted"
            ? "Hint-assisted attempt"
            : "Reference-assisted attempt"}
      </p>
      {available ? (
        <>
          <p className="learning-recommendation">
            {feedback.next_action ||
              feedback.improvement_suggestions[0] ||
              "Refine your answer using the coaching below."}
          </p>
          <button
            type="button"
            className="btn btn-primary"
            disabled={busy}
            onClick={onImprove}
          >
            Improve my answer
          </button>
          {feedback.improvements_from_previous &&
            feedback.improvements_from_previous.length > 0 && (
              <section className="learning-comparison">
                <h3>What improved</h3>
                <ul>
                  {feedback.improvements_from_previous.map((item, i) => (
                    <li key={i}>{item}</li>
                  ))}
                </ul>
              </section>
            )}
          {feedback.missing_points.length > 0 && (
            <section>
              <h3>Focus on</h3>
              <ul>
                {feedback.missing_points.map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            </section>
          )}
          {feedback.improvement_suggestions.length > 0 && (
            <section>
              <h3>How to strengthen it</h3>
              <ul>
                {feedback.improvement_suggestions.map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            </section>
          )}
          {feedback.correct_points.length > 0 && (
            <section>
              <h3>Keep doing</h3>
              <ul>
                {feedback.correct_points.map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            </section>
          )}
          {feedback.suggested_structure.length > 0 && (
            <details>
              <summary>Suggested answer structure</summary>
              <ol>
                {feedback.suggested_structure.map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ol>
            </details>
          )}
          {feedback.improved_example_answer && (
            <details>
              <summary>Explore an AI-generated example</summary>
              <p className="learning-caption">
                One possible response, not an authoritative benchmark. Check its
                claims and use your own experience.
              </p>
              <p className="learning-example">
                {feedback.improved_example_answer}
              </p>
            </details>
          )}
        </>
      ) : (
        <div role="status">
          <p>
            Coaching is unavailable for this attempt. Your submitted answer is
            saved; no score or improvement is inferred.
          </p>
          <button
            type="button"
            className="btn btn-primary"
            disabled={busy}
            onClick={onImprove}
          >
            Revise and try coaching again
          </button>
        </div>
      )}
      <details>
        <summary>
          {previous
            ? "Compare your last two attempts"
            : "Review your submitted answer"}
        </summary>
        {previous && (
          <section>
            <h3>Attempt {previous.attempt_number}</h3>
            <p className="learning-example">{previous.answer_text}</p>
            <p className="learning-caption">
              {previous.assistance_level.replace(/_/g, " ")}
            </p>
          </section>
        )}
        <section>
          <h3>Attempt {attempt.attempt_number}</h3>
          <p className="learning-example">{attempt.answer_text}</p>
          <p className="learning-caption">
            {attempt.assistance_level.replace(/_/g, " ")}
          </p>
        </section>
      </details>
      <div className="learning-next">
        <p>Ready to apply this elsewhere?</p>
        <button
          type="button"
          className="btn btn-secondary"
          onClick={onNext}
          disabled={busy}
        >
          {generating ? "Generating question..." : "Try a similar question"}
        </button>
      </div>
    </aside>
  );
}
