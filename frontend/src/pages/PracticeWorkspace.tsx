import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";
import ConfirmDialog from "../components/ConfirmDialog";
import {
  ArrowRightIcon,
  BookOpenIcon,
  CheckCircleIcon,
  ChevronDownIcon,
  CodeIcon,
  LightbulbIcon,
  RotateCcwIcon,
  SparklesIcon,
  UsersIcon,
} from "../components/Icons";
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
  const [submitting, setSubmitting] = useState(false);
  const [revealingHint, setRevealingHint] = useState(false);
  const [revealingRef, setRevealingRef] = useState(false);
  const [generatingSimilar, setGeneratingSimilar] = useState(false);
  const [showRefConfirm, setShowRefConfirm] = useState(false);

  // Hub state (when no sessionId)
  const [summaries, setSummaries] = useState<PracticeSessionSummary[]>([]);
  const [recommendations, setRecommendations] = useState<PracticeRecommendationItem[]>([]);
  const [hubTopic, setHubTopic] = useState("Authentication & Authorization");
  const [hubType, setHubType] = useState<InterviewType>("technical");
  const [hubDifficulty, setHubDifficulty] = useState<PracticeDifficulty>("medium");
  const [startingSession, setStartingSession] = useState(false);
  const [pendingDeleteSession, setPendingDeleteSession] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);

  const handleUnauthorized = useCallback(() => {
    logout();
    navigate("/login", { replace: true });
  }, [logout, navigate]);

  // Load session or Hub
  const loadSession = useCallback(async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await getPracticeSession(id);
      setSession(data);
      setActiveQuestionIndex((data.questions?.length ?? 1) - 1);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        handleUnauthorized();
        return;
      }
      setError(err instanceof Error ? err.message : "Failed to load practice session.");
    } finally {
      setLoading(false);
    }
  }, [handleUnauthorized]);

  const loadHub = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [sumList, recList] = await Promise.all([
        listPracticeSessions(20),
        getPracticeRecommendations(5),
      ]);
      setSummaries(sumList);
      setRecommendations(recList);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        handleUnauthorized();
        return;
      }
      setError(err instanceof Error ? err.message : "Failed to load practice history.");
    } finally {
      setLoading(false);
    }
  }, [handleUnauthorized]);

  // Automatic session creation from query params (e.g. from report click)
  useEffect(() => {
    const qTopic = searchParams.get("topic");
    if (!sessionId && qTopic) {
      const qType = (searchParams.get("type") as InterviewType) || "technical";
      const qGap = searchParams.get("gap") || undefined;
      const qReportId = searchParams.get("reportId") ? parseInt(searchParams.get("reportId")!, 10) : undefined;

      async function initFromQuery() {
        setStartingSession(true);
        try {
          const newSession = await createPracticeSession({
            topic: qTopic!,
            interview_type: qType,
            weakness_context: qGap,
            source_report_id: qReportId,
            difficulty: "medium",
          });
          navigate(`/practice/${newSession.id}`, { replace: true });
        } catch (err) {
          setError(err instanceof Error ? err.message : "Could not initialize practice session.");
          setStartingSession(false);
        }
      }
      void initFromQuery();
      return;
    }

    if (sessionId) {
      void loadSession(sessionId);
    } else {
      void loadHub();
    }
  }, [sessionId, searchParams, loadSession, loadHub, navigate]);

  // Active question & attempt
  const currentQuestion: PracticeQuestion | undefined = session?.questions?.[activeQuestionIndex];
  const attempts: PracticeAttempt[] = currentQuestion?.attempts || [];
  const latestAttempt: PracticeAttempt | undefined = attempts[attempts.length - 1];

  // Determine current assistance level
  function getAssistanceLevel(): AssistanceLevel {
    if (!currentQuestion) return "independent";
    if (currentQuestion.reference_revealed) return "reference_assisted";
    if (currentQuestion.hints_revealed?.length > 0) return "hint_assisted";
    return "independent";
  }

  // Handle Hint Reveal
  async function handleRevealNextHint() {
    if (!currentQuestion || revealingHint) return;
    const currentHints = currentQuestion.hints_revealed || [];
    const nextLevel = currentHints.includes(1) ? 2 : 1;
    if (currentHints.includes(nextLevel)) return;

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
      alert(err instanceof Error ? err.message : "Failed to reveal hint.");
    } finally {
      setRevealingHint(false);
    }
  }

  // Handle Reference Reveal
  async function handleConfirmRevealRef() {
    if (!currentQuestion || revealingRef) return;
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
      alert(err instanceof Error ? err.message : "Failed to reveal reference answer.");
    } finally {
      setRevealingRef(false);
    }
  }

  // Handle Submit Answer
  async function handleSubmitAnswer() {
    if (!currentQuestion || !answerText.trim() || submitting) return;
    setSubmitting(true);
    try {
      const newAttempt = await submitPracticeAttempt(currentQuestion.id, {
        answer_text: answerText.trim(),
      });
      setSession((prev) => {
        if (!prev) return prev;
        const updatedQuestions = [...prev.questions];
        const q = { ...updatedQuestions[activeQuestionIndex] };
        q.attempts = [...(q.attempts || []), newAttempt];
        updatedQuestions[activeQuestionIndex] = q;
        return { ...prev, questions: updatedQuestions };
      });
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to evaluate answer.");
    } finally {
      setSubmitting(false);
    }
  }

  // Handle Generate Similar Question
  async function handleGenerateSimilar() {
    if (!session || generatingSimilar) return;
    setGeneratingSimilar(true);
    try {
      const newQ = await generateNextQuestion(session.id, {
        difficulty: (currentQuestion?.difficulty as PracticeDifficulty) || "medium",
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
      alert(err instanceof Error ? err.message : "Failed to generate similar question.");
    } finally {
      setGeneratingSimilar(false);
    }
  }

  // Start new session from Hub
  async function handleStartHubSession(topic: string, type: InterviewType, diff: PracticeDifficulty) {
    setStartingSession(true);
    try {
      const newSession = await createPracticeSession({
        topic,
        interview_type: type,
        difficulty: diff,
      });
      navigate(`/practice/${newSession.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create practice session.");
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
      alert(err instanceof Error ? err.message : "Failed to delete practice session.");
    } finally {
      setDeleting(false);
    }
  }

  // RENDER: Loading or Error
  if (loading || startingSession) {
    return (
      <div className="practice-page">
        <div className="pm-card" style={{ padding: "3rem", textAlign: "center" }}>
          <SparklesIcon size={24} style={{ color: "#3b82f6", marginBottom: "1rem" }} />
          <h2>Preparing Your Practice Session...</h2>
          <p style={{ color: "#94a3b8" }}>
            Grounding concepts, progressive hints, and reference answers with AI.
          </p>
        </div>
      </div>
    );
  }

  if (error && !session) {
    return (
      <div className="practice-page">
        <div className="pm-card" style={{ padding: "2.5rem", textAlign: "center" }}>
          <h2 style={{ color: "#ef4444" }}>Could Not Load Practice</h2>
          <p style={{ color: "#94a3b8", marginBottom: "1.5rem" }}>{error}</p>
          <Link to="/practice" className="btn btn-secondary">
            Return to Practice Hub
          </Link>
        </div>
      </div>
    );
  }

  // =========================================================================
  // VIEW A: PRACTICE HUB (when no sessionId)
  // =========================================================================
  if (!sessionId) {
    return (
      <div className="practice-page">
        <header className="practice-header">
          <div>
            <span className="pm-eyebrow">GUIDED LEARNING</span>
            <h1 className="pm-page-title">Personalized Practice Hub</h1>
            <p className="pm-page-subtitle">
              Master interview answers in your own words through progressive hints, reference answers, and structured AI coaching.
            </p>
          </div>
        </header>

        {/* Continue Improving from Recent Reports */}
        {recommendations.length > 0 && (
          <section className="pm-card" style={{ padding: "1.75rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "1.25rem" }}>
              <LightbulbIcon size={20} style={{ color: "#eab308" }} />
              <h2 style={{ fontSize: "1.15rem", margin: 0 }}>Continue Improving — Recommended for You</h2>
            </div>
            <div className="practice-hub-grid">
              {recommendations.map((rec, idx) => (
                <article key={idx} className="practice-rec-card">
                  <div>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.5rem" }}>
                      <span className="badge badge-neutral" style={{ textTransform: "capitalize" }}>
                        {rec.interview_type}
                      </span>
                      <span className={`badge ${rec.priority === "high" ? "badge-danger" : "badge-warning"}`}>
                        {rec.priority} priority
                      </span>
                    </div>
                    <strong style={{ fontSize: "1.05rem", color: "#f1f5f9", display: "block", marginBottom: "0.35rem" }}>
                      {rec.topic}
                    </strong>
                    <p style={{ fontSize: "0.85rem", color: "#94a3b8", margin: 0 }}>
                      {rec.observed_gap}
                    </p>
                  </div>
                  <button
                    className="btn btn-primary"
                    style={{ marginTop: "1rem" }}
                    onClick={() => handleStartHubSession(rec.topic, rec.interview_type, "medium")}
                  >
                    <span>Practice This Topic</span>
                    <ArrowRightIcon size={14} />
                  </button>
                </article>
              ))}
            </div>
          </section>
        )}

        {/* Start Independent Practice */}
        <section className="pm-card" style={{ padding: "1.75rem" }}>
          <h2 style={{ fontSize: "1.15rem", marginBottom: "1rem" }}>Start Targeted Practice</h2>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "1rem", marginBottom: "1.5rem" }}>
            <div>
              <label style={{ display: "block", fontSize: "0.825rem", color: "#94a3b8", marginBottom: "0.4rem" }}>
                Topic / Concept
              </label>
              <input
                type="text"
                className="input-field"
                value={hubTopic}
                onChange={(e) => setHubTopic(e.target.value)}
                placeholder="e.g. SQL Joins, Overfitting, Conflict Resolution"
              />
            </div>
            <div>
              <label style={{ display: "block", fontSize: "0.825rem", color: "#94a3b8", marginBottom: "0.4rem" }}>
                Interview Type
              </label>
              <select
                className="input-field"
                value={hubType}
                onChange={(e) => setHubType(e.target.value as InterviewType)}
              >
                <option value="technical">Technical Interview</option>
                <option value="hr">HR / Behavioral</option>
              </select>
            </div>
            <div>
              <label style={{ display: "block", fontSize: "0.825rem", color: "#94a3b8", marginBottom: "0.4rem" }}>
                Difficulty
              </label>
              <select
                className="input-field"
                value={hubDifficulty}
                onChange={(e) => setHubDifficulty(e.target.value as PracticeDifficulty)}
              >
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
            </div>
          </div>
          <button
            className="btn btn-primary"
            onClick={() => handleStartHubSession(hubTopic, hubType, hubDifficulty)}
            disabled={!hubTopic.trim()}
          >
            <BookOpenIcon size={16} />
            <span>Launch Practice Studio</span>
          </button>
        </section>

        {/* Previous Practice Sessions */}
        {summaries.length > 0 && (
          <section className="pm-card" style={{ padding: "1.75rem" }}>
            <h2 style={{ fontSize: "1.15rem", marginBottom: "1rem" }}>Your Practice Sessions</h2>
            <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
              {summaries.map((s) => (
                <div
                  key={s.id}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "1rem 1.25rem",
                    background: "#0d1017",
                    border: "1px solid #1f242e",
                    borderRadius: "8px",
                    flexWrap: "wrap",
                    gap: "1rem",
                  }}
                >
                  <div>
                    <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.25rem" }}>
                      <strong>{s.topic}</strong>
                      <span className="badge badge-neutral" style={{ textTransform: "capitalize" }}>
                        {s.interview_type}
                      </span>
                    </div>
                    <p style={{ fontSize: "0.825rem", color: "#64748b", margin: 0 }}>
                      {s.question_count} {s.question_count === 1 ? "question" : "questions"} ·{" "}
                      {s.attempt_count} {s.attempt_count === 1 ? "attempt" : "attempts"} · Created{" "}
                      {formatDateTime(s.created_at)}
                    </p>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                    <Link to={`/practice/${s.id}`} className="btn btn-secondary">
                      <span>Resume</span>
                      <ArrowRightIcon size={14} />
                    </Link>
                    <button
                      className="btn btn-danger-outline"
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
    <div className="practice-page">
      {/* Studio Header */}
      <header className="practice-header">
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "0.25rem" }}>
            <Link to="/practice" style={{ fontSize: "0.825rem", color: "#94a3b8", textDecoration: "none" }}>
              ← Practice Hub
            </Link>
            {session?.source_report_id && (
              <Link
                to={`/reports/${session.source_report_id}`}
                style={{ fontSize: "0.825rem", color: "#3b82f6", textDecoration: "none" }}
              >
                · Return to Report
              </Link>
            )}
          </div>
          <h1 className="pm-page-title" style={{ fontSize: "1.75rem" }}>{session?.topic}</h1>
          <div className="practice-badge-group">
            <span className="badge badge-neutral">
              {session?.interview_type === "hr" ? <UsersIcon size={13} /> : <CodeIcon size={13} />}
              <span style={{ textTransform: "capitalize", marginLeft: "4px" }}>
                {session?.interview_type} Practice
              </span>
            </span>
            <span className="badge badge-neutral">Difficulty: {currentQuestion?.difficulty || "medium"}</span>
            <span
              className={`badge ${
                assistanceLevel === "independent"
                  ? "badge-independent"
                  : assistanceLevel === "hint_assisted"
                    ? "badge-hint-assisted"
                    : "badge-reference-assisted"
              }`}
            >
              {assistanceLevel === "independent"
                ? "Independent Practice"
                : assistanceLevel === "hint_assisted"
                  ? "Hint-Assisted"
                  : "Reference-Assisted"}
            </span>
          </div>
        </div>

        {/* Question Selector if multiple */}
        {session && session.questions.length > 1 && (
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <span style={{ fontSize: "0.825rem", color: "#94a3b8" }}>Questions:</span>
            {session.questions.map((q, idx) => (
              <button
                key={q.id}
                className={`btn ${idx === activeQuestionIndex ? "btn-primary" : "btn-secondary"}`}
                style={{ minWidth: "36px", padding: "0.35rem 0.65rem", fontSize: "0.85rem" }}
                onClick={() => {
                  setActiveQuestionIndex(idx);
                  setAnswerText("");
                }}
              >
                {idx + 1}
              </button>
            ))}
          </div>
        )}
      </header>

      {/* Main Studio Grid */}
      <div className="practice-grid">
        {/* Question & Clues Panel */}
        <section className="practice-question-card">
          <div className="practice-question-head">
            <span className="badge badge-neutral">
              Question {activeQuestionIndex + 1} of {session?.questions.length || 1}
            </span>
            <span style={{ fontSize: "0.825rem", color: "#64748b" }}>
              {attempts.length} {attempts.length === 1 ? "attempt submitted" : "attempts submitted"}
            </span>
          </div>

          <h2 className="practice-question-text">{currentQuestion?.question_text}</h2>

          {session?.weakness_context && (
            <div className="practice-weakness-note">
              <strong>Targeting Growth Area:</strong> {session.weakness_context}
            </div>
          )}

          {/* Help & Clues Toolbar */}
          <div className="practice-help-toolbar">
            <button
              className="btn btn-secondary"
              onClick={handleRevealNextHint}
              disabled={revealingHint || (currentQuestion?.hints_revealed?.length ?? 0) >= 2}
            >
              <LightbulbIcon size={15} style={{ color: "#eab308" }} />
              <span>
                {(currentQuestion?.hints_revealed?.length ?? 0) === 0
                  ? "Get Hint 1 (Direction)"
                  : (currentQuestion?.hints_revealed?.length ?? 0) === 1
                    ? "Get Hint 2 (Structure)"
                    : "All Hints Revealed"}
              </span>
            </button>

            {!currentQuestion?.reference_revealed && (
              <button
                className="btn btn-secondary"
                onClick={() => setShowRefConfirm(true)}
                disabled={revealingRef}
              >
                <BookOpenIcon size={15} style={{ color: "#3b82f6" }} />
                <span>Show Reference Answer</span>
              </button>
            )}
          </div>

          {/* Revealed Hints */}
          {currentQuestion && currentQuestion.hints_revealed?.length > 0 && (
            <div className="practice-hints-container">
              {currentQuestion.hints_revealed.map((lvl) => (
                <div key={lvl} className="hint-card">
                  <div className="hint-card-title">
                    <LightbulbIcon size={13} />
                    <span>Hint {lvl} {lvl === 1 ? "· Directional Clue" : "· Answer Framework"}</span>
                  </div>
                  <p className="hint-card-text">{currentQuestion.revealed_hints[String(lvl)]}</p>
                </div>
              ))}
            </div>
          )}

          {/* Revealed Reference Answer */}
          {currentQuestion?.reference_revealed && (
            <div className="reference-card">
              <div className="reference-card-title">
                <BookOpenIcon size={14} />
                <span>
                  {session?.interview_type === "hr"
                    ? "Example of a Strong Response (Assisted)"
                    : "Complete Reference Answer (Assisted)"}
                </span>
              </div>
              <p className="reference-card-body">{currentQuestion.reference_answer}</p>
              {currentQuestion.reference_explanation && (
                <p className="reference-card-explanation">{currentQuestion.reference_explanation}</p>
              )}
              <div className="reference-warning-alert">
                Learning Note: You viewed the reference answer. Submissions for this question are recorded as assisted practice to help you learn formulation in your own words.
              </div>
            </div>
          )}
        </section>

        {/* Answer Submission Workspace */}
        <section className="practice-answer-section">
          <div className="practice-textarea-wrap">
            <textarea
              className="practice-textarea"
              placeholder="Formulate your interview answer here in your own words. Take your time to structure your explanation clearly..."
              value={answerText}
              onChange={(e) => setAnswerText(e.target.value)}
              disabled={submitting}
              rows={8}
            />
            <div className="practice-editor-meta">
              <span>{answerText.length} characters</span>
              <span>{answerText.trim().split(/\s+/).filter(Boolean).length} words</span>
            </div>
          </div>

          <div className="practice-action-row">
            {latestAttempt && !answerText && (
              <button
                className="btn btn-secondary"
                onClick={() => setAnswerText(latestAttempt.answer_text)}
              >
                <RotateCcwIcon size={14} />
                <span>Reload Last Attempt</span>
              </button>
            )}

            <button
              className="btn btn-primary"
              onClick={handleSubmitAnswer}
              disabled={!answerText.trim() || submitting}
            >
              <SparklesIcon size={15} />
              <span>{submitting ? "Analyzing with AI Coach..." : "Submit for AI Coaching"}</span>
            </button>
          </div>
        </section>

        {/* AI Answer Coach Feedback Panel (when attempt submitted) */}
        {latestAttempt && (
          <section className="coach-panel">
            <div className="coach-header">
              <div className="coach-title">
                <SparklesIcon size={18} style={{ color: "#3b82f6" }} />
                <span>AI Answer Coach Feedback · Attempt #{latestAttempt.attempt_number}</span>
              </div>
              <span className={`badge ${
                latestAttempt.assistance_level === "independent"
                  ? "badge-independent"
                  : latestAttempt.assistance_level === "hint_assisted"
                    ? "badge-hint-assisted"
                    : "badge-reference-assisted"
              }`}>
                {latestAttempt.assistance_level === "independent"
                  ? "Independent Attempt"
                  : latestAttempt.assistance_level === "hint_assisted"
                    ? "Hint-Assisted"
                    : "Reference-Assisted"}
              </span>
            </div>

            {/* Comparison with previous attempt if retry */}
            {latestAttempt.feedback.improvements_from_previous &&
              latestAttempt.feedback.improvements_from_previous.length > 0 && (
                <div className="coach-comparison-banner">
                  <span className="coach-comparison-title">What Improved Since Your Last Attempt:</span>
                  <ul className="coach-list">
                    {latestAttempt.feedback.improvements_from_previous.map((imp, idx) => (
                      <li key={idx} style={{ color: "#22c55e" }}>{imp}</li>
                    ))}
                  </ul>
                </div>
              )}

            {/* What you got right & what was missing */}
            <div className="coach-two-col">
              <div className="coach-card coach-card-good">
                <h3 className="coach-card-title">What You Got Right</h3>
                {latestAttempt.feedback.correct_points.length > 0 ? (
                  <ul className="coach-list">
                    {latestAttempt.feedback.correct_points.map((pt, idx) => (
                      <li key={idx}>{pt}</li>
                    ))}
                  </ul>
                ) : (
                  <p style={{ fontSize: "0.85rem", color: "#94a3b8", margin: 0 }}>
                    Keep developing your response to articulate core fundamentals.
                  </p>
                )}
              </div>

              <div className="coach-card coach-card-missing">
                <h3 className="coach-card-title">What Was Missing</h3>
                {latestAttempt.feedback.missing_points.length > 0 ? (
                  <ul className="coach-list">
                    {latestAttempt.feedback.missing_points.map((pt, idx) => (
                      <li key={idx}>{pt}</li>
                    ))}
                  </ul>
                ) : (
                  <p style={{ fontSize: "0.85rem", color: "#94a3b8", margin: 0 }}>
                    Strong coverage of key concepts without major omissions.
                  </p>
                )}
              </div>
            </div>

            {/* Suggested Structure */}
            {latestAttempt.feedback.suggested_structure.length > 0 && (
              <div className="coach-card coach-card-structure">
                <h3 className="coach-card-title">Recommended Answer Structure</h3>
                <ul className="coach-list">
                  {latestAttempt.feedback.suggested_structure.map((step, idx) => (
                    <li key={idx}>{step}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Improved Example Answer */}
            {latestAttempt.feedback.improved_example_answer && (
              <div className="coach-example-card">
                <span style={{ fontSize: "0.8rem", fontWeight: 700, color: "#818cf8", textTransform: "uppercase" }}>
                  Polished Example Answer (AI-Generated Blueprint)
                </span>
                <p style={{ fontSize: "0.925rem", color: "#f1f5f9", lineHeight: 1.6, margin: 0 }}>
                  {latestAttempt.feedback.improved_example_answer}
                </p>
              </div>
            )}

            {/* Next Action & Refinement CTA */}
            {latestAttempt.feedback.next_action && (
              <div className="coach-next-action-card">
                <div>
                  <span style={{ fontSize: "0.8rem", fontWeight: 700, color: "#60a5fa", textTransform: "uppercase" }}>
                    Recommended Next Step
                  </span>
                  <p style={{ fontSize: "0.925rem", color: "#f1f5f9", margin: "0.25rem 0 0" }}>
                    {latestAttempt.feedback.next_action}
                  </p>
                </div>
                <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
                  <button
                    className="btn btn-secondary"
                    onClick={() => {
                      setAnswerText("");
                      window.scrollTo({ top: 300, behavior: "smooth" });
                    }}
                  >
                    <RotateCcwIcon size={14} />
                    <span>Improve My Answer</span>
                  </button>

                  <button
                    className="btn btn-primary"
                    onClick={handleGenerateSimilar}
                    disabled={generatingSimilar}
                  >
                    <span>{generatingSimilar ? "Generating..." : "Try a Similar Question"}</span>
                    <ArrowRightIcon size={14} />
                  </button>
                </div>
              </div>
            )}
          </section>
        )}
      </div>

      {/* Confirmation Dialog before revealing reference answer */}
      <ConfirmDialog
        open={showRefConfirm}
        title="Reveal Reference Answer?"
        description="Viewing the reference answer is great for assisted learning, but it marks your practice session as 'Reference-Assisted'. You can still submit and refine your answer to test your formulation."
        confirmLabel="Reveal Answer"
        busy={revealingRef}
        onConfirm={handleConfirmRevealRef}
        onCancel={() => setShowRefConfirm(false)}
      />
    </div>
  );
}
