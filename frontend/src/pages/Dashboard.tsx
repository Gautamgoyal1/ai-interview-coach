import { useCallback, useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  ArrowRightIcon,
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
import { practiceLink } from "../utils/practiceNavigation";
import "./Dashboard.css";

type Panel = "analyses" | "reports" | "recommendations";
const allPending = { analyses: true, reports: true, recommendations: true };
const noFailures = { analyses: false, reports: false, recommendations: false };
const priorityRank: Record<string, number> = { high: 0, medium: 1, low: 2 };
const sameRole = (a: string, b: string) =>
  a.trim().toLowerCase() === b.trim().toLowerCase();

export default function Dashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [analyses, setAnalyses] = useState<ResumeAnalysisHistoryItem[]>([]);
  const [reports, setReports] = useState<InterviewReportSummary[]>([]);
  const [recommendations, setRecommendations] = useState<
    PracticeRecommendationItem[]
  >([]);
  const [pending, setPending] = useState(allPending);
  const [failures, setFailures] = useState(noFailures);
  const generation = useRef(0);

  const loadOverview = useCallback(async () => {
    const run = ++generation.current;
    setPending(allPending);
    const load = async <T,>(
      panel: Panel,
      request: Promise<T>,
      apply: (data: T) => void,
    ) => {
      try {
        const data = await request;
        if (run !== generation.current) return;
        apply(data);
        setFailures((old) => ({ ...old, [panel]: false }));
      } catch (error) {
        if (run !== generation.current) return;
        if (error instanceof ApiError && error.status === 401) {
          logout();
          navigate("/login", { replace: true });
          return;
        }
        setFailures((old) => ({ ...old, [panel]: true }));
      } finally {
        if (run === generation.current)
          setPending((old) => ({ ...old, [panel]: false }));
      }
    };
    await Promise.all([
      load("analyses", getResumeAnalyses(10), setAnalyses),
      load("reports", listInterviewReports(10), setReports),
      load(
        "recommendations",
        getPracticeRecommendations(3),
        setRecommendations,
      ),
    ]);
  }, [logout, navigate]);
  useEffect(() => {
    void loadOverview();
    return () => {
      generation.current++;
    };
  }, [loadOverview]);

  const loading = Object.values(pending).some(Boolean);
  const hasError = Object.values(failures).some(Boolean);
  const goal =
    user?.target_role?.trim() ||
    analyses[0]?.job_role ||
    reports[0]?.target_role ||
    "Your next opportunity";
  const analysis = analyses.find((item) => sameRole(item.job_role, goal));
  const report = reports.find((item) => sameRole(item.target_role, goal));
  const relevant = recommendations
    .filter((item) => sameRole(item.target_role, goal))
    .sort(
      (a, b) =>
        (priorityRank[a.priority] ?? 3) - (priorityRank[b.priority] ?? 3),
    );
  const recommended = relevant[0];
  let next = {
    eyebrow: "BUILD YOUR STARTING POINT",
    title: "Analyze your resume to begin",
    description:
      "See how your experience aligns with a target role, then turn the gaps into interview practice.",
    label: "Analyze Resume",
    to: "/analyze",
    reason: "A saved resume gives your interview a useful starting point.",
  };
  if (analysis)
    next = {
      eyebrow: "PUT YOUR EXPERIENCE INTO WORDS",
      title: `Practice for your ${goal} interview`,
      description:
        "Your resume is ready. Choose a technical or behavioral round and rehearse the decisions behind your work.",
      label: "Set Up Interview",
      to: `/interview?analysisId=${analysis.id}`,
      reason: `Based on ${analysis.filename}`,
    };
  else if (report)
    next = {
      eyebrow: "TAKE ANOTHER STEP",
      title: "Build on your last interview",
      description:
        "Choose a focused practice topic or use your latest feedback to plan another round.",
      label: "Choose a Practice Topic",
      to: "/practice",
      reason: "Your latest interview report is available below.",
    };
  if (recommended)
    next = {
      eyebrow: "YOUR NEXT PRACTICE",
      title: recommended.topic,
      description: recommended.observed_gap,
      label: "Practice This Topic",
      to: practiceLink(
        recommended.topic,
        {
          interviewType: recommended.interview_type,
          reportId: recommended.source_report_id,
          targetRole: recommended.target_role,
        },
        recommended.observed_gap,
      ),
      reason: `${recommended.interview_type === "hr" ? "Behavioral" : "Technical"} practice from your interview feedback`,
    };
  if (hasError && !analysis && !report && !recommended)
    next = {
      eyebrow: "LET'S RECONNECT",
      title: "Your workspace is temporarily incomplete",
      description:
        "Unavailable data does not mean your history is empty. Retry loading your saved work.",
      label: "Open Analysis History",
      to: "/history",
      reason: "Your existing work has not been removed.",
    };
  const activity = [
    ...analyses.slice(0, 4).map((item) => ({
      key: `a${item.id}`,
      kind: "Resume analysis",
      title: item.job_role,
      detail: item.filename,
      date: item.created_at,
      to: `/history/${item.id}`,
      value: `${item.match_score.toFixed(0)}% match`,
    })),
    ...reports.slice(0, 4).map((item) => ({
      key: `r${item.id}`,
      kind:
        item.interview_type === "hr"
          ? "Behavioral interview"
          : "Technical interview",
      title: item.target_role,
      detail: "Interview report",
      date: item.interview_date,
      to: `/reports/${item.session_id}`,
      value:
        item.overall_score == null
          ? "Score unavailable"
          : `${item.overall_score.toFixed(0)} / 100`,
    })),
  ]
    .sort((a, b) => Date.parse(b.date) - Date.parse(a.date))
    .slice(0, 5);

  return (
    <div className="prep-dashboard">
      <header className="command-heading">
        <div>
          <p className="pm-eyebrow">Your preparation</p>
          <h1>{goal}</h1>
          <p>
            {user?.full_name
              ? `${user.full_name.split(" ")[0]}, here is your next step.`
              : "A clear next step, grounded in your preparation."}
          </p>
        </div>
        <Link to="/profile" className="command-text-link">
          Edit preparation goal <ArrowRightIcon size={14} />
        </Link>
      </header>
      {hasError && (
        <div className="pm-alert-error" role="alert">
          <span>
            Some workspace information could not be loaded. Available
            information is shown below.
          </span>
          <button
            className="btn btn-secondary btn-sm"
            onClick={() => void loadOverview()}
            disabled={loading}
          >
            {loading ? "Retrying..." : "Retry"}
          </button>
        </div>
      )}
      <section
        className="command-next"
        aria-label="Recommended next action"
        aria-busy={loading}
      >
        <div className="command-next-main">
          <p className="pm-eyebrow">
            {loading ? "Updating your preparation" : next.eyebrow}
          </p>
          <h2>{loading ? "Finding your next useful step" : next.title}</h2>
          <p>
            {loading
              ? "Your saved work is loading. Each section becomes available independently."
              : next.description}
          </p>
          {loading ? (
            <p role="status" className="command-loading">
              <span className="pm-spinner" aria-hidden="true" />
              Loading your next action...
            </p>
          ) : (
            <Link to={next.to} className="btn btn-primary">
              {next.label}
              <ArrowRightIcon size={16} />
            </Link>
          )}
        </div>
        <div className="command-next-note">
          <BookOpenIcon size={22} />
          <strong>
            {recommended ? "From your feedback" : "Your preparation context"}
          </strong>
          <p>
            {loading
              ? "Your resume, interview feedback and practice gaps shape this recommendation."
              : next.reason}
          </p>
        </div>
      </section>
      <section className="command-evidence" aria-label="Preparation snapshot">
        <article aria-busy={pending.analyses}>
          <div className="command-section-head">
            <h2>
              <FileTextIcon size={17} />
              Resume alignment
            </h2>
            <Link to="/history">Saved resumes</Link>
          </div>
          {pending.analyses && <p role="status">Loading resume history...</p>}
          {failures.analyses && (
            <p role="status">
              Resume history unavailable.
              {analyses.length > 0
                ? " Previously loaded entries remain below."
                : ""}
            </p>
          )}
          {analysis ? (
            <>
              <div className="command-measure">
                <strong>
                  {analysis.match_score.toFixed(0)}
                  <small>%</small>
                </strong>
                <span>match to {analysis.job_role}</span>
              </div>
              <Link
                className="command-work-link"
                to={`/history/${analysis.id}`}
              >
                {analysis.filename}
                <ArrowRightIcon size={14} />
              </Link>
            </>
          ) : (
            !pending.analyses &&
            !failures.analyses && (
              <p>
                {analyses.length
                  ? "No resume analysis for this goal yet. Choose a saved resume or analyze one for this goal."
                  : "No resume analyses yet. Upload a PDF to evaluate matched skills."}
              </p>
            )
          )}
          <span className="command-caption">
            Recent Resume Profiles
            {!pending.analyses && !failures.analyses
              ? `: ${analyses.length} shown (up to 10)`
              : ""}
          </span>
        </article>
        <article aria-busy={pending.reports}>
          <div className="command-section-head">
            <h2>
              <MessageSquareIcon size={17} />
              Interview performance
            </h2>
            <Link to="/reports">All reports</Link>
          </div>
          {pending.reports && <p role="status">Loading report history...</p>}
          {failures.reports && (
            <p role="status">
              Report history unavailable.
              {reports.length > 0
                ? " Previously loaded entries remain below."
                : ""}
            </p>
          )}
          {report ? (
            <>
              <div className="command-measure">
                <strong>
                  {report.overall_score == null
                    ? "Unavailable"
                    : `${report.overall_score.toFixed(0)} / 100`}
                </strong>
                <span>
                  {report.interview_type === "hr" ? "Behavioral" : "Technical"}{" "}
                  practice score
                  {report.status === "partial" ? " - partial grading" : ""}
                </span>
              </div>
              <Link
                className="command-work-link"
                to={`/reports/${report.session_id}`}
              >
                Review latest feedback
                <ArrowRightIcon size={14} />
              </Link>
            </>
          ) : (
            !pending.reports &&
            !failures.reports && (
              <p>
                {reports.length
                  ? "No interview report for this goal yet. Your other reports remain available."
                  : "No interview reports yet. Your first completed round will give you a starting point."}
              </p>
            )
          )}
          <span className="command-caption">
            Recent Reports
            {!pending.reports && !failures.reports
              ? `: ${reports.length} shown (up to 10)`
              : ""}
          </span>
        </article>
      </section>
      <div className="command-lower">
        <section className="command-activity">
          <div className="command-section-head">
            <h2>Recent activity</h2>
            <span className="command-caption">Your saved work</span>
          </div>
          {activity.length ? (
            <ul>
              {activity.map((item) => (
                <li key={item.key}>
                  <div>
                    <span className="command-caption">
                      {item.kind} &middot; {formatDateTime(item.date)}
                    </span>
                    <Link to={item.to}>
                      {item.title}
                      <ArrowRightIcon size={14} />
                    </Link>
                    <span className="command-file">{item.detail}</span>
                  </div>
                  <span className="command-activity-value">{item.value}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p>
              {loading
                ? "Loading recent activity..."
                : hasError
                  ? "Saved activity is unavailable while we reconnect."
                  : "Your preparation starts here. Analyses and interview reports will appear as you build them."}
            </p>
          )}
        </section>
        <section
          className="command-practice"
          aria-busy={pending.recommendations}
        >
          <div className="command-section-head">
            <h2>Practice focus</h2>
            <Link to="/practice">Practice Hub</Link>
          </div>
          {pending.recommendations && (
            <p role="status">Loading practice recommendations...</p>
          )}
          {failures.recommendations && (
            <p role="status">
              Practice recommendations could not be refreshed. Previously loaded
              recommendations remain available.
            </p>
          )}
          {relevant.length ? (
            <ul>
              {relevant.map((rec) => (
                <li key={`${rec.source_report_id}-${rec.topic}`}>
                  <span className="command-caption">
                    {rec.interview_type === "hr" ? "Behavioral" : "Technical"}{" "}
                    &middot; {rec.priority} priority
                  </span>
                  <Link
                    to={practiceLink(
                      rec.topic,
                      {
                        interviewType: rec.interview_type,
                        reportId: rec.source_report_id,
                        targetRole: rec.target_role,
                      },
                      rec.observed_gap,
                    )}
                  >
                    {rec.topic}
                    <ArrowRightIcon size={14} />
                  </Link>
                  <p>{rec.suggested_action || rec.observed_gap}</p>
                </li>
              ))}
            </ul>
          ) : (
            !pending.recommendations &&
            !failures.recommendations && (
              <p>
                {recommendations.length
                  ? "Your available recommendations are for other roles. Open Practice Hub to explore them."
                  : "Focused recommendations will appear after an interview. You can also choose your own practice topic."}
              </p>
            )
          )}
        </section>
      </div>
    </div>
  );
}
