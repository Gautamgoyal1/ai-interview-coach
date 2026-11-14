import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  ArrowRightIcon,
  BarChartIcon,
  BookOpenIcon,
  FileTextIcon,
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

  const userFullName = user?.full_name?.trim();
  const rawHandle = user?.email ? user.email.split("@")[0] : "";
  const cleanHandle = rawHandle.replace(/_\d{8,}$/, "");
  const fallbackHandle = cleanHandle.length > 20 ? cleanHandle.slice(0, 18) + "…" : cleanHandle;
  const displayName = userFullName || fallbackHandle;

  // ── Next recommended action ──
  let nextTitle = "Analyze your resume to begin";
  let nextDescription =
    "Upload a PDF resume and target role to identify matched skills, gaps, and tailored interview topics.";
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

  const latestScore =
    latestReport?.overall_score != null
      ? `${latestReport.overall_score.toFixed(0)} / 100`
      : latestAnalysis
      ? `${latestAnalysis.match_score.toFixed(0)}%`
      : "—";

  const latestScoreLabel =
    latestReport?.overall_score != null
      ? "Interview Score"
      : latestAnalysis
      ? "Resume Match"
      : "No score yet";

  const currentFocus =
    latestReport?.target_role || latestAnalysis?.job_role || "General";

  if (loading) {
    return (
      <div className="dash-page">
        <div className="dash-editorial-header" aria-busy="true">
          <div className="dash-welcome-col">
            <div className="pm-skeleton" style={{ height: 14, width: "30%", marginBottom: 14 }} />
            <div className="pm-skeleton" style={{ height: 36, width: "65%", marginBottom: 10 }} />
            <div className="pm-skeleton" style={{ height: 16, width: "80%" }} />
          </div>
          <div className="dash-next-action-col">
            <div className="pm-skeleton" style={{ height: 18, width: "50%", marginBottom: 10 }} />
            <div className="pm-skeleton" style={{ height: 24, width: "80%", marginBottom: 8 }} />
            <div className="pm-skeleton" style={{ height: 44, width: 160 }} />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="dash-page">
      {error && (
        <div className="pm-alert-error" role="alert">
          <span>{error}</span>
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={() => void loadOverview()}
          >
            Retry
          </button>
        </div>
      )}

      {/* ── 1. Editorial welcome band ── */}
      <section className="dash-editorial-header" aria-label="Welcome and next action">
        <div className="dash-welcome-col">
          <p className="dash-eyebrow">Your Workspace</p>
          <h1 className="dash-welcome-title">
            {displayName ? `Welcome back, ${displayName}` : "Welcome back"}
          </h1>
          <p className="dash-welcome-sub">
            Track your resume profile, technical interviews, and personalized practice roadmap.
          </p>
          <div className="dash-welcome-links">
            <Link to="/analyze" className="btn btn-secondary btn-sm">
              <FileTextIcon size={15} />
              <span>Analyze Resume</span>
            </Link>
            <Link to="/interview" className="btn btn-secondary btn-sm">
              <MessageSquareIcon size={15} />
              <span>Start Interview</span>
            </Link>
          </div>
        </div>

        <div className="dash-next-action-col">
          <p className="dash-next-label">Recommended Next Step</p>
          <h2 className="dash-next-title">{nextTitle}</h2>
          <p className="dash-next-desc">{nextDescription}</p>
          <Link to={nextTo} className="btn btn-primary">
            <span>{nextLabel}</span>
            <ArrowRightIcon size={15} />
          </Link>
        </div>
      </section>

      {/* ── 2. Horizontal stats strip ── */}
      <div className="dash-stats-strip" role="region" aria-label="Preparation snapshot">
        <div className="dash-stat-item">
          <strong className="dash-stat-num tabular-nums">{analyses.length}</strong>
          <span className="dash-stat-label">Resume Profiles</span>
        </div>
        <div className="dash-stat-divider" />
        <div className="dash-stat-item">
          <strong className="dash-stat-num tabular-nums">{reports.length}</strong>
          <span className="dash-stat-label">Interviews Done</span>
        </div>
        <div className="dash-stat-divider" />
        <div className="dash-stat-item">
          <strong className="dash-stat-num tabular-nums">{latestScore}</strong>
          <span className="dash-stat-label">{latestScoreLabel}</span>
        </div>
        <div className="dash-stat-divider" />
        <div className="dash-stat-item">
          <strong className="dash-stat-num dash-stat-focus">{currentFocus}</strong>
          <span className="dash-stat-label">Current Focus</span>
        </div>
      </div>

      {/* ── 3. Learning section: featured + compact rows ── */}
      {recommendations.length > 0 && (
        <section className="dash-learning-section" aria-label="Targeted practice recommendations">
          <div className="dash-learning-head">
            <h2 className="dash-section-heading">Targeted Practice</h2>
            <Link to="/practice" className="dash-view-all">
              Open Practice Hub →
            </Link>
          </div>

          {/* Featured recommendation */}
          <article className="dash-featured-rec">
            <div className="dash-featured-rec-meta">
              <span className="badge badge-accent" style={{ textTransform: "capitalize" }}>
                {recommendations[0].interview_type}
              </span>
              <span className="dash-featured-priority">
                {recommendations[0].priority} priority
              </span>
            </div>
            <h3 className="dash-featured-topic">{recommendations[0].topic}</h3>
            <p className="dash-featured-gap">{recommendations[0].observed_gap}</p>
            <Link
              to={`/practice?topic=${encodeURIComponent(recommendations[0].topic)}&type=${encodeURIComponent(recommendations[0].interview_type)}&gap=${encodeURIComponent(recommendations[0].observed_gap)}&reportId=${recommendations[0].source_report_id || ""}`}
              className="btn btn-primary"
            >
              <BookOpenIcon size={15} />
              <span>Practice This Topic</span>
            </Link>
          </article>

          {/* Additional recs as compact rows */}
          {recommendations.length > 1 && (
            <div className="dash-rec-rows">
              {recommendations.slice(1).map((rec, idx) => (
                <div key={idx + 1} className="dash-rec-row">
                  <div className="dash-rec-row-info">
                    <strong className="dash-rec-row-topic">{rec.topic}</strong>
                    <span className="dash-rec-row-gap">{rec.observed_gap}</span>
                  </div>
                  <div className="dash-rec-row-right">
                    <span className="badge" style={{ textTransform: "capitalize" }}>
                      {rec.interview_type}
                    </span>
                    <Link
                      to={`/practice?topic=${encodeURIComponent(rec.topic)}&type=${encodeURIComponent(rec.interview_type)}&gap=${encodeURIComponent(rec.observed_gap)}&reportId=${rec.source_report_id || ""}`}
                      className="dash-rec-row-cta"
                    >
                      Practice →
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      )}

      {/* ── 4. Recent activity: two plain lists side by side ── */}
      <div className="dash-activity-cols">
        <section className="dash-activity-col">
          <div className="dash-activity-col-head">
            <div className="dash-activity-col-title">
              <FileTextIcon size={15} />
              <h3>Resume Profiles</h3>
            </div>
            <Link to="/history" className="dash-view-all">View all →</Link>
          </div>

          {analyses.length === 0 ? (
            <p className="dash-activity-empty">
              No resume analyses yet. Upload a PDF to evaluate matched skills.
            </p>
          ) : (
            <ul className="dash-activity-list">
              {analyses.slice(0, 4).map((item) => (
                <li key={item.id} className="dash-activity-row">
                  <div className="dash-activity-main">
                    <strong>{item.job_role}</strong>
                    <span>{item.filename} · {formatDateTime(item.created_at)}</span>
                  </div>
                  <div className="dash-activity-right">
                    <span className="badge tabular-nums">{item.match_score.toFixed(0)}%</span>
                    <Link
                      to={`/history/${item.id}`}
                      className="dash-activity-link"
                      aria-label={`Open analysis for ${item.job_role}`}
                    >
                      View
                    </Link>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="dash-activity-col">
          <div className="dash-activity-col-head">
            <div className="dash-activity-col-title">
              <BarChartIcon size={15} />
              <h3>Interview Reports</h3>
            </div>
            <Link to="/reports" className="dash-view-all">View all →</Link>
          </div>

          {reports.length === 0 ? (
            <p className="dash-activity-empty">
              No interview reports yet. Complete an interview session to generate feedback.
            </p>
          ) : (
            <ul className="dash-activity-list">
              {reports.slice(0, 4).map((rep) => (
                <li key={rep.id} className="dash-activity-row">
                  <div className="dash-activity-main">
                    <strong>{rep.target_role}</strong>
                    <span>{formatDateTime(rep.interview_date)}</span>
                  </div>
                  <div className="dash-activity-right">
                    <span className="badge badge-accent tabular-nums">
                      {rep.overall_score !== null
                        ? `${rep.overall_score.toFixed(0)} / 100`
                        : rep.status}
                    </span>
                    <Link
                      to={`/reports/${rep.session_id}`}
                      className="dash-activity-link"
                      aria-label={`Open report for ${rep.target_role}`}
                    >
                      Report
                    </Link>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </div>
  );
}
