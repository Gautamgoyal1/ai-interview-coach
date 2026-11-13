import { useState } from "react";
import { Link } from "react-router-dom";
import type { RecommendationItem } from "../../types/report";

interface PracticePlanProps {
  recommendations: RecommendationItem[];
}

function priorityBadgeClass(priority: string): string {
  const normalized = priority.toLowerCase();
  if (normalized === "high") return "badge-danger";
  if (normalized === "medium") return "badge-warning";
  return "badge-neutral";
}

export default function PracticePlan({ recommendations }: PracticePlanProps) {
  const [completed, setCompleted] = useState<Record<number, boolean>>({});

  function toggleItem(index: number) {
    setCompleted((prev) => ({ ...prev, [index]: !prev[index] }));
  }

  return (
    <section className="pm-card report-card">
      <div className="report-card-header">
        <div>
          <h3>Personalized Preparation Roadmap</h3>
          <p>Prioritized next steps based on your interview gaps</p>
        </div>
      </div>

      {recommendations.length === 0 ? (
        <p className="report-empty-note">No recommendations generated.</p>
      ) : (
        <div className="roadmap-list">
          {recommendations.map((rec, idx) => {
            const done = Boolean(completed[idx]);
            return (
              <article
                key={idx}
                className={`roadmap-item${done ? " roadmap-done" : ""}`}
              >
                <div className="roadmap-item-head">
                  <label className="roadmap-check-label">
                    <input
                      type="checkbox"
                      checked={done}
                      onChange={() => toggleItem(idx)}
                    />
                    <strong>{rec.area}</strong>
                  </label>
                  <span className={`badge ${priorityBadgeClass(rec.priority)}`}>
                    {rec.priority} priority
                  </span>
                </div>
                <p className="roadmap-gap">
                  <strong>Observed gap:</strong> {rec.observed_gap}
                </p>
                <p className="roadmap-action">
                  <strong>Next step:</strong> {rec.action}
                </p>
                <div style={{ marginTop: "0.75rem" }}>
                  <Link
                    to={`/practice?topic=${encodeURIComponent(rec.area)}&gap=${encodeURIComponent(rec.observed_gap)}`}
                    className="btn btn-secondary"
                    style={{ fontSize: "0.8rem", padding: "0.35rem 0.75rem" }}
                  >
                    <span>Practice This Topic</span>
                    <span style={{ fontSize: "0.9rem" }}>→</span>
                  </Link>
                </div>
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}
