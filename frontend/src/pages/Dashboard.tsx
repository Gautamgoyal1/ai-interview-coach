import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  ArrowRightIcon,
  BarChartIcon,
  BookOpenIcon,
  FileTextIcon,
  LightbulbIcon,
  MessageSquareIcon,
} from "../components/Icons";
import { useAuth } from "../hooks/useAuth";
import { ApiError } from "../services/api";
import { getPracticeRecommendations } from "../services/practice.service";
import { listInterviewReports } from "../services/report.service";
import { getResumeAnalyses } from "../services/resume.service";
import type { PracticeRecommendationItem } from "../types/practice";
import type { InterviewReportSummary } from "../types/report";
import type { ResumeAnalysisHistoryItem } from "../types/resume";
import { formatDateTime } from "../utils/formatters";
import "./Dashboard.css";

export default function Dashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [analyses, setAnalyses] = useState<ResumeAnalysisHistoryItem[]>([]);
  const [reports, setReports] = useState<InterviewReportSummary[]>([]);
  const [recommendations, setRecommendations] = useState<PracticeRecommendationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadOverview = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [analysesData, reportsData, recsData] = await Promise.all([
        getResumeAnalyses(10),
        listInterviewReports(10),
        getPracticeRecommendations(3),
      ]);
      setAnalyses(analysesData);
      setReports(reportsData);
      setRecommendations(recsData);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        logout();
        navigate("/login", { replace: true });
        return;
      }
      setError(
        err instanceof Error
          ? err.message
          : "Could not load your workspace overview.",
      );
    } finally {
      setLoading(false);
    }
  }, [logout, navigate]);

  useEffect(() => {
    void loadOverview();
  }, [loadOverview]);

  const latestAnalysis = analyses[0] ?? null;
  const latestReport = reports[0] ?? null;

  let nextTitle = "Analyze your resume to begin";
  let nextDescription =
    "Upload a PDF resume and target role to identify matched skills, gaps, and interview topics.";
  let nextTo = "/analyze";
  let nextLabel = "Upload Resume";

  if (latestAnalysis && !latestReport) {
    nextTitle = `Start your ${latestAnalysis.job_role} AI interview`;
    nextDescription =
      "Your resume profile is ready. Practice technical questions tailored to your strengths and gaps.";
    nextTo = `/interview?analysisId=${latestAnalysis.id}`;
    nextLabel = "Start AI Interview";
  } else if (latestReport) {
    nextTitle = `Review your ${latestReport.target_role} report`;
    nextDescription =
      "Inspect your rubric-based dimension breakdown, missed concepts, and study roadmap.";
    nextTo = `/reports/${latestReport.session_id}`;
    nextLabel = "View Latest Report";
  }

  return (
    <div className="dash-page">
      <header className="pm-page-header">
        <div>
          <p className="pm-eyebrow">OVERVIEW</p>
          <h1 className="pm-page-title">
            Welcome back{user?.email ? `, ${user.email.split("@")[0]}` : ""}
          </h1>
          <p className="pm-page-subtitle">
            Track your resume analyses, technical interview sessions, and
            rubric-based performance reports.
          </p>
        </div>

        <div className="dash-header-actions">
          <Link to="/analyze" className="btn btn-secondary">
            <FileTextIcon size={15} />
            <span>Analyze Resume</span>
          </Link>
          <Link to="/interview" className="btn btn-primary">
            <MessageSquareIcon size={15} />
            <span>Start Interview</span>
          </Link>
        </div>
      </header>

      {error && (
        <div className="pm-alert-error" role="alert" style={{ marginBottom: 20 }}>
          <span>{error}</span>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => void loadOverview()}
          >
            Retry
          </button>
        </div>
      )}

      {loading ? (
        <div className="dash-metrics-grid" aria-busy="true">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="pm-card dash-metric-card">
              <div className="pm-skeleton" style={{ height: 12, width: "60%" }} />
              <div
                className="pm-skeleton"
                style={{ height: 28, width: "40%", marginTop: 10 }}
              />
            </div>
          ))}
        </div>
      ) : (
        <>
          <section className="dash-metrics-grid" aria-label="Preparation metrics">
            <article className="pm-card dash-metric-card">
              <span className="dash-metric-label">Resume Analyses</span>
              <strong className="dash-metric-value tabular-nums">
                {analyses.length}
              </strong>
              <span className="dash-metric-hint">Saved evaluations</span>
            </article>

            <article className="pm-card dash-metric-card">
              <span className="dash-metric-label">Latest Resume Match</span>
              <strong className="dash-metric-value tabular-nums">
                {latestAnalysis
                  ? `${latestAnalysis.match_score.toFixed(1)}%`
                  : "—"}
              </strong>
              <span className="dash-metric-hint">
                {latestAnalysis ? latestAnalysis.job_role : "No analysis yet"}
              </span>
            </article>

            <article className="pm-card dash-metric-card">
              <span className="dash-metric-label">Interview Reports</span>
              <strong className="dash-metric-value tabular-nums">
                {reports.length}
              </strong>
              <span className="dash-metric-hint">Completed interviews</span>
            </article>

            <article className="pm-card dash-metric-card">
              <span className="dash-metric-label">Latest Practice Score</span>
              <strong className="dash-metric-value tabular-nums">
                {latestReport && latestReport.overall_score !== null
                  ? `${latestReport.overall_score.toFixed(1)} / 100`
                  : "—"}
              </strong>
              <span className="dash-metric-hint">
                {latestReport
                  ? `Rubric ${latestReport.rubric_version}`
                  : "No report yet"}
              </span>
            </article>
          </section>

          <section className="pm-card dash-next-card">
            <div className="dash-next-copy">
              <span className="badge badge-accent">Recommended next step</span>
              <h2>{nextTitle}</h2>
              <p>{nextDescription}</p>
            </div>
            <div className="dash-next-actions">
              <Link to={nextTo} className="btn btn-primary">
                <span>{nextLabel}</span>
                <ArrowRightIcon size={15} />
              </Link>
            </div>
          </section>

          {recommendations.length > 0 && (
            <section className="pm-card" style={{ padding: "1.5rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                  <LightbulbIcon size={18} style={{ color: "#eab308" }} />
                  <h3 style={{ margin: 0, fontSize: "1.05rem", fontWeight: 700 }}>Continue Improving — Targeted Practice</h3>
                </div>
                <Link to="/practice" className="dash-view-all">
                  Open Practice Hub →
                </Link>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: "1rem" }}>
                {recommendations.map((rec, idx) => (
                  <article
                    key={idx}
                    style={{
                      padding: "1rem 1.25rem",
                      background: "#0d1017",
                      border: "1px solid #1f242e",
                      borderRadius: "8px",
                      display: "flex",
                      flexDirection: "column",
                      justifyContent: "space-between",
                      gap: "0.75rem",
                    }}
                  >
                    <div>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.35rem" }}>
                        <strong style={{ fontSize: "0.95rem", color: "#f1f5f9" }}>{rec.topic}</strong>
                        <span className="badge badge-neutral" style={{ textTransform: "capitalize", fontSize: "0.7rem" }}>
                          {rec.interview_type}
                        </span>
                      </div>
                      <p style={{ fontSize: "0.825rem", color: "#94a3b8", margin: 0, lineHeight: 1.4 }}>
                        {rec.observed_gap}
                      </p>
                    </div>
                    <Link
                      to={`/practice?topic=${encodeURIComponent(rec.topic)}&type=${encodeURIComponent(rec.interview_type)}&gap=${encodeURIComponent(rec.observed_gap)}&reportId=${rec.source_report_id || ""}`}
                      className="btn btn-secondary"
                      style={{ fontSize: "0.8rem", padding: "0.35rem 0.65rem", alignSelf: "flex-start" }}
                    >
                      <BookOpenIcon size={13} />
                      <span>Practice Topic</span>
                    </Link>
                  </article>
                ))}
              </div>
            </section>
          )}

          <div className="dash-recent-grid">
            <section className="pm-card dash-recent-card">
              <div className="dash-recent-head">
                <div className="dash-recent-title">
                  <FileTextIcon size={16} />
                  <h3>Recent Resume Analyses</h3>
                </div>
                <Link to="/history" className="dash-view-all">
                  View all
                </Link>
              </div>

              {analyses.length === 0 ? (
                <p className="dash-empty-inline">
                  No resume analyses yet. Upload a PDF to get started.
                </p>
              ) : (
                <ul className="dash-list">
                  {analyses.slice(0, 4).map((item) => (
                    <li key={item.id} className="dash-list-item">
                      <div className="dash-list-main">
                        <strong>{item.job_role}</strong>
                        <span>
                          {item.filename} · {formatDateTime(item.created_at)}
                        </span>
                      </div>
                      <div className="dash-list-right">
                        <span className="badge tabular-nums">
                          {item.match_score.toFixed(0)}% match
                        </span>
                        <Link
                          to={`/history/${item.id}`}
                          className="dash-item-link"
                        >
                          Open
                        </Link>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </section>

            <section className="pm-card dash-recent-card">
              <div className="dash-recent-head">
                <div className="dash-recent-title">
                  <BarChartIcon size={16} />
                  <h3>Recent Interview Reports</h3>
                </div>
                <Link to="/reports" className="dash-view-all">
                  View all
                </Link>
              </div>

              {reports.length === 0 ? (
                <p className="dash-empty-inline">
                  No interview reports yet. Complete an AI interview to generate
                  one.
                </p>
              ) : (
                <ul className="dash-list">
                  {reports.slice(0, 4).map((rep) => (
                    <li key={rep.id} className="dash-list-item">
                      <div className="dash-list-main">
                        <strong>{rep.target_role}</strong>
                        <span>{formatDateTime(rep.interview_date)}</span>
                      </div>
                      <div className="dash-list-right">
                        <span className="badge badge-accent tabular-nums">
                          {rep.overall_score !== null
                            ? `${rep.overall_score.toFixed(0)} / 100`
                            : rep.status}
                        </span>
                        <Link
                          to={`/reports/${rep.session_id}`}
                          className="dash-item-link"
                        >
                          Open
                        </Link>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </section>
          </div>
        </>
      )}
    </div>
  );
}
