import { Link } from "react-router-dom";

interface MissedPointsProps {
  strengths: string[];
  weaknesses: string[];
  missingConcepts: string[];
}

export default function MissedPoints({
  strengths,
  weaknesses,
  missingConcepts,
}: MissedPointsProps) {
  return (
    <div className="report-two-col">
      <section className="pm-card report-card">
        <div className="report-card-header">
          <div>
            <h3>Strengths</h3>
            <p>Evidence-supported concepts and topics you handled well</p>
          </div>
        </div>
        {strengths.length > 0 ? (
          <ul className="report-bullet-list report-strengths">
            {strengths.map((item, idx) => (
              <li key={idx}>{item}</li>
            ))}
          </ul>
        ) : (
          <p className="report-empty-note">
            No clear strengths recorded yet.
          </p>
        )}
      </section>

      <section className="pm-card report-card">
        <div className="report-card-header">
          <div>
            <h3>Areas for Improvement</h3>
            <p>Observed weaknesses and missing technical concepts</p>
          </div>
        </div>
        {weaknesses.length > 0 ? (
          <ul className="report-bullet-list report-weaknesses">
            {weaknesses.map((item, idx) => (
              <li key={idx} style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "0.5rem" }}>
                <span>{item}</span>
                <Link
                  to={`/practice?topic=${encodeURIComponent(item.split(":")[0])}&gap=${encodeURIComponent(item)}`}
                  className="badge badge-neutral"
                  style={{ textDecoration: "none", fontSize: "0.75rem", whiteSpace: "nowrap", cursor: "pointer" }}
                >
                  Practice →
                </Link>
              </li>
            ))}
          </ul>
        ) : (
          <p className="report-empty-note">
            No major weaknesses identified in evaluated answers.
          </p>
        )}

        {missingConcepts.length > 0 && (
          <div className="missing-concepts-wrap">
            <span className="missing-concepts-label">Missing concepts</span>
            <div className="missing-concepts-tags">
              {missingConcepts.map((concept, idx) => (
                <Link
                  key={idx}
                  to={`/practice?topic=${encodeURIComponent(concept)}&gap=${encodeURIComponent('Missing concept: ' + concept)}`}
                  className="badge badge-warning"
                  style={{ textDecoration: "none", cursor: "pointer" }}
                >
                  {concept} ↗
                </Link>
              ))}
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
