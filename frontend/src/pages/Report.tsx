import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import ActionMenu from "../components/ActionMenu";
import ConfirmDialog from "../components/ConfirmDialog";
import { ArrowRightIcon, BarChartIcon } from "../components/Icons";
import MissedPoints from "../features/reports/MissedPoints";
import ModelAnswer from "../features/reports/ModelAnswer";
import PracticePlan from "../features/reports/PracticePlan";
import TopicScores from "../features/reports/TopicScores";
import { useReport } from "../features/reports/useReport";
import { useAuth } from "../hooks/useAuth";
import { ApiError } from "../services/api";
import { deleteInterviewSession } from "../services/interview.service";
import { deleteInterviewReport } from "../services/report.service";
import { formatDateTime } from "../utils/formatters";
import "./Report.css";

const TECHNICAL_DIMENSIONS = [
  "technical_correctness",
  "relevance",
  "completeness",
  "technical_depth",
];

const HR_DIMENSIONS = [
  "reasoning_critical_thinking",
  "decision_making_tradeoffs",
  "communication_clarity",
  "relevance_completeness",
  "reflection_adaptability",
];

function scoreBadgeClass(score: number | null): string {
  if (score === null) return "badge-neutral";
  if (score >= 75) return "badge-success";
  if (score >= 50) return "badge-warning";
  return "badge-danger";
}

function barToneClass(pct: number | null): string {
  if (pct === null) return "";
  if (pct >= 75) return "bar-success";
  if (pct >= 50) return "bar-warning";
  return "bar-danger";
}

export default function Report() {
  const { sessionId } = useParams<{ sessionId?: string }>();
  const navigate = useNavigate();
  const { logout } = useAuth();
  const {
    report,
    summaries,
    loading,
    generating,
    error,
    unauthorized,
    loadOrGenerateReport,
    retryGenerate,
    loadReportHistory,
    removeSummary,
    clearReport,
  } = useReport();

  const [pendingDelete, setPendingDelete] = useState<{
    sessionId: string;
    targetRole: string;
    mode: "report" | "interview";
  } | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const handleUnauthorized = useCallback(() => {
    logout();
    navigate("/login", { replace: true });
  }, [logout, navigate]);

  useEffect(() => {
    if (unauthorized) {
      handleUnauthorized();
    }
  }, [unauthorized, handleUnauthorized]);

  useEffect(() => {
    if (sessionId) {
      void loadOrGenerateReport(sessionId);
    } else {
      void loadReportHistory();
    }
  }, [sessionId, loadOrGenerateReport, loadReportHistory]);

  async function handleConfirmDelete() {
    if (!pendingDelete || deleting) return;
    setDeleting(true);
    setDeleteError(null);
    try {
      if (pendingDelete.mode === "report") {
        await deleteInterviewReport(pendingDelete.sessionId);
        setNotice(
          `Deleted report for "${pendingDelete.targetRole}" (underlying interview preserved).`,
        );
      } else {
        await deleteInterviewSession(pendingDelete.sessionId);
        setNotice(
          `Deleted interview session and report for "${pendingDelete.targetRole}".`,
        );
      }
      removeSummary(pendingDelete.sessionId);
      setPendingDelete(null);
      if (sessionId) {
        clearReport();
        navigate("/reports", { replace: true });
      }
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        handleUnauthorized();
        return;
      }
      setDeleteError(
        err instanceof Error ? err.message : "Could not complete deletion.",
      );
    } finally {
      setDeleting(false);
    }
  }

  if (!sessionId) {
    return (
      <div className="report-list-page">
        <header className="pm-page-header">
          <div>
            <p className="pm-eyebrow">Practice Performance</p>
            <h1 className="pm-page-title">Interview Reports</h1>
            <p className="pm-page-subtitle">
              Review rubric-based evaluations, topic breakdowns, and study plans
              from your completed AI interviews.
            </p>
          </div>
          <Link to="/interview" className="btn btn-primary">
            <span>Start AI Interview</span>
            <ArrowRightIcon size={15} />
          </Link>
        </header>

        {notice && (
          <div className="pm-toast" role="status">
            <span>{notice}</span>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => setNotice(null)}
            >
              Dismiss
            </button>
          </div>
        )}

        {loading && (
          <div className="pm-status-banner" role="status">
            <span className="pm-spinner" aria-hidden="true" />
            <div>
              <strong>Loading interview reports</strong>
              <p>Fetching your saved evaluation reports...</p>
            </div>
          </div>
        )}

        {!loading && error && (
          <section className="pm-card report-error-card" role="alert">
            <h2>Could not load reports</h2>
            <p>{error}</p>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => void loadReportHistory()}
            >
              Retry
            </button>
          </section>
        )}

        {!loading && !error && summaries.length === 0 && (
          <section className="pm-card pm-empty-state">
            <div className="pm-empty-icon">
              <BarChartIcon size={22} />
            </div>
            <h2>No interview reports yet</h2>
            <p>
              Complete an AI technical interview to generate your rubric-based
              performance report and preparation roadmap.
            </p>
            <div className="pm-empty-actions">
              <Link to="/interview" className="btn btn-primary">
                <span>Start Your First AI Interview</span>
                <ArrowRightIcon size={15} />
              </Link>
            </div>
          </section>
        )}

        {!loading && !error && summaries.length > 0 && (
          <section className="pm-card report-table-card" aria-label="Interview reports">
            <div className="report-table-wrap">
              <table className="report-table">
                <thead>
                  <tr>
                    <th>Target Role</th>
                    <th>Status</th>
                    <th>Rubric</th>
                    <th>Date</th>
                    <th>Score</th>
                    <th className="report-th-actions">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {summaries.map((item) => (
                    <tr key={item.id}>
                      <td>
                        <div style={{ display: "flex", alignItems: "center", gap: 6, flexWrap: "wrap" }}>
                          <span
                            className={`badge ${
                              item.interview_type === "hr"
                                ? "badge-success"
                                : "badge-accent"
                            }`}
                          >
                            {item.interview_type === "hr" ? "HR" : "Technical"}
                          </span>
                          <strong className="report-row-role">
                            {item.target_role}
                          </strong>
                        </div>
                      </td>
                      <td>
                        <span className="badge badge-neutral">{item.status}</span>
                      </td>
                      <td className="tabular-nums">{item.rubric_version}</td>
                      <td className="report-row-date">
                        {formatDateTime(item.interview_date)}
                      </td>
                      <td>
                        <span
                          className={`badge ${scoreBadgeClass(item.overall_score)} tabular-nums`}
                        >
                          {item.overall_score !== null
                            ? `${item.overall_score.toFixed(0)} / 100`
                            : "N/A"}
                        </span>
                      </td>
                      <td className="report-td-actions">
                        <div style={{ display: "inline-flex", gap: 8, alignItems: "center" }}>
                          <Link
                            to={`/reports/${item.session_id}`}
                            className="btn btn-secondary"
                          >
                            View Report
                          </Link>
                          <ActionMenu
                            label={`Actions for ${item.target_role} report`}
                            items={[
                              {
                                label: "View Report",
                                to: `/reports/${item.session_id}`,
                              },
                              {
                                label: "Delete Report",
                                tone: "danger",
                                onClick: () => {
                                  setDeleteError(null);
                                  setPendingDelete({
                                    sessionId: item.session_id,
                                    targetRole: item.target_role,
                                    mode: "report",
                                  });
                                },
                              },
                              {
                                label: "Delete Interview & Report",
                                tone: "danger",
                                onClick: () => {
                                  setDeleteError(null);
                                  setPendingDelete({
                                    sessionId: item.session_id,
                                    targetRole: item.target_role,
                                    mode: "interview",
                                  });
                                },
                              },
                            ]}
                          />
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="report-mobile-list">
              {summaries.map((item) => (
                <article key={item.id} className="report-mobile-card">
                  <div className="report-mobile-top">
                    <div>
                      <div
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: 6,
                          marginBottom: 4,
                        }}
                      >
                        <span
                          className={`badge ${
                            item.interview_type === "hr"
                              ? "badge-success"
                              : "badge-accent"
                          }`}
                        >
                          {item.interview_type === "hr" ? "HR" : "Technical"}
                        </span>
                        <h2 className="report-row-role">{item.target_role}</h2>
                      </div>
                      <span className="report-row-date">
                        {formatDateTime(item.interview_date)} · Rubric{" "}
                        {item.rubric_version}
                      </span>
                    </div>
                    <span
                      className={`badge ${scoreBadgeClass(item.overall_score)} tabular-nums`}
                    >
                      {item.overall_score !== null
                        ? `${item.overall_score.toFixed(0)} / 100`
                        : "N/A"}
                    </span>
                  </div>
                  <div className="report-mobile-bottom">
                    <span className="badge badge-neutral">{item.status}</span>
                    <div style={{ display: "inline-flex", gap: 8, alignItems: "center" }}>
                      <Link
                        to={`/reports/${item.session_id}`}
                        className="btn btn-secondary"
                      >
                        View Report
                      </Link>
                      <ActionMenu
                        label={`Actions for ${item.target_role} report`}
                        items={[
                          {
                            label: "View Report",
                            to: `/reports/${item.session_id}`,
                          },
                          {
                            label: "Delete Report",
                            tone: "danger",
                            onClick: () => {
                              setDeleteError(null);
                              setPendingDelete({
                                sessionId: item.session_id,
                                targetRole: item.target_role,
                                mode: "report",
                              });
                            },
                          },
                          {
                            label: "Delete Interview & Report",
                            tone: "danger",
                            onClick: () => {
                              setDeleteError(null);
                              setPendingDelete({
                                sessionId: item.session_id,
                                targetRole: item.target_role,
                                mode: "interview",
                              });
                            },
                          },
                        ]}
                      />
                    </div>
                  </div>
                </article>
              ))}
            </div>
          </section>
        )}

        <ConfirmDialog
          open={pendingDelete !== null}
          title={
            pendingDelete?.mode === "interview"
              ? "Delete this interview and report?"
              : "Delete this interview report?"
          }
          description={
            pendingDelete?.mode === "interview"
              ? "This will permanently delete the interview session, all questions and answers, and its performance report."
              : "This will remove the generated report from your history. Your underlying interview session and answers will remain preserved."
          }
          confirmLabel={
            pendingDelete?.mode === "interview"
              ? "Delete Interview & Report"
              : "Delete Report"
          }
          busy={deleting}
          error={deleteError}
          onCancel={() => {
            if (!deleting) setPendingDelete(null);
          }}
          onConfirm={() => void handleConfirmDelete()}
        />
      </div>
    );
  }

  return (
    <div className="report-page">
      <div className="report-detail-bar">
        <Link to="/reports" className="btn btn-secondary">
          All Interview Reports
        </Link>
        {report && (
          <div className="report-detail-meta">
            <span>
              Role: <strong>{report.target_role}</strong>
            </span>
            <span>
              Date: <strong>{formatDateTime(report.interview_date)}</strong>
            </span>
            <span>
              Rubric: <strong className="tabular-nums">{report.rubric_version}</strong>
            </span>
            <ActionMenu
              label="Report actions"
              items={[
                {
                  label: "Delete Report",
                  tone: "danger",
                  onClick: () => {
                    setDeleteError(null);
                    setPendingDelete({
                      sessionId: report.session_id,
                      targetRole: report.target_role,
                      mode: "report",
                    });
                  },
                },
                {
                  label: "Delete Interview & Report",
                  tone: "danger",
                  onClick: () => {
                    setDeleteError(null);
                    setPendingDelete({
                      sessionId: report.session_id,
                      targetRole: report.target_role,
                      mode: "interview",
                    });
                  },
                },
              ]}
            />
          </div>
        )}
      </div>

      {(loading || generating) && !report && (
        <div className="pm-status-banner" role="status">
          <span className="pm-spinner" aria-hidden="true" />
          <div>
            <strong>
              {generating
                ? "Generating your interview report"
                : "Loading interview report"}
            </strong>
            <p>
              Aggregating rubric scores, topic performance, and study
              recommendations...
            </p>
          </div>
        </div>
      )}

      {!loading && !generating && error && !report && (
        <section className="pm-card report-error-card" role="alert">
          <h2>Report unavailable</h2>
          <p>{error}</p>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => void retryGenerate(sessionId)}
          >
            Retry Report Generation
          </button>
        </section>
      )}

      {report && (() => {
        const isHR =
          report.interview_type === "hr" ||
          report.rubric_version?.includes("hr") ||
          "reasoning_critical_thinking" in report.dimension_scores;
        const activeDimensions = isHR ? HR_DIMENSIONS : TECHNICAL_DIMENSIONS;

        return (
        <div className="report-sections">
          <header className="pm-card report-hero-card">
            <div className="report-hero-main">
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  marginBottom: 6,
                  flexWrap: "wrap",
                }}
              >
                <span
                  className={`badge ${
                    isHR ? "badge-success" : "badge-accent"
                  }`}
                >
                  {isHR ? "HR / Behavioral Interview" : "Technical Interview"}
                </span>
                <p className="pm-eyebrow" style={{ margin: 0 }}>
                  {isHR
                    ? "Competency & Judgment Evaluation"
                    : "Rubric-Based Practice Report"}
                </p>
              </div>
              <h1 className="report-hero-title">
                {report.target_role} —{" "}
                {isHR ? "Behavioral Evaluation" : "Interview Evaluation"}
              </h1>
              <p className="report-disclaimer">
                Practice score calculated deterministically using PrepMate rubric{" "}
                <strong className="tabular-nums">{report.rubric_version}</strong>.
                Not a standardized certification or hiring prediction.
              </p>
              <div className="report-stats-row">
                <span className="badge badge-neutral">
                  Status: {report.status}
                </span>
                <span className="badge badge-neutral tabular-nums">
                  Answered: {report.completion_stats.questions_answered}
                </span>
                <span className="badge badge-neutral tabular-nums">
                  Primary: {report.completion_stats.primary_questions_completed} /{" "}
                  {report.completion_stats.total_primary_questions}
                </span>
                <span className="badge badge-neutral tabular-nums">
                  Follow-ups: {report.completion_stats.follow_ups_answered}
                </span>
              </div>
            </div>

            <div className="report-overall-box">
              <span className="report-overall-kicker">Overall Score</span>
              <strong className="report-overall-value tabular-nums">
                {report.overall_score !== null
                  ? report.overall_score.toFixed(1)
                  : "N/A"}
              </strong>
              <span className="report-overall-denom">out of 100</span>
            </div>
          </header>

        {notice && (
          <div className="pm-toast" role="status">
            <span>{notice}</span>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => setNotice(null)}
            >
              Dismiss
            </button>
          </div>
        )}

          {report.evaluation_coverage.is_partial && (
            <div className="report-partial-banner" role="status">
              <strong>Partial evaluation coverage:</strong>{" "}
              {report.evaluation_coverage.evaluated_count} of{" "}
              {report.evaluation_coverage.total_answered} answered question(s)
              have completed rubric scores (
              {report.evaluation_coverage.unavailable_count} unavailable).
            </div>
          )}

          {(() => {
            const scoredTopics = report.topic_scores.filter(
              (t) => t.score !== null,
            );
            const strongest =
              scoredTopics.length > 0
                ? [...scoredTopics].sort(
                    (a, b) => (b.score ?? 0) - (a.score ?? 0),
                  )[0]
                : null;
            const topRec = report.recommendations[0] ?? null;
            if (!strongest && !topRec) return null;
            return (
              <div className="report-highlights-grid">
                {strongest && (
                  <article className="pm-card report-highlight-card">
                    <span className="pm-eyebrow">Strongest Topic</span>
                    <strong>{strongest.topic}</strong>
                    <p>
                      Average score{" "}
                      <span className="tabular-nums">
                        {strongest.score?.toFixed(2)} / 5
                      </span>{" "}
                      across {strongest.questions_asked} question(s).
                    </p>
                  </article>
                )}
                {topRec && (
                  <article className="pm-card report-highlight-card">
                    <span className="pm-eyebrow">Highest-Priority Improvement</span>
                    <strong>{topRec.area}</strong>
                    <p>{topRec.action}</p>
                  </article>
                )}
              </div>
            );
          })()}

          <section className="pm-card report-card">
            <div className="report-card-header">
              <div>
                <h3>
                  {isHR
                    ? "Behavioral Competency Breakdown"
                    : "Evaluation Breakdown"}
                </h3>
                <p>
                  {isHR
                    ? "5 weighted behavioral dimensions (0–5 scale)"
                    : "Weighted rubric dimensions (0–5 scale)"}
                </p>
              </div>
            </div>
            <div className="dimension-grid">
              {activeDimensions.map((key) => {
                const dim = report.dimension_scores[key];
                if (!dim) return null;
                const pct =
                  dim.percentage !== null
                    ? Math.max(0, Math.min(100, dim.percentage))
                    : 0;
                return (
                  <div key={key} className="dimension-item">
                    <div className="dimension-head">
                      <strong>
                        {dim.label}{" "}
                        <span className="dim-weight tabular-nums">
                          ({Math.round(dim.weight * 100)}%)
                        </span>
                      </strong>
                      <span className="tabular-nums">
                        {dim.average_score !== null
                          ? `${dim.average_score.toFixed(2)} / 5`
                          : "N/A"}
                      </span>
                    </div>
                    <div
                      className={`report-bar-track ${barToneClass(dim.percentage)}`}
                    >
                      <span style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </section>

          <TopicScores topics={report.topic_scores} />

          <MissedPoints
            strengths={report.strengths}
            weaknesses={report.weaknesses}
            missingConcepts={report.missing_concepts}
          />

          <PracticePlan recommendations={report.recommendations} />

          <ModelAnswer items={report.question_feedback} />
        </div>
        );
      })()}

      <ConfirmDialog
        open={pendingDelete !== null}
        title={
          pendingDelete?.mode === "interview"
            ? "Delete this interview and report?"
            : "Delete this interview report?"
        }
        description={
          pendingDelete?.mode === "interview"
            ? "This will permanently delete the interview session, all questions and answers, and its performance report."
            : "This will remove the generated report from your history. Your underlying interview session and answers will remain preserved."
        }
        confirmLabel={
          pendingDelete?.mode === "interview"
            ? "Delete Interview & Report"
            : "Delete Report"
        }
        busy={deleting}
        error={deleteError}
        onCancel={() => {
          if (!deleting) setPendingDelete(null);
        }}
        onConfirm={() => void handleConfirmDelete()}
      />
    </div>
  );
}
