import { useCallback, useEffect, useRef, useState } from "react";
import {
  Link,
  useNavigate,
  useParams,
  useSearchParams,
} from "react-router-dom";
import { listInterviewReports } from "../services/report.service";
import { practiceLink } from "../utils/practiceNavigation";
import ConfirmDialog from "../components/ConfirmDialog";
import { ArrowRightIcon, BookOpenIcon } from "../components/Icons";
import { useAuth } from "../hooks/useAuth";
import { ApiError } from "../services/api";
import {
  createPracticeSession,
  deletePracticeSession,
  generateNextQuestion,
  getPracticeRecommendations,
  getPracticeSession,
  revealHint,
  revealReference,
  submitPracticeAttempt,
} from "../services/practice.service";
import type {
  AssistanceLevel,
  InterviewType,
  PracticeAttempt,
  PracticeDifficulty,
  PracticeQuestion,
  PracticeRecommendationItem,
  PracticeSessionDetail,
  PracticeSessionSummary,
} from "../types/practice";
import { listPracticeSessions } from "../services/practice.service";
import { formatDateTime } from "../utils/formatters";
import "./Practice.css";
import "./PracticeLearning.css";
import PracticeCoaching from "../features/practice/PracticeCoaching";
import {
  confirmDiscardAnswer,
  useUnsentAnswerWarning,
} from "../hooks/useUnsentAnswerWarning";

export default function PracticeWorkspace() {
  const { sessionId } = useParams<{ sessionId?: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { logout } = useAuth();

  // Session state
  const [session, setSession] = useState<PracticeSessionDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Active question state
  const [activeQuestionIndex, setActiveQuestionIndex] = useState(0);
  const [answerText, setAnswerText] = useState("");
  const answerRef = useRef<HTMLTextAreaElement>(null);
  const operationRef = useRef(false);
  const focusCoaching = useRef(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [revealingHint, setRevealingHint] = useState(false);
  const [revealingRef, setRevealingRef] = useState(false);
  const [generatingSimilar, setGeneratingSimilar] = useState(false);
  const [showRefConfirm, setShowRefConfirm] = useState(false);

  // Hub state (when no sessionId)
  const [summaries, setSummaries] = useState<PracticeSessionSummary[]>([]);
  const [recommendations, setRecommendations] = useState<
    PracticeRecommendationItem[]
  >([]);
  const [hubFailures, setHubFailures] = useState({
    sessions: false,
    recommendations: false,
  });
  const [returnSessionId, setReturnSessionId] = useState<string | null>(null);
  const startingQuery = useRef<string | null>(null);
  const [queryAttempt, setQueryAttempt] = useState(0);
  const [hubTopic, setHubTopic] = useState("Authentication & Authorization");
  const [hubType, setHubType] = useState<InterviewType>("technical");
  const [hubDifficulty, setHubDifficulty] =
    useState<PracticeDifficulty>("medium");
  const [startingSession, setStartingSession] = useState(false);
  const [pendingDeleteSession, setPendingDeleteSession] = useState<
    string | null
  >(null);
  const [deleting, setDeleting] = useState(false);

  const handleUnauthorized = useCallback(() => {
    logout();
    navigate("/login", { replace: true });
  }, [logout, navigate]);

  // Load session or Hub
  const loadSession = useCallback(
    async (id: string) => {
      setLoading(true);
      setError(null);
      try {
        const data = await getPracticeSession(id);
        setSession(data);
        setActiveQuestionIndex(Math.max(0, (data.questions?.length ?? 1) - 1));
      } catch (err) {
        if (err instanceof ApiError && err.status === 401) {
          handleUnauthorized();
          return;
        }
        setError(
          err instanceof Error
            ? err.message
            : "Failed to load practice session.",
        );
      } finally {
        setLoading(false);
        setStartingSession(false);
      }
    },
    [handleUnauthorized],
  );

  const loadHub = useCallback(async () => {
    setLoading(true);
    setError(null);
    const results = await Promise.allSettled([
      listPracticeSessions(20),
      getPracticeRecommendations(5),
    ]);
    if (
      results.some(
        (result) =>
          result.status === "rejected" &&
          result.reason instanceof ApiError &&
          result.reason.status === 401,
      )
    ) {
      handleUnauthorized();
      setLoading(false);
      return;
    }
    const [sessionsResult, recommendationsResult] = results;
    if (sessionsResult.status === "fulfilled")
      setSummaries(sessionsResult.value);
    if (recommendationsResult.status === "fulfilled")
      setRecommendations(recommendationsResult.value);
    setHubFailures({
      sessions: sessionsResult.status === "rejected",
      recommendations: recommendationsResult.status === "rejected",
    });
    if (results.some((result) => result.status === "rejected"))
      setError(
        "Some practice information could not be loaded. Available sessions and recommendations are shown below.",
      );
    setLoading(false);
  }, [handleUnauthorized]);

  // Automatic session creation from query params (e.g. from report click)
  useEffect(() => {
    const qTopic = searchParams.get("topic");
    if (!sessionId && qTopic) {
      if (startingQuery.current === searchParams.toString()) return;
      startingQuery.current = searchParams.toString();
      const qType = (searchParams.get("type") as InterviewType) || "technical";
      const qGap = searchParams.get("gap") || undefined;
      const qReportId = searchParams.get("reportId")
        ? parseInt(searchParams.get("reportId")!, 10)
        : undefined;

      async function initFromQuery() {
        setStartingSession(true);
        setError(null);
        try {
          const newSession = await createPracticeSession({
            topic: qTopic!,
            interview_type: qType,
            weakness_context: qGap,
            source_report_id: qReportId,
            target_role: searchParams.get("role") || undefined,
            difficulty: "medium",
          });
          setSession(newSession);
          setActiveQuestionIndex((newSession.questions?.length ?? 1) - 1);
          setStartingSession(false);
          setLoading(false);
          navigate(`/practice/${newSession.id}?${searchParams.toString()}`, {
            replace: true,
          });
        } catch (err) {
          setError(
            err instanceof Error
              ? err.message
              : "Could not initialize practice session.",
          );
          setStartingSession(false);
          setLoading(false);
        }
      }
      void initFromQuery();
      return;
    }

    if (sessionId) {
      startingQuery.current = null;
      if (session?.id === sessionId && (session.questions?.length ?? 0) > 0) {
        setLoading(false);
        setStartingSession(false);
        return;
      }
      void loadSession(sessionId);
    } else {
      setSession(null);
      void loadHub();
    }
  }, [
    sessionId,
    searchParams,
    loadSession,
    loadHub,
    navigate,
    session?.id,
    session?.questions?.length,
    queryAttempt,
  ]);

  // Active question & attempt
  const currentQuestion: PracticeQuestion | undefined =
    session?.questions?.[activeQuestionIndex];
  const attempts: PracticeAttempt[] = currentQuestion?.attempts || [];
  const latestAttempt: PracticeAttempt | undefined =
    attempts[attempts.length - 1];

  useEffect(() => {
    if (focusCoaching.current && latestAttempt) {
      focusCoaching.current = false;
      document.getElementById("coaching-title")?.focus();
    }
  }, [latestAttempt?.id]);
  const busy = submitting || revealingHint || revealingRef || generatingSimilar;
  const dirty =
    Boolean(answerText.trim()) &&
    answerText.trim() !== latestAttempt?.answer_text.trim();
  useUnsentAnswerWarning(Boolean(sessionId) && dirty);
  function improveAnswer() {
    if (!answerText.trim()) setAnswerText(latestAttempt?.answer_text || "");
    answerRef.current?.focus();
    answerRef.current?.scrollIntoView({ block: "center", behavior: "auto" });
  }

  useEffect(() => {
    let cancelled = false;
    setReturnSessionId(null);
    if (!session?.source_report_id) return;
    const supplied = searchParams.get("reportSessionId");
    if (
      supplied &&
      Number(searchParams.get("reportId")) === session.source_report_id
    ) {
      setReturnSessionId(supplied);
      return;
    }
    void listInterviewReports(100)
      .then((reports) => {
        if (!cancelled)
          setReturnSessionId(
            reports.find((report) => report.id === session.source_report_id)
              ?.session_id || null,
          );
      })
      .catch(() => {
        /* Keep the honest Reports-list fallback if the source is unavailable. */
      });
    return () => {
      cancelled = true;
    };
  }, [session?.source_report_id, searchParams]);

  // Determine current assistance level
  function getAssistanceLevel(): AssistanceLevel {
    if (!currentQuestion) return "independent";
    if (currentQuestion.reference_revealed) return "reference_assisted";
    if (currentQuestion.hints_revealed?.length > 0) return "hint_assisted";
    return "independent";
  }

  // Handle Hint Reveal
  async function handleRevealNextHint() {
    if (!currentQuestion || operationRef.current) return;
    const currentHints = currentQuestion.hints_revealed || [];
    const nextLevel = currentHints.includes(1) ? 2 : 1;
    if (currentHints.includes(nextLevel)) return;

    operationRef.current = true;
    setActionError(null);
    setRevealingHint(true);
    try {
      const res = await revealHint(currentQuestion.id, nextLevel);
      setSession((prev) => {
        if (!prev) return prev;
        const updatedQuestions = [...prev.questions];
        const q = { ...updatedQuestions[activeQuestionIndex] };
        q.hints_revealed = res.hints_revealed;
        q.revealed_hints = {
          ...q.revealed_hints,
          [String(nextLevel)]: res.hint_text,
        };
        updatedQuestions[activeQuestionIndex] = q;
        return { ...prev, questions: updatedQuestions };
      });
    } catch (err) {
      setActionError(
        err instanceof Error ? err.message : "Failed to reveal hint.",
      );
    } finally {
      operationRef.current = false;
      setRevealingHint(false);
    }
  }

  // Handle Reference Reveal
  async function handleConfirmRevealRef() {
    if (!currentQuestion || operationRef.current) return;
    operationRef.current = true;
    setActionError(null);
    setRevealingRef(true);
    setShowRefConfirm(false);
    try {
      const res = await revealReference(currentQuestion.id);
      setSession((prev) => {
        if (!prev) return prev;
        const updatedQuestions = [...prev.questions];
        const q = { ...updatedQuestions[activeQuestionIndex] };
        q.reference_revealed = true;
        q.reference_answer = res.reference_answer;
        q.reference_explanation = res.reference_explanation;
        updatedQuestions[activeQuestionIndex] = q;
        return { ...prev, questions: updatedQuestions };
      });
    } catch (err) {
      setActionError(
        err instanceof Error
          ? err.message
          : "Failed to reveal reference answer.",
      );
    } finally {
      operationRef.current = false;
      setRevealingRef(false);
    }
  }

  // Handle Submit Answer
  async function handleSubmitAnswer() {
    if (!currentQuestion || !answerText.trim() || operationRef.current) return;
    operationRef.current = true;
    setActionError(null);
    setSubmitting(true);
    try {
      const newAttempt = await submitPracticeAttempt(currentQuestion.id, {
        answer_text: answerText.trim(),
      });
      focusCoaching.current = true;
      setSession((prev) => {
        if (!prev) return prev;
        const updatedQuestions = [...prev.questions];
        const q = { ...updatedQuestions[activeQuestionIndex] };
        q.attempts = [...(q.attempts || []), newAttempt];
        updatedQuestions[activeQuestionIndex] = q;
        return { ...prev, questions: updatedQuestions };
      });
    } catch (err) {
      setActionError(
        err instanceof Error ? err.message : "Failed to evaluate answer.",
      );
    } finally {
      operationRef.current = false;
      setSubmitting(false);
    }
  }

  // Handle Generate Similar Question
  async function handleGenerateSimilar() {
    if (!session || operationRef.current || !confirmDiscardAnswer(dirty))
      return;
    operationRef.current = true;
    setActionError(null);
    setGeneratingSimilar(true);
    try {
      const newQ = await generateNextQuestion(session.id, {
        difficulty:
          (currentQuestion?.difficulty as PracticeDifficulty) || "medium",
      });
      setSession((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          questions: [...prev.questions, newQ],
        };
      });
      setActiveQuestionIndex(session.questions.length);
      setAnswerText("");
    } catch (err) {
      setActionError(
        err instanceof Error
          ? err.message
          : "Failed to generate similar question.",
      );
    } finally {
      operationRef.current = false;
      setGeneratingSimilar(false);
    }
  }

  // Start new session from Hub
  async function handleStartHubSession(
    topic: string,
    type: InterviewType,
    diff: PracticeDifficulty,
  ) {
    setStartingSession(true);
    setError(null);
    try {
      const newSession = await createPracticeSession({
        topic,
        interview_type: type,
        difficulty: diff,
      });
      setSession(newSession);
      setActiveQuestionIndex((newSession.questions?.length ?? 1) - 1);
      setStartingSession(false);
      setLoading(false);
      navigate(`/practice/${newSession.id}`);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not create practice session.",
      );
      setStartingSession(false);
    }
  }

  // Delete session from Hub
  async function handleConfirmDelete() {
    if (!pendingDeleteSession || deleting) return;
    setDeleting(true);
    try {
      await deletePracticeSession(pendingDeleteSession);
      setSummaries((prev) => prev.filter((s) => s.id !== pendingDeleteSession));
      setPendingDeleteSession(null);
    } catch (err) {
      alert(
        err instanceof Error
          ? err.message
          : "Failed to delete practice session.",
      );
    } finally {
      setDeleting(false);
    }
  }

  // RENDER: Loading or Error
  if (loading || startingSession) {
    return (
      <div className="practice-page">
        <div className="pm-status-banner" role="status">
          <span className="pm-spinner" aria-hidden="true" />
          <h2>
            {startingSession
              ? "Preparing Your Practice Session..."
              : sessionId
                ? "Loading practice session..."
                : "Loading practice hub..."}
          </h2>
          <p style={{ color: "#94a3b8" }}>
            Your saved questions and attempts will appear here.
          </p>
        </div>
      </div>
    );
  }

  if (error && sessionId && (!session || session.id !== sessionId)) {
    return (
      <div className="practice-page">
        <div className="pm-card" role="alert" style={{ padding: "2rem" }}>
          <h2 style={{ color: "#ef4444" }}>Could Not Load Practice</h2>
          <p style={{ color: "#94a3b8", marginBottom: "1.5rem" }}>{error}</p>
          <button
            className="btn btn-secondary"
            onClick={() => void loadSession(sessionId)}
          >
            Retry
          </button>
          <Link to="/practice" className="btn btn-secondary">
            Return to Practice Hub
          </Link>
        </div>
      </div>
    );
  }

  // =========================================================================
  // VIEW A: PRACTICE HUB (when no sessionId) — Editorial warm layout
  // =========================================================================
  if (!sessionId) {
    const featuredRec = recommendations[0] ?? null;
    const additionalRecs = recommendations.slice(1);

    return (
      <div className="practice-page">
        {error && (
          <div className="pm-alert-error" role="alert">
            <span>{error}</span>
            <button
              className="btn btn-secondary"
              onClick={() => {
                if (searchParams.get("topic")) {
                  startingQuery.current = null;
                  setQueryAttempt((value) => value + 1);
                } else void loadHub();
              }}
            >
              Retry
            </button>
          </div>
        )}
        {hubFailures.recommendations && (
          <p role="status">
            Recommendations unavailable. You can still choose a topic or resume
            a session.
          </p>
        )}
        {/* Open page header — no card border */}
        <header className="practice-hub-header">
          <div>
            <p className="practice-hub-eyebrow">Guided Learning</p>
            <h1 className="practice-hub-title">Practice Studio</h1>
            <p className="practice-hub-sub">
              Master interview answers through progressive hints, AI coaching,
              and targeted gap practice.
            </p>
          </div>
        </header>

        {/* Featured recommendation in warm editorial band */}
        {featuredRec && (
          <section
            className="practice-featured-section"
            aria-label="Recommended for you"
          >
            <p className="practice-featured-label">Recommended for You</p>
            <div className="practice-featured-topic">
              <div className="practice-featured-main">
                <div className="practice-featured-badges">
                  <span
                    className="badge badge-accent"
                    style={{ textTransform: "capitalize" }}
                  >
                    {featuredRec.interview_type}
                  </span>
                  <span
                    className={`badge ${featuredRec.priority === "high" ? "badge-danger" : "badge-warning"}`}
                  >
                    {featuredRec.priority} priority
                  </span>
                </div>
                <h2 className="practice-featured-topic-name">
                  {featuredRec.topic}
                </h2>
                <p className="practice-featured-gap">
                  {featuredRec.observed_gap}
                </p>
                <button
                  className="btn btn-primary"
                  onClick={() =>
                    navigate(
                      practiceLink(
                        featuredRec.topic,
                        {
                          interviewType: featuredRec.interview_type,
                          reportId: featuredRec.source_report_id,
                          targetRole: featuredRec.target_role,
                        },
                        featuredRec.observed_gap,
                      ),
                    )
                  }
                >
                  <span>Practice Now</span>
                  <ArrowRightIcon size={14} />
                </button>
              </div>
            </div>

            {/* Additional recommendations as compact rows */}
            {additionalRecs.length > 0 && (
              <div className="practice-additional-recs">
                {additionalRecs.map((rec, idx) => (
                  <div key={idx + 1} className="practice-compact-rec-row">
                    <div className="practice-compact-rec-info">
                      <strong className="practice-compact-rec-topic">
                        {rec.topic}
                      </strong>
                      <span className="practice-compact-rec-gap">
                        {rec.observed_gap}
                      </span>
                    </div>
                    <div className="practice-compact-rec-actions">
                      <span
                        className="badge"
                        style={{ textTransform: "capitalize" }}
                      >
                        {rec.interview_type}
                      </span>
                      <button
                        className="practice-compact-cta"
                        onClick={() =>
                          navigate(
                            practiceLink(
                              rec.topic,
                              {
                                interviewType: rec.interview_type,
                                reportId: rec.source_report_id,
                                targetRole: rec.target_role,
                              },
                              rec.observed_gap,
                            ),
                          )
                        }
                      >
                        Practice →
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        )}

        {/* Start Practice — open form section, not inside a card */}
        <section
          className="practice-start-section"
          aria-label="Start a new practice session"
        >
          <h2 className="practice-start-heading">Start Targeted Practice</h2>
          <p className="practice-start-sub">
            Choose any concept or topic to begin self-paced practice with
            instant AI coaching.
          </p>
          <div className="practice-start-form">
            <div className="practice-start-field practice-start-field--wide">
              <label htmlFor="practice-topic" className="field-label">
                Topic / Concept
              </label>
              <input
                type="text"
                className="pm-input"
                value={hubTopic}
                onChange={(e) => setHubTopic(e.target.value)}
                id="practice-topic"
                placeholder="e.g. SQL Joins, System Design, Conflict Resolution"
              />
            </div>
            <div className="practice-start-field">
              <label htmlFor="practice-type" className="field-label">
                Interview Type
              </label>
              <select
                className="pm-select"
                id="practice-type"
                value={hubType}
                onChange={(e) => setHubType(e.target.value as InterviewType)}
              >
                <option value="technical">Technical Interview</option>
                <option value="hr">HR / Behavioral</option>
              </select>
            </div>
            <div className="practice-start-field">
              <label htmlFor="practice-difficulty" className="field-label">
                Difficulty
              </label>
              <select
                className="pm-select"
                id="practice-difficulty"
                value={hubDifficulty}
                onChange={(e) =>
                  setHubDifficulty(e.target.value as PracticeDifficulty)
                }
              >
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
            </div>
            <div className="practice-start-field practice-start-field--btn">
              <label className="field-label" style={{ visibility: "hidden" }}>
                Launch
              </label>
              <button
                className="btn btn-primary"
                onClick={() =>
                  handleStartHubSession(hubTopic, hubType, hubDifficulty)
                }
                disabled={!hubTopic.trim()}
              >
                <BookOpenIcon size={16} />
                <span>Launch Studio</span>
              </button>
            </div>
          </div>
        </section>

        {/* History: plain list section, no card wrapper */}
        {hubFailures.sessions && (
          <p role="status">
            Practice sessions unavailable. Your saved sessions have not been
            deleted.
          </p>
        )}
        {summaries.length > 0 && (
          <section
            className="practice-history-section"
            aria-label="Your practice sessions"
          >
            <div className="practice-history-head">
              <h2 className="dash-section-heading">Your Sessions</h2>
            </div>
            <div className="practice-history-rows">
              {summaries.map((s) => (
                <div key={s.id} className="practice-history-row">
                  <div className="practice-history-row-info">
                    <div className="practice-history-row-title">
                      <strong>{s.topic}</strong>
                      <span
                        className="badge badge-neutral"
                        style={{ textTransform: "capitalize" }}
                      >
                        {s.interview_type}
                      </span>
                    </div>
                    <p className="practice-history-row-meta">
                      {s.question_count}{" "}
                      {s.question_count === 1 ? "question" : "questions"} ·{" "}
                      {s.attempt_count}{" "}
                      {s.attempt_count === 1 ? "attempt" : "attempts"} ·{" "}
                      {formatDateTime(s.created_at)}
                    </p>
                  </div>
                  <div className="practice-history-row-actions">
                    <Link
                      to={`/practice/${s.id}`}
                      className="btn btn-secondary btn-sm"
                    >
                      <span>Resume</span>
                      <ArrowRightIcon size={14} />
                    </Link>
                    <button
                      className="btn btn-danger-outline btn-sm"
                      onClick={() => setPendingDeleteSession(s.id)}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        <ConfirmDialog
          open={Boolean(pendingDeleteSession)}
          title="Delete Practice Session?"
          description="Are you sure you want to delete this practice session? All associated questions and coaching attempts will be permanently removed."
          confirmLabel="Delete Session"
          busy={deleting}
          onConfirm={handleConfirmDelete}
          onCancel={() => setPendingDeleteSession(null)}
        />
      </div>
    );
  }

  // =========================================================================
  // VIEW B: ACTIVE PRACTICE STUDIO (when sessionId is present)
  // =========================================================================
  const assistanceLevel = getAssistanceLevel();

  return (
    <div className="practice-page practice-learning">
      <header className="learning-header">
        <nav aria-label="Practice navigation" className="learning-nav">
          <Link to="/practice" className="practice-back-link">
            Back to Practice Hub
          </Link>
          {session?.source_report_id && (
            <Link
              to={
                returnSessionId
                  ? `/reports/${encodeURIComponent(returnSessionId)}`
                  : "/reports"
              }
              className="practice-report-link"
            >
              {returnSessionId ? "Return to Report" : "Interview Reports"}
            </Link>
          )}
        </nav>
        <div className="learning-title-row">
          <div>
            <p className="learning-section-label">Practice workspace</p>
            <h1>{session?.topic || "Your practice session"}</h1>
            <p className="learning-caption">
              {session?.interview_type === "hr"
                ? "HR / Behavioral"
                : "Technical"}{" "}
              / {session?.target_role}
            </p>
          </div>
          {session && session.questions.length > 1 && (
            <div className="learning-question-picker">
              <label htmlFor="practice-question-picker">Saved question</label>
              <select
                id="practice-question-picker"
                className="pm-select"
                value={activeQuestionIndex}
                disabled={busy}
                onChange={(e) => {
                  const index = Number(e.target.value);
                  if (!confirmDiscardAnswer(dirty)) return;
                  setActiveQuestionIndex(index);
                  setAnswerText("");
                  setActionError(null);
                }}
              >
                {session.questions.map((q, index) => (
                  <option key={q.id} value={index}>
                    Question {index + 1} / {q.difficulty}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>
      </header>
      {actionError && (
        <div className="pm-alert-error" role="alert">
          <div>
            <strong>That action could not be completed.</strong>
            <p>{actionError}</p>
            <p>Your answer is still here. Use the same action to retry.</p>
          </div>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => setActionError(null)}
          >
            Dismiss
          </button>
        </div>
      )}
      {!currentQuestion ? (
        <section className="learning-empty">
          <h2>No questions in this session yet</h2>
          <p>Generate a question to begin. Your session is saved.</p>
          <button
            type="button"
            className="btn btn-primary"
            disabled={busy}
            onClick={handleGenerateSimilar}
          >
            {generatingSimilar
              ? "Generating question..."
              : "Generate a question"}
          </button>
        </section>
      ) : (
        <div className="learning-grid">
          <div className="learning-main">
            <section
              className="learning-question"
              aria-labelledby="practice-question-title"
            >
              <div className="learning-question-meta">
                <span className="learning-section-label">
                  01 / Question {activeQuestionIndex + 1}
                </span>
                <span>
                  {currentQuestion.difficulty} / {attempts.length}{" "}
                  {attempts.length === 1 ? "attempt" : "attempts"}
                </span>
              </div>
              <h2
                id="practice-question-title"
                className="practice-question-text"
              >
                {currentQuestion.question_text}
              </h2>
              {session?.weakness_context && (
                <p className="learning-growth">
                  <strong>Practice focus:</strong> {session.weakness_context}
                </p>
              )}
              <details className="learning-help">
                <summary>Need a starting point? Hints & example</summary>
                <p className="learning-caption">
                  Hints and examples are recorded as assistance for this
                  question, including later attempts.
                </p>
                <div className="learning-help-actions">
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={handleRevealNextHint}
                    disabled={
                      busy || (currentQuestion.hints_revealed?.length ?? 0) >= 2
                    }
                  >
                    {revealingHint
                      ? "Loading hint..."
                      : (currentQuestion.hints_revealed?.length ?? 0) === 0
                        ? "Get Hint 1 (Direction)"
                        : currentQuestion.hints_revealed.length === 1
                          ? "Get Hint 2 (Structure)"
                          : "All hints revealed"}
                  </button>
                  {!currentQuestion.reference_revealed && (
                    <button
                      type="button"
                      className="btn btn-secondary"
                      onClick={() => setShowRefConfirm(true)}
                      disabled={busy}
                    >
                      {revealingRef
                        ? "Loading example..."
                        : "Show Reference Answer"}
                    </button>
                  )}
                </div>
                {currentQuestion.hints_revealed?.map((level) => (
                  <section key={level} className="learning-hint">
                    <h3>
                      Hint {level} / {level === 1 ? "Direction" : "Structure"}
                    </h3>
                    <p>{currentQuestion.revealed_hints[String(level)]}</p>
                  </section>
                ))}
                {currentQuestion.reference_revealed && (
                  <section className="learning-hint">
                    <h3>AI-generated example / Reference-assisted</h3>
                    <p className="learning-caption">
                      One possible response, not an authoritative benchmark.
                      Verify claims and adapt it to your experience.
                    </p>
                    <p className="learning-example">
                      {currentQuestion.reference_answer}
                    </p>
                    {currentQuestion.reference_explanation && (
                      <p>{currentQuestion.reference_explanation}</p>
                    )}
                    <p className="learning-caption">
                      Future submissions for this question are recorded as
                      reference-assisted.
                    </p>
                  </section>
                )}
              </details>
            </section>
            <form
              className="learning-editor"
              aria-busy={submitting}
              onSubmit={(event) => {
                event.preventDefault();
                void handleSubmitAnswer();
              }}
            >
              <div className="learning-section-label">
                02 / {latestAttempt ? "Improved attempt" : "Your answer"}
              </div>
              <div className="learning-editor-heading">
                <label htmlFor="practice-answer">
                  {latestAttempt
                    ? "Refine your response"
                    : "Build your response"}
                </label>
                <span className="learning-assistance">
                  {assistanceLevel === "independent"
                    ? "Independent practice"
                    : assistanceLevel === "hint_assisted"
                      ? "Hint-assisted"
                      : "Reference-assisted"}
                </span>
              </div>
              <textarea
                ref={answerRef}
                id="practice-answer"
                aria-label="Your practice answer"
                aria-describedby="practice-draft-note"
                className="practice-textarea"
                placeholder="Explain your approach in your own words. Include a concrete example."
                value={answerText}
                onChange={(e) => setAnswerText(e.target.value)}
                disabled={busy}
                rows={9}
              />
              <div className="practice-editor-meta">
                <span>
                  {answerText.trim().split(/\s+/).filter(Boolean).length} words
                </span>
                <span>Attempt {attempts.length + 1}</span>
              </div>
              <p id="practice-draft-note" className="learning-caption">
                Unsubmitted edits are temporary. Submitted attempts are saved to
                this session.
              </p>
              <div className="learning-editor-actions">
                {latestAttempt && !answerText && (
                  <button
                    type="button"
                    className="btn btn-secondary"
                    disabled={busy}
                    onClick={improveAnswer}
                  >
                    Use last attempt
                  </button>
                )}
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={!answerText.trim() || busy}
                >
                  {submitting
                    ? "Getting coaching..."
                    : latestAttempt
                      ? "Submit improved attempt"
                      : "Submit for coaching"}
                </button>
              </div>
            </form>
          </div>
          {latestAttempt ? (
            <PracticeCoaching
              attempt={latestAttempt}
              previous={attempts[attempts.length - 2]}
              onImprove={improveAnswer}
              onNext={() => void handleGenerateSimilar()}
              busy={busy}
              generating={generatingSimilar}
            />
          ) : (
            <aside className="learning-coach learning-coach-empty">
              <div className="learning-section-label">03 / Coaching</div>
              <h2>Make the first attempt yours</h2>
              <p>
                Submit an answer to see what worked, what to strengthen, and a
                focused next step.
              </p>
              <p className="learning-caption">
                You can revise the same answer after coaching. Hints are
                available when you need a starting point.
              </p>
            </aside>
          )}
        </div>
      )}
      <ConfirmDialog
        open={showRefConfirm}
        title="Reveal Reference Answer?"
        description="Viewing this AI-generated example marks future attempts on this question as reference-assisted. It is one possible approach, not an authoritative answer. Use it to learn, then explain in your own words."
        confirmLabel="Reveal Answer"
        busy={revealingRef}
        onConfirm={handleConfirmRevealRef}
        onCancel={() => setShowRefConfirm(false)}
      />
    </div>
  );
}
