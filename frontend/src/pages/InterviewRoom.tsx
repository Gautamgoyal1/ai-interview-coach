import { useCallback, useEffect, useRef, useState } from "react";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";
import {
  ArrowRightIcon,
  CheckCircleIcon,
  GraduationCapIcon,
  XIcon,
} from "../components/Icons";
import AnswerBox from "../features/interview/AnswerBox";
import InterviewSetup from "../features/interview/InterviewSetup";
import ProgressBar from "../features/interview/ProgressBar";
import QuestionCard from "../features/interview/QuestionCard";
import {
  type StartInterviewOptions,
  useInterview,
} from "../features/interview/useInterview";
import { useAuth } from "../hooks/useAuth";
import type { ExperienceLevel } from "../types/interview";
import "./InterviewRoom.css";

const EXPERIENCE_LABELS: Record<ExperienceLevel, string> = {
  internship: "Internship",
  fresher: "Fresher",
  intermediate: "Intermediate",
  experienced: "Experienced",
};

export default function InterviewRoom() {
  const { sessionId } = useParams<{ sessionId?: string }>();
  const [searchParams] = useSearchParams();
  const analysisIdParam = searchParams.get("analysisId");

  const navigate = useNavigate();
  const { logout } = useAuth();
  const {
    session,
    loading,
    submitting,
    error,
    unauthorized,
    setError,
    beginSession,
    loadSession,
    submitAnswer,
    finishSession,
  } = useInterview();

  const [answerText, setAnswerText] = useState("");
  const startedAnalysisRef = useRef<string | null>(null);

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
      void loadSession(sessionId);
      return;
    }

    if (analysisIdParam) {
      const numericId = Number(analysisIdParam);
      if (
        Number.isInteger(numericId) &&
        numericId > 0 &&
        startedAnalysisRef.current !== analysisIdParam
      ) {
        startedAnalysisRef.current = analysisIdParam;
        void beginSession(numericId).then((created) => {
          if (created) {
            navigate(`/interview/${created.session_id}`, { replace: true });
          }
        });
      }
    }
  }, [sessionId, analysisIdParam, loadSession, beginSession, navigate]);

  async function handleStartFromSetup(
    analysisId: number,
    options: StartInterviewOptions,
  ) {
    const created = await beginSession(analysisId, options);
    if (created) {
      navigate(`/interview/${created.session_id}`, { replace: true });
    }
  }

  async function handleSubmitAnswer() {
    if (!session || !session.current_question) return;
    const updated = await submitAnswer(
      session.session_id,
      session.current_question.question_id,
      answerText,
    );
    if (updated) {
      setAnswerText("");
    }
  }

  async function handleEndInterview() {
    if (!session || submitting) return;
    await finishSession(session.session_id);
  }

  if (!sessionId && !analysisIdParam && !session) {
    return (
      <div className="interview-setup-page">
        {error && (
          <div className="pm-alert-error" role="alert">
            <span>{error}</span>
          </div>
        )}
        <InterviewSetup
          onStart={handleStartFromSetup}
          onUnauthorized={handleUnauthorized}
          starting={loading}
        />
      </div>
    );
  }

  if (loading && !session) {
    return (
      <div className="iv-shell">
        <div className="iv-container iv-loading-wrap">
          <div className="pm-status-banner" role="status">
            <span className="pm-spinner" aria-hidden="true" />
            <div>
              <strong>Preparing your interview workspace</strong>
              <p>
                Loading your profile and calibrating your questions...
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!session && error) {
    return (
      <div className="iv-shell">
        <div className="iv-container iv-loading-wrap">
          <section className="pm-card interview-error-card" role="alert">
            <h2>Unable to open interview</h2>
            <p>{error}</p>
            <div className="interview-error-actions">
              <Link to="/interview" className="btn btn-primary">
                Start New Interview
              </Link>
              <Link to="/history" className="btn btn-secondary">
                Back to History
              </Link>
            </div>
          </section>
        </div>
      </div>
    );
  }

  if (!session) {
    return null;
  }

  const answeredTurns = session.conversation_history.filter(
    (turn) => turn.answer_text !== null,
  );
  const experienceLabel =
    EXPERIENCE_LABELS[session.experience_level ?? "fresher"];
  const isInProgress =
    session.status === "in_progress" && session.current_question !== null;
  const roundTypeLabel =
    session.interview_type === "hr" ? "Behavioral round" : "Technical round";

  return (
    <div className="iv-shell">
      {/* Top Header Bar matching conceptual preview */}
      <header className="iv-header">
        <div className="iv-header-inner">
          <div className="iv-header-left">
            <Link to="/" className="iv-brand" aria-label="PrepMate Dashboard">
              <span className="iv-brand-mark">
                <GraduationCapIcon size={18} />
              </span>
              <span className="iv-brand-copy">
                <strong>PrepMate</strong>
                <span>Interview workspace</span>
              </span>
            </Link>
          </div>

          <div className="iv-header-right">
            {isInProgress && (
              <span className="iv-header-count tabular-nums">
                Question {Math.min(session.question_index, session.max_questions)} of{" "}
                {session.max_questions}
              </span>
            )}
            <Link to="/" className="btn btn-ghost iv-header-btn">
              Dashboard
            </Link>
            {isInProgress ? (
              <button
                type="button"
                className="btn btn-danger-outline iv-header-btn"
                onClick={() => void handleEndInterview()}
                disabled={submitting}
              >
                End interview
              </button>
            ) : (
              <Link to="/interview" className="btn btn-primary iv-header-btn">
                <span>New Interview</span>
                <ArrowRightIcon size={14} />
              </Link>
            )}
          </div>
        </div>
      </header>

      {/* Main Workspace */}
      <div className="iv-container">
        {error && (
          <div className="pm-alert-error iv-alert" role="alert">
            <span>{error}</span>
            <button
              type="button"
              className="banner-dismiss"
              onClick={() => setError(null)}
              aria-label="Dismiss error"
            >
              <XIcon size={16} />
            </button>
          </div>
        )}

        {isInProgress && session.current_question ? (
          <div className="iv-workspace">
            {/* Subheader bar */}
            <div className="iv-subheader">
              <div className="iv-subheader-info">
                <h1 className="iv-role-title">
                  {session.target_role} Interview
                </h1>
                <p className="iv-role-meta">
                  {experienceLabel} level · {roundTypeLabel}
                </p>
              </div>

              <div className="iv-status-pill">
                In progress
              </div>
            </div>

            {/* Full-width slim progress bar */}
            <ProgressBar
              questionIndex={session.question_index}
              maxQuestions={session.max_questions}
              isFollowUp={session.current_question.is_follow_up}
              answeredCount={answeredTurns.length}
            />

            {/* Split Grid: Left Question, Right Answer */}
            <div className="iv-split-grid">
              <QuestionCard
                question={session.current_question}
                questionIndex={session.question_index}
                maxQuestions={session.max_questions}
              />

              <AnswerBox
                questionId={session.current_question.question_id}
                answer={answerText}
                onChange={setAnswerText}
                onSubmit={() => void handleSubmitAnswer()}
                submitting={submitting}
                disabled={loading}
              />
            </div>
          </div>
        ) : (
          <section className="iv-complete-card">
            <span className="badge badge-success">
              <CheckCircleIcon size={13} />
              <span>Interview Complete</span>
            </span>
            <h2>{session.target_role} Interview Complete</h2>
            <p className="iv-complete-summary">
              You completed{" "}
              <strong className="tabular-nums">{answeredTurns.length}</strong>{" "}
              {answeredTurns.length === 1 ? "question" : "questions"} at the{" "}
              <strong>{experienceLabel}</strong> level. Your session has been
              saved and is ready for rubric evaluation.
            </p>
            <div className="iv-complete-actions">
              <Link
                to={`/reports/${session.session_id}`}
                className="btn btn-primary"
              >
                <span>View Interview Report</span>
                <ArrowRightIcon size={15} />
              </Link>
              <Link to="/" className="btn btn-secondary">
                Return to Dashboard
              </Link>
              <Link to="/interview" className="btn btn-secondary">
                Start Another Interview
              </Link>
            </div>
          </section>
        )}

        {answeredTurns.length > 0 && (
          <section className="iv-transcript-section">
            <div className="iv-transcript-header">
              <h3>Session Transcript</h3>
              <span className="badge badge-neutral tabular-nums">
                {answeredTurns.length}{" "}
                {answeredTurns.length === 1 ? "response" : "responses"}
              </span>
            </div>
            <div className="iv-transcript-list">
              {answeredTurns.map((turn) => (
                <article key={turn.question_id} className="iv-transcript-item">
                  <div className="iv-transcript-meta">
                    <span className="tabular-nums">
                      Q{turn.question_index}
                      {turn.is_follow_up ? " · Follow-up" : ""} · {turn.topic}
                    </span>
                    <span className="badge badge-neutral">{turn.difficulty}</span>
                  </div>
                  <p className="iv-transcript-question">{turn.question_text}</p>
                  <p className="iv-transcript-answer">
                    <strong>Your answer:</strong> {turn.answer_text}
                  </p>
                </article>
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  );
}
