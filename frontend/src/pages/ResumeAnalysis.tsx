
import { useState, type FormEvent } from "react";
import { useResume } from "../features/resume/useResume";
import "./ResumeAnalysis.css";

export default function ResumeAnalysis() {
  const [file, setFile] = useState<File | null>(null);
  const [jobRole, setJobRole] = useState("Machine Learning Engineer");
  const [jobDescription, setJobDescription] = useState("");

  const { result, loading, error, submitResume } = useResume();

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file) return;
    await submitResume(file, jobRole, jobDescription);
  }

  const score = result
    ? Math.max(0, Math.min(100, result.match_score))
    : 0;

  return (
    <main className="resume-page">
      <header className="hero">
        <p className="eyebrow">AI INTERVIEW COACH</p>
        <h1>Resume Analyzer</h1>
        <p>
          Understand your strengths, identify skill gaps, and prepare
          for your next interview.
        </p>
      </header>

      <form className="resume-form" onSubmit={handleSubmit}>
        <div className="form-heading">
          <div>
            <h2>Analyze your resume</h2>
            <p>Upload your resume and tell us which role you're targeting.</p>
          </div>
          <span className="form-step">PDF · MAX 10 MB</span>
        </div>

        <label htmlFor="resume-file">Resume</label>
        <input
          id="resume-file"
          type="file"
          accept="application/pdf,.pdf"
          required
          onChange={(event) => {
            const selected = event.target.files?.[0] ?? null;
            setFile(
              selected &&
                (selected.type === "application/pdf" ||
                  selected.name.toLowerCase().endsWith(".pdf")) &&
                selected.size <= 10 * 1024 * 1024
                ? selected
                : null,
            );
          }}
        />
        {file === null && (
          <p className="hint">Select a PDF file smaller than 10 MB.</p>
        )}
        {file && (
          <p className="file-selected">
            ✓ Selected: {file.name}
          </p>
        )}

        <label htmlFor="job-role">Target job role</label>
        <input
          id="job-role"
          value={jobRole}
          onChange={(event) => setJobRole(event.target.value)}
          minLength={2}
          maxLength={150}
          required
          placeholder="e.g. Machine Learning Engineer"
        />

        <label htmlFor="job-description">
          Job description <span className="optional">(optional)</span>
        </label>
        <textarea
          id="job-description"
          value={jobDescription}
          onChange={(event) => setJobDescription(event.target.value)}
          maxLength={15000}
          rows={4}
          placeholder="Paste the job description or required skills..."
        />

        {error && <p className="error-message">{error}</p>}

        <button type="submit" disabled={!file || !jobRole.trim() || loading}>
          {loading ? "Analyzing your resume..." : "Analyze Resume →"}
        </button>

        <p className="form-footnote">
          Your analysis includes skill matching, actionable feedback, and
          potential interview questions.
        </p>
      </form>

      {loading && (
        <div className="analysis-status" role="status">
          <span className="loading-dot" />
          <div>
            <strong>Analyzing your resume</strong>
            <p>Reviewing skills and preparing your personalized feedback...</p>
          </div>
        </div>
      )}

      {!result && !loading && (
        <section className="empty-state">
          <div className="empty-icon">✦</div>
          <h2>Your career insights start here</h2>
          <p>
            Run your first analysis to see your role match, skill gaps,
            strengths, and interview preparation recommendations.
          </p>
          <div className="empty-features">
            <span>01 · Skill match</span>
            <span>02 · Improvement plan</span>
            <span>03 · Interview questions</span>
          </div>
        </section>
      )}

      {result && (
        <section className="results">
          <div className="results-heading">
            <div>
              <p className="eyebrow">YOUR REPORT</p>
              <h2>Resume insights</h2>
              <p>Here is how your resume aligns with your target role.</p>
            </div>
            <span className="report-status">Analysis complete</span>
          </div>

          <article className="score-card">
            <div className="score-copy">
              <span className="section-kicker">OVERALL ROLE MATCH</span>
              <h3>{score.toFixed(1)}%</h3>
              <p>
                {score >= 80
                  ? "Strong alignment with your target role."
                  : score >= 60
                    ? "Good foundation. A few targeted improvements may help."
                    : "Use the insights below to identify areas to strengthen."}
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
            </div>

            <div
              className="score-ring"
              style={{ "--score": `${score * 3.6}deg` } as React.CSSProperties}
              aria-label={`${score.toFixed(1)} percent match`}
            >
              <div>
                <strong>{Math.round(score)}</strong>
                <span>out of 100</span>
              </div>
            </div>
          </article>

          <div className="result-grid">
            <ResultList
              title="Skills identified"
              subtitle="Skills detected in your resume"
              items={result.resume_skills}
              kind="skills"
              icon="✳"
            />
            <ResultList
              title="Matched skills"
              subtitle="Skills aligned with the target role"
              items={result.matched_skills}
              kind="matched"
              icon="✓"
            />
            <ResultList
              title="Skills to develop"
              subtitle="Skills identified as missing for this role"
              items={result.missing_skills}
              kind="missing"
              icon="↗"
            />
            <ResultList
              title="Your strengths"
              subtitle="Positive signals from your resume"
              items={result.strengths}
              kind="strengths"
              icon="✦"
            />
            <ResultList
              title="Improvement plan"
              subtitle="Practical ways to strengthen your profile"
              items={result.improvement_suggestions}
              kind="suggestions"
              icon="↗"
            />
            <ResultList
              title="Likely interview questions"
              subtitle="Questions to practise for your target role"
              items={result.likely_interview_questions}
              kind="questions"
              icon="?"
            />
          </div>

          <p className="report-note">
            <strong>Remember:</strong> A match score is an estimate based on
            the resume and role information provided, not a hiring prediction.
          </p>
        </section>
      )}
    </main>
  );
}

function ResultList({
  title,
  subtitle,
  items,
  kind,
  icon,
}: {
  title: string;
  subtitle: string;
  items: string[];
  kind: string;
  icon: string;
}) {
  return (
    <article className={`result-card result-${kind}`}>
      <div className="result-card-heading">
        <span className="result-icon" aria-hidden="true">{icon}</span>
        <div>
          <h3>{title}</h3>
          <p>{subtitle}</p>
        </div>
        <span className="result-count">{items.length}</span>
      </div>

      {items.length > 0 ? (
        kind === "skills" || kind === "matched" || kind === "missing" ? (
          <div className="skill-tags">
            {items.map((item, index) => (
              <span className="skill-tag" key={`${item}-${index}`}>
                {kind === "matched" && <span aria-hidden="true">✓ </span>}
                {item}
              </span>
            ))}
          </div>
        ) : (
          <ol className="insight-list">
            {items.map((item, index) => (
              <li key={`${item}-${index}`}>
                <span className="insight-number">
                  {String(index + 1).padStart(2, "0")}
                </span>
                <span>{item}</span>
              </li>
            ))}
          </ol>
        )
      ) : (
        <div className="result-empty">
          <span>✓</span>
          <p>No items identified in this category.</p>
        </div>
      )}
    </article>
  );
}
