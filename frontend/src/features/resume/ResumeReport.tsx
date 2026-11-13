import { useMemo, useState, type CSSProperties } from "react";
import { Link } from "react-router-dom";
import type { ResumeAnalysisResult } from "../../types/resume";
import "../../pages/ResumeAnalysis.css";

interface ResumeReportProps {
  result: ResumeAnalysisResult;
  skillEvidence?: Record<string, string>;
  analysisId?: number | null;
  version?: number;
  subtitle?: string;
  statusLabel?: string;
}

type SkillFilter = "all" | "demonstrated" | "mentioned" | "missing";

interface SkillEntry {
  name: string;
  category: "demonstrated" | "mentioned" | "missing";
  isMatched: boolean;
}

export default function ResumeReport({
  result,
  skillEvidence,
  analysisId,
  version,
  subtitle = "Here is how your resume aligns with your target role.",
  statusLabel = "Analysis complete",
}: ResumeReportProps) {
  const score = Math.max(0, Math.min(100, result.match_score));
  const resolvedAnalysisId = analysisId ?? result.analysis_id ?? null;
  const resolvedVersion = version ?? result.version ?? 1;
  const evidenceMap = skillEvidence ?? result.skill_evidence ?? {};

  const skillEntries = useMemo<SkillEntry[]>(() => {
    const matchedSet = new Set(result.matched_skills);
    const missingSet = new Set(result.missing_skills);
    const allNames = Array.from(
      new Set([
        ...result.matched_skills,
        ...result.missing_skills,
        ...result.resume_skills,
      ]),
    );

    return allNames.map((name) => {
      if (missingSet.has(name)) {
        return { name, category: "missing", isMatched: false };
      }
      const ev = evidenceMap[name];
      if (ev === "demonstrated") {
        return { name, category: "demonstrated", isMatched: matchedSet.has(name) };
      }
      if (ev === "mentioned_only" || ev === "mentioned") {
        return { name, category: "mentioned", isMatched: matchedSet.has(name) };
      }
      return {
        name,
        category: matchedSet.has(name) ? "demonstrated" : "mentioned",
        isMatched: matchedSet.has(name),
      };
    });
  }, [result.matched_skills, result.missing_skills, result.resume_skills, evidenceMap]);

  const counts = useMemo(() => {
    return {
      all: skillEntries.length,
      demonstrated: skillEntries.filter((s) => s.category === "demonstrated").length,
      mentioned: skillEntries.filter((s) => s.category === "mentioned").length,
      missing: skillEntries.filter((s) => s.category === "missing").length,
    };
  }, [skillEntries]);

  const [activeFilter, setActiveFilter] = useState<SkillFilter>("all");
  const [selectedSkill, setSelectedSkill] = useState<string | null>(null);
  const [showAllImprovements, setShowAllImprovements] = useState(false);
  const [checkedImprovements, setCheckedImprovements] = useState<Record<number, boolean>>({});
  const [showQuestions, setShowQuestions] = useState(false);

  const visibleSkills = useMemo(() => {
    if (activeFilter === "all") return skillEntries;
    return skillEntries.filter((s) => s.category === activeFilter);
  }, [skillEntries, activeFilter]);

  const selectedEntry =
    skillEntries.find((s) => s.name === selectedSkill) ?? null;

  const visibleImprovements = showAllImprovements
    ? result.improvement_suggestions
    : result.improvement_suggestions.slice(0, 3);

  function toggleImprovement(index: number) {
    setCheckedImprovements((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
  }

  return (
    <section className="results">
      <div className="results-heading">
        <div>
          <p className="pm-eyebrow">RESUME REPORT · V{resolvedVersion}</p>
          <h2>{result.job_role}</h2>
          <p>{subtitle}</p>
        </div>
        <span className="badge badge-success">{statusLabel}</span>
      </div>

      {/* Section 1 — Resume Overview */}
      <article className="pm-card score-card">
        <div className="score-copy">
          <span className="pm-eyebrow">RESUME MATCH SCORE</span>
          <h3 className="tabular-nums">{score.toFixed(1)}%</h3>
          <p>
            {score >= 80
              ? "Strong alignment with target role requirements."
              : score >= 60
                ? "Solid foundation with a few targeted skill gaps to close."
                : "Key role skills are missing from your resume. Focus on the top gaps below."}
          </p>
          <div
            className="score-track"
            role="progressbar"
            aria-label="Resume match score"
            aria-valuenow={score}
            aria-valuemin={0}
            aria-valuemax={100}
          >
            <span style={{ width: `${score}%` }} />
          </div>

          <div className="overview-kpis">
            <span className="overview-kpi">
              <strong>{result.matched_skills.length}</strong> matched
            </span>
            <span className="overview-kpi">
              <strong>{result.missing_skills.length}</strong> gaps
            </span>
            <span className="overview-kpi">
              <strong>{result.strengths.length}</strong> strengths
            </span>
          </div>
        </div>

        <div className="score-card-right">
          <div
            className="score-ring"
            style={{ "--score": `${score * 3.6}deg` } as CSSProperties}
            aria-label={`${score.toFixed(1)} percent match`}
          >
            <div>
              <strong className="tabular-nums">{Math.round(score)}</strong>
              <span>/ 100</span>
            </div>
          </div>

          {resolvedAnalysisId && (
            <Link
              to={`/interview?analysisId=${resolvedAnalysisId}`}
              className="btn btn-primary"
            >
              Start AI Interview →
            </Link>
          )}
        </div>
      </article>

      {/* Section 2 — Interactive Skill Breakdown */}
      <article className="pm-card result-card">
        <div className="result-card-heading">
          <div>
            <h3>Interactive Skill Breakdown</h3>
            <p>
              Filter by evidence category and click any skill to inspect why it matters.
            </p>
          </div>
        </div>

        <div className="skill-filter-tabs" role="tablist" aria-label="Filter skills by category">
          {(
            [
              ["all", `All (${counts.all})`],
              ["demonstrated", `Demonstrated (${counts.demonstrated})`],
              ["mentioned", `Mentioned (${counts.mentioned})`],
              ["missing", `Missing (${counts.missing})`],
            ] as const
          ).map(([key, label]) => (
            <button
              key={key}
              type="button"
              role="tab"
              aria-selected={activeFilter === key}
              className={`skill-filter-tab${activeFilter === key ? " active" : ""}`}
              onClick={() => setActiveFilter(key)}
            >
              {label}
            </button>
          ))}
        </div>

        {visibleSkills.length > 0 ? (
          <div className="skill-tags">
            {visibleSkills.map((entry) => (
              <button
                key={entry.name}
                type="button"
                className={`skill-chip skill-chip-${entry.category}${
                  selectedSkill === entry.name ? " selected" : ""
                }`}
                aria-pressed={selectedSkill === entry.name}
                onClick={() =>
                  setSelectedSkill((prev) =>
                    prev === entry.name ? null : entry.name,
                  )
                }
              >
                <span>{entry.name}</span>
                <span className="skill-chip-dot" aria-hidden="true" />
              </button>
            ))}
          </div>
        ) : (
          <p className="result-empty">No skills in this category.</p>
        )}

        {selectedEntry && (
          <div className="skill-inspector" role="region" aria-label={`Details for ${selectedEntry.name}`}>
            <div className="skill-inspector-head">
              <strong>{selectedEntry.name}</strong>
              <span className={`badge ${
                selectedEntry.category === "demonstrated"
                  ? "badge-success"
                  : selectedEntry.category === "missing"
                    ? "badge-warning"
                    : "badge-accent"
              }`}>
                {selectedEntry.category === "demonstrated"
                  ? "Demonstrated in resume"
                  : selectedEntry.category === "missing"
                    ? "Missing from resume"
                    : "Mentioned only"}
              </span>
            </div>
            <p>
              {selectedEntry.category === "demonstrated"
                ? `Your resume shows practical context for ${selectedEntry.name}${
                    selectedEntry.isMatched ? ` aligned with ${result.job_role}.` : "."
                  } Be ready to walk through a concrete project or trade-off using it.`
                : selectedEntry.category === "mentioned"
                  ? `${selectedEntry.name} appears in your resume without strong project or action-verb evidence. Add a bullet showing how you applied it and what outcome it produced.`
                  : `${selectedEntry.name} is required for ${result.job_role}, but no evidence was found in your resume. If you have used it, add it with project context; otherwise prioritize it in your prep.`}
            </p>
          </div>
        )}
      </article>

      {/* Section 3 — Priority Improvements & Strengths */}
      <div className="result-grid">
        <article className="pm-card result-card">
          <div className="result-card-heading">
            <div>
              <h3>Priority Improvements</h3>
              <p>Top actions to strengthen your profile</p>
            </div>
            <span className="badge badge-neutral tabular-nums">
              {result.improvement_suggestions.length}
            </span>
          </div>

          {visibleImprovements.length > 0 ? (
            <ul className="checklist-list">
              {visibleImprovements.map((item, idx) => (
                <li key={`${idx}-${item}`} className={checkedImprovements[idx] ? "checked" : ""}>
                  <label>
                    <input
                      type="checkbox"
                      checked={Boolean(checkedImprovements[idx])}
                      onChange={() => toggleImprovement(idx)}
                    />
                    <span>{item}</span>
                  </label>
                </li>
              ))}
            </ul>
          ) : (
            <p className="result-empty">No additional improvements suggested.</p>
          )}

          {result.improvement_suggestions.length > 3 && (
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => setShowAllImprovements((prev) => !prev)}
            >
              {showAllImprovements
                ? "Show top 3 improvements"
                : `Show all ${result.improvement_suggestions.length} improvements`}
            </button>
          )}
        </article>

        <article className="pm-card result-card">
          <div className="result-card-heading">
            <div>
              <h3>Key Strengths</h3>
              <p>Signals supported by your resume</p>
            </div>
            <span className="badge badge-neutral tabular-nums">
              {result.strengths.length}
            </span>
          </div>

          {result.strengths.length > 0 ? (
            <ul className="insight-list">
              {result.strengths.map((item, index) => (
                <li key={`${index}-${item}`}>
                  <span className="insight-number">{index + 1}</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="result-empty">No specific strengths highlighted.</p>
          )}
        </article>
      </div>

      {/* Section 4 — Collapsible Interview Preparation Questions */}
      <article className="pm-card result-card">
        <div className="result-card-heading">
          <div>
            <h3>Likely Interview Questions</h3>
            <p>
              {result.likely_interview_questions.length} tailored topics derived from your resume and target role
            </p>
          </div>
          <button
            type="button"
            className="btn btn-secondary"
            aria-expanded={showQuestions}
            onClick={() => setShowQuestions((prev) => !prev)}
          >
            {showQuestions ? "Hide Questions" : "Preview Questions"}
          </button>
        </div>

        {showQuestions && (
          result.likely_interview_questions.length > 0 ? (
            <ul className="insight-list">
              {result.likely_interview_questions.map((q, index) => (
                <li key={`${index}-${q}`}>
                  <span className="insight-number">Q{index + 1}</span>
                  <span>{q}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="result-empty">No sample questions generated.</p>
          )
        )}
      </article>
    </section>
  );
}
