import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import ActionMenu from "../components/ActionMenu";
import ConfirmDialog from "../components/ConfirmDialog";
import { ArrowRightIcon, HistoryIcon } from "../components/Icons";
import ResumeReport from "../features/resume/ResumeReport";
import { useAuth } from "../hooks/useAuth";
import { ApiError } from "../services/api";
import {
  deleteResumeAnalysis,
  getResumeAnalyses,
  getResumeAnalysisById,
} from "../services/resume.service";
import type {
  ResumeAnalysisHistoryItem,
  SavedResumeAnalysis,
} from "../types/resume";
import { formatDateTime } from "../utils/formatters";
import "./History.css";
import "./ResumeAnalysis.css";

function getScoreBadgeClass(score: number): string {
  if (score >= 80) return "badge-success";
  if (score >= 60) return "badge-accent";
  return "badge-warning";
}

export default function History() {
  const { analysisId } = useParams<{ analysisId?: string }>();
  const { logout } = useAuth();
  const navigate = useNavigate();

  const [items, setItems] = useState<ResumeAnalysisHistoryItem[]>([]);
  const [selected, setSelected] = useState<SavedResumeAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [notFound, setNotFound] = useState(false);

  const [pendingDelete, setPendingDelete] = useState<{
    id: number;
    jobRole: string;
    interviewCount: number;
  } | null>(null);
  const [cascadeDelete, setCascadeDelete] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const handleUnauthorized = useCallback(() => {
    logout();
    navigate("/login", { replace: true });
  }, [logout, navigate]);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    setNotFound(false);

    if (analysisId !== undefined) {
      const numericId = Number(analysisId);
      if (!Number.isInteger(numericId) || numericId <= 0) {
        setSelected(null);
        setNotFound(true);
        setLoading(false);
        return;
      }

      try {
        const detail = await getResumeAnalysisById(numericId);
        setSelected(detail);
      } catch (err) {
        if (err instanceof ApiError && err.status === 401) {
          handleUnauthorized();
          return;
        }
        if (err instanceof ApiError && err.status === 404) {
          setSelected(null);
          setNotFound(true);
          return;
        }
        setError(
          err instanceof Error
            ? err.message
            : "Could not load the saved resume analysis.",
        );
      } finally {
        setLoading(false);
      }
      return;
    }

    setSelected(null);
    try {
      const historyList = await getResumeAnalyses();
      setItems(historyList);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        handleUnauthorized();
        return;
      }
      setError(
        err instanceof Error
          ? err.message
          : "Could not load your resume analysis history.",
      );
    } finally {
      setLoading(false);
    }
  }, [analysisId, handleUnauthorized]);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  async function handleConfirmDelete() {
    if (!pendingDelete || deleting) return;
    setDeleting(true);
    setDeleteError(null);
    try {
      const res = await deleteResumeAnalysis(pendingDelete.id, cascadeDelete);
      const deletedRole = pendingDelete.jobRole;
      setItems((prev) => prev.filter((item) => item.id !== pendingDelete.id));
      setPendingDelete(null);
      setCascadeDelete(false);
      setNotice(
        res.mode === "archived"
          ? `Removed "${deletedRole}" from analysis history (linked interviews preserved).`
          : `Deleted "${deletedRole}" analysis.`,
      );
      if (analysisId !== undefined) {
        navigate("/history", { replace: true });
      }
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        handleUnauthorized();
        return;
      }
      setDeleteError(
        err instanceof Error ? err.message : "Could not delete analysis.",
      );
    } finally {
      setDeleting(false);
    }
  }

  if (analysisId !== undefined) {
    return (
      <div className="history-page">
        <div className="pm-card history-detail-bar">
          <Link to="/history" className="btn btn-secondary">
            ← Back to History
          </Link>

          {selected && (
            <div className="history-detail-meta">
              <span>
                File: <strong>{selected.filename}</strong>
              </span>
              <span>
                Analyzed: <strong>{formatDateTime(selected.created_at)}</strong>
              </span>
              <Link
                to={`/interview?analysisId=${selected.id}`}
                className="btn btn-primary"
              >
                <span>Start AI Interview</span>
                <ArrowRightIcon size={14} />
              </Link>
              <ActionMenu
                label="Analysis actions"
                items={[
                  {
                    label: "Start Interview",
                    to: `/interview?analysisId=${selected.id}`,
                  },
                  {
                    label: "Delete Analysis",
                    tone: "danger",
                    onClick: () => {
                      setDeleteError(null);
                      setCascadeDelete(false);
                      setPendingDelete({
                        id: selected.id,
                        jobRole: selected.result.job_role,
                        interviewCount: selected.interview_count ?? 0,
                      });
                    },
                  },
                ]}
              />
            </div>
          )}
        </div>

        {loading && (
          <div className="pm-status-banner" role="status">
            <span className="pm-spinner" />
            <div>
              <strong>Loading saved analysis</strong> — Fetching your stored
              resume report...
            </div>
          </div>
        )}

        {!loading && notFound && (
          <section className="pm-empty-state" role="alert">
            <h2>Analysis not found</h2>
            <p>
              This saved resume analysis does not exist or does not belong to
              your account.
            </p>
            <div style={{ marginTop: 16 }}>
              <Link to="/history" className="btn btn-secondary">
                Return to Analysis History
              </Link>
            </div>
          </section>
        )}

        {!loading && error && (
          <div className="pm-alert-error" role="alert">
            <span>{error}</span>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => void loadData()}
            >
              Try Again
            </button>
          </div>
        )}

        {!loading && !error && !notFound && selected && (
          <ResumeReport
            result={selected.result}
            skillEvidence={selected.skill_evidence}
            analysisId={selected.id}
            version={selected.version ?? 1}
            statusLabel="Saved report"
            subtitle={`Stored report for ${selected.filename} (${formatDateTime(selected.created_at)}).`}
          />
        )}

        <ConfirmDialog
          open={pendingDelete !== null}
          title="Delete this resume analysis?"
          description="This will remove the analysis from your saved history."
          warningNote={
            pendingDelete && pendingDelete.interviewCount > 0
              ? `This analysis has ${pendingDelete.interviewCount} linked interview session(s). By default, it will be archived from history while keeping your interviews and reports intact.`
              : undefined
          }
          checkboxLabel={
            pendingDelete && pendingDelete.interviewCount > 0
              ? "Also permanently delete linked interview sessions and reports"
              : undefined
          }
          checkboxChecked={cascadeDelete}
          onCheckboxChange={setCascadeDelete}
          confirmLabel={
            pendingDelete && pendingDelete.interviewCount > 0 && !cascadeDelete
              ? "Remove from History"
              : "Delete Analysis"
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
    <div className="history-page">
      <header className="pm-page-header">
        <div>
          <p className="pm-eyebrow">SAVED REPORTS</p>
          <h1 className="pm-page-title">Analysis History</h1>
          <p className="pm-page-subtitle">
            Reopen any previous resume evaluation or start a tailored AI
            interview from a saved profile.
          </p>
        </div>

        <Link to="/analyze" className="btn btn-primary">
          + New Analysis
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
          <span className="pm-spinner" />
          <div>
            <strong>Loading analysis history</strong> — Retrieving your saved
            resume evaluations...
          </div>
        </div>
      )}

      {!loading && error && (
        <div className="pm-alert-error" role="alert">
          <span>{error}</span>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => void loadData()}
          >
            Retry
          </button>
        </div>
      )}

      {!loading && !error && items.length === 0 && (
        <section className="pm-empty-state">
          <div className="pm-empty-icon">
            <HistoryIcon size={20} />
          </div>
          <h2>No saved analyses yet</h2>
          <p>
            Once you analyze a resume, your role match score, skill breakdown,
            and interview questions will be saved here for quick review.
          </p>
          <div style={{ marginTop: 18 }}>
            <Link to="/analyze" className="btn btn-primary">
              <span>Analyze Your First Resume</span>
              <ArrowRightIcon size={14} />
            </Link>
          </div>
        </section>
      )}

      {!loading && !error && items.length > 0 && (
        <>
          <div className="pm-card history-table-wrap">
            <table className="history-table">
              <thead>
                <tr>
                  <th>Target Role</th>
                  <th>Resume File</th>
                  <th>Analyzed</th>
                  <th>Match Score</th>
                  <th className="th-actions">Actions</th>
                </tr>
              </thead>
              <tbody>
                {items.map((item) => {
                  const hasScore =
                    typeof item.match_score === "number" &&
                    Number.isFinite(item.match_score);
                  const scoreValue = hasScore
                    ? Math.max(0, Math.min(100, item.match_score))
                    : null;

                  return (
                    <tr key={item.id}>
                      <td>
                        <strong className="table-role">{item.job_role}</strong>
                      </td>
                      <td>
                        <span className="table-filename" title={item.filename}>
                          {item.filename}
                        </span>
                      </td>
                      <td className="table-date tabular-nums">
                        {formatDateTime(item.created_at)}
                      </td>
                      <td>
                        {scoreValue !== null ? (
                          <span
                            className={`badge tabular-nums ${getScoreBadgeClass(scoreValue)}`}
                          >
                            {scoreValue.toFixed(0)}%
                          </span>
                        ) : (
                          "—"
                        )}
                      </td>
                      <td>
                        <div className="table-actions">
                          <Link
                            to={`/history/${item.id}`}
                            className="btn btn-secondary"
                          >
                            View
                          </Link>
                          <ActionMenu
                            label={`Actions for ${item.job_role}`}
                            items={[
                              {
                                label: "View Analysis",
                                to: `/history/${item.id}`,
                              },
                              {
                                label: "Start Interview",
                                to: `/interview?analysisId=${item.id}`,
                              },
                              {
                                label: "Delete Analysis",
                                tone: "danger",
                                onClick: () => {
                                  setDeleteError(null);
                                  setCascadeDelete(false);
                                  setPendingDelete({
                                    id: item.id,
                                    jobRole: item.job_role,
                                    interviewCount: item.interview_count ?? 0,
                                  });
                                },
                              },
                            ]}
                          />
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          <section
            className="history-mobile-list"
            aria-label="Saved resume analyses"
          >
            {items.map((item) => {
              const hasScore =
                typeof item.match_score === "number" &&
                Number.isFinite(item.match_score);
              const scoreValue = hasScore
                ? Math.max(0, Math.min(100, item.match_score))
                : null;

              return (
                <article key={item.id} className="pm-card history-mobile-card">
                  <div className="history-mobile-head">
                    <strong>{item.job_role}</strong>
                    {scoreValue !== null && (
                      <span
                        className={`badge tabular-nums ${getScoreBadgeClass(scoreValue)}`}
                      >
                        {scoreValue.toFixed(0)}%
                      </span>
                    )}
                  </div>
                  <p className="history-mobile-meta">
                    {item.filename} · {formatDateTime(item.created_at)}
                  </p>
                  <div className="history-mobile-actions">
                    <Link
                      to={`/history/${item.id}`}
                      className="btn btn-secondary"
                    >
                      View Analysis
                    </Link>
                    <Link
                      to={`/interview?analysisId=${item.id}`}
                      className="btn btn-primary"
                    >
                      Start Interview
                    </Link>
                    <ActionMenu
                      label={`Actions for ${item.job_role}`}
                      items={[
                        {
                          label: "View Analysis",
                          to: `/history/${item.id}`,
                        },
                        {
                          label: "Start Interview",
                          to: `/interview?analysisId=${item.id}`,
                        },
                        {
                          label: "Delete Analysis",
                          tone: "danger",
                          onClick: () => {
                            setDeleteError(null);
                            setCascadeDelete(false);
                            setPendingDelete({
                              id: item.id,
                              jobRole: item.job_role,
                              interviewCount: item.interview_count ?? 0,
                            });
                          },
                        },
                      ]}
                    />
                  </div>
                </article>
              );
            })}
          </section>
        </>
      )}

      <ConfirmDialog
        open={pendingDelete !== null}
        title="Delete this resume analysis?"
        description="This will remove the analysis from your saved history."
        warningNote={
          pendingDelete && pendingDelete.interviewCount > 0
            ? `This analysis has ${pendingDelete.interviewCount} linked interview session(s). By default, it will be archived from history while keeping your interviews and reports intact.`
            : undefined
        }
        checkboxLabel={
          pendingDelete && pendingDelete.interviewCount > 0
            ? "Also permanently delete linked interview sessions and reports"
            : undefined
        }
        checkboxChecked={cascadeDelete}
        onCheckboxChange={setCascadeDelete}
        confirmLabel={
          pendingDelete && pendingDelete.interviewCount > 0 && !cascadeDelete
            ? "Remove from History"
            : "Delete Analysis"
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
