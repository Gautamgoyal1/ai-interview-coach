import { useEffect, useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import FileUpload from "../components/FileUpload";
import { ArrowRightIcon, FileTextIcon } from "../components/Icons";
import ResumeReport from "../features/resume/ResumeReport";
import { useResume } from "../features/resume/useResume";
import { useAuth } from "../hooks/useAuth";
import "./ResumeAnalysis.css";

export default function ResumeAnalysis() {
  const [file, setFile] = useState<File | null>(null);
  const [fileError, setFileError] = useState<string | null>(null);
  const [jobRole, setJobRole] = useState("Machine Learning Engineer");
  const [jobDescription, setJobDescription] = useState("");

  const { logout } = useAuth();
  const navigate = useNavigate();
  const { result, loading, error, unauthorized, submitResume } = useResume();

  useEffect(() => {
    if (unauthorized) {
      logout();
      navigate("/login", { replace: true });
    }
  }, [unauthorized, logout, navigate]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file) return;
    await submitResume(file, jobRole, jobDescription);
  }

  return (
    <div className="resume-page">
      <header className="pm-page-header">
        <div>
          <p className="pm-eyebrow">RESUME ANALYZER</p>
          <h1 className="pm-page-title">Evaluate Resume Alignment</h1>
          <p className="pm-page-subtitle">
            Upload your PDF resume and target role to identify matched skills,
            missing requirements, and likely interview topics.
          </p>
        </div>
      </header>

      <form className="pm-card resume-form" onSubmit={handleSubmit}>
        <div className="form-heading">
          <div>
            <h2>Upload &amp; Configure</h2>
            <p>
              Provide your resume and optional job description for evidence-aware
              skill matching.
            </p>
          </div>
          <span className="badge">PDF · Max 10 MB</span>
        </div>

        <div className="resume-form-grid">
          <div className="resume-form-col">
            <div className="form-field" style={{ height: "100%" }}>
              <span className="field-label">Resume PDF</span>
              <FileUpload
                file={file}
                fileError={fileError}
                onSelect={(nextFile, nextErr) => {
                  setFile(nextFile);
                  setFileError(nextErr);
                }}
              />
            </div>
          </div>

          <div className="resume-form-col">
            <div className="form-field">
              <label htmlFor="job-role" className="field-label">
                Target job role
              </label>
              <input
                id="job-role"
                className="pm-input"
                value={jobRole}
                onChange={(event) => setJobRole(event.target.value)}
                minLength={2}
                maxLength={150}
                required
                placeholder="e.g. Machine Learning Engineer"
              />
            </div>

            <div className="form-field">
              <label htmlFor="job-description" className="field-label">
                Job description <span className="optional">(optional)</span>
              </label>
              <textarea
                id="job-description"
                className="pm-textarea"
                value={jobDescription}
                onChange={(event) => setJobDescription(event.target.value)}
                maxLength={15000}
                rows={5}
                placeholder="Paste the job description or required skills for more targeted matching..."
              />
            </div>
          </div>
        </div>

        {error && (
          <div className="pm-alert-error" role="alert">
            <span>{error}</span>
          </div>
        )}

        <div className="form-footer-row">
          <span className="form-footnote">
            Deterministic skill matching paired with evidence-aware feedback.
          </span>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={!file || !jobRole.trim() || loading}
          >
            <span>{loading ? "Analyzing resume..." : "Analyze Resume"}</span>
            <ArrowRightIcon size={15} />
          </button>
        </div>
      </form>

      {loading && (
        <div className="pm-status-banner" role="status" style={{ marginTop: 20 }}>
          <span className="pm-spinner" />
          <div>
            <strong>Analyzing your resume</strong> — Extracting skills and
            evaluating role alignment...
          </div>
        </div>
      )}

      {!result && !loading && (
        <section className="pm-empty-state" style={{ marginTop: 20 }}>
          <div className="pm-empty-icon">
            <FileTextIcon size={20} />
          </div>
          <h2>Ready when you are</h2>
          <p>
            Select a PDF resume above to generate your skill breakdown, gap
            analysis, and practice interview questions.
          </p>
        </section>
      )}

      {result && (
        <div className="resume-results-wrap">
          {result.reused ? (
            <div className="pm-card reuse-banner" role="status">
              <div>
                <strong>Reused existing analysis (v{result.version ?? 1})</strong>
                <p>
                  This matches a previous analysis with the same resume, role, and job description — no duplicate history entry was created.
                </p>
              </div>
              <button
                type="button"
                className="btn btn-secondary"
                disabled={!file || loading}
                onClick={() => {
                  if (file) {
                    void submitResume(file, jobRole, jobDescription, true);
                  }
                }}
              >
                Force Fresh Analysis
              </button>
            </div>
          ) : (
            <div className="pm-card reuse-banner fresh" role="status">
              <div>
                <strong>New analysis saved (v{result.version ?? 1})</strong>
                <p>
                  Your updated resume analysis is saved and ready for interview practice.
                </p>
              </div>
            </div>
          )}

          <ResumeReport
            result={result}
            statusLabel={result.reused ? "Saved analysis reused" : "New analysis"}
          />
          <div className="pm-card history-callout">
            <span>Manage your saved analyses or launch an interview anytime.</span>
            <Link to="/history" className="btn btn-secondary">
              <span>View Analysis History</span>
              <ArrowRightIcon size={14} />
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
