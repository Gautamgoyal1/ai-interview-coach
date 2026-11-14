import { Link } from "react-router-dom";
import { practiceLink, type PracticeOrigin } from "../../utils/practiceNavigation";
import type { TopicPerformance } from "../../types/report";

interface TopicScoresProps {
  origin?: PracticeOrigin;
  topics: TopicPerformance[];
}

function barToneClass(score: number | null): string {
  if (score === null) return "";
  if (score >= 75) return "bar-success";
  if (score >= 50) return "bar-warning";
  return "bar-danger";
}

export default function TopicScores({ topics, origin = {} }: TopicScoresProps) {
  return (
    <section className="pm-card report-card">
      <div className="report-card-header">
        <div>
          <h3>{origin.interviewType === "hr" ? "Behavioral Topic Performance" : "Technical Topic Performance"}</h3>
          <p>Performance across topics covered in your interview</p>
        </div>
      </div>

      {topics.length === 0 ? (
        <p className="report-empty-note">No topics recorded.</p>
      ) : (
        <div className="topic-bars">
          {topics.map((item) => {
            const pct =
              item.score !== null ? Math.max(0, Math.min(100, item.score)) : 0;
            return (
              <div key={item.topic} className="topic-row">
                <div className="topic-row-head">
                  <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                    <strong>{item.topic}</strong>
                    <Link
                      to={practiceLink(item.topic, origin)}
                      className="badge badge-neutral"
                      style={{ textDecoration: "none", fontSize: "0.75rem", padding: "0.15rem 0.45rem", cursor: "pointer" }}
                    >
                      Practice →
                    </Link>
                  </div>
                  <span className="tabular-nums">
                    {item.score !== null ? `${item.score.toFixed(1)}%` : "N/A"}{" "}
                    · {item.questions_asked}{" "}
                    {item.questions_asked === 1 ? "question" : "questions"}
                  </span>
                </div>
                <div className={`report-bar-track ${barToneClass(item.score)}`}>
                  <span style={{ width: `${pct}%` }} />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
