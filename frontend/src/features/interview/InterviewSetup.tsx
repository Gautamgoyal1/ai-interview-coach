import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  ArrowRightIcon,
  CheckCircleIcon,
  CodeIcon,
  FileTextIcon,
  UsersIcon,
} from "../../components/Icons";
import { getResumeAnalyses } from "../../services/resume.service";
import type {
  ExperienceLevel,
  InterviewType,
  ProgressionMode,
  StartingDifficulty,
} from "../../types/interview";
import type { ResumeAnalysisHistoryItem } from "../../types/resume";
import { formatDateTime } from "../../utils/formatters";
import type { StartInterviewOptions } from "./useInterview";

interface InterviewSetupProps {
  onStart: (analysisId: number, options: StartInterviewOptions) => void;
  onUnauthorized: () => void;
  starting: boolean;
}

const EXPERIENCE_LEVEL_OPTIONS: {
  value: ExperienceLevel;
  label: string;
  hint: string;
}[] = [
  {
    value: "internship",
    label: "Student / Internship",
    hint: "Foundational concepts, coursework & campus projects",
  },
  {
    value: "fresher",
    label: "Fresher / Entry Level",
    hint: "Core role fundamentals, projects & practical application",
  },
  {
    value: "intermediate",
    label: "Experienced: 1–3 years",
    hint: "Applied trade-offs, real-world debugging & collaboration",
  },
  {
    value: "experienced",
    label: "Experienced: 3+ years",
    hint: "Deep architectural trade-offs, leadership & production dilemmas",
  },
];

const DIFFICULTY_OPTIONS: {
  value: StartingDifficulty;
  label: string;
  hint: string;
}[] = [
  {
    value: "easy",
    label: "Easy",
    hint: "Approachable fundamentals & straightforward scenarios",
  },
  {
    value: "medium",
    label: "Medium",
    hint: "Realistic trade-offs, standard depth & balanced challenge",
  },
  {
    value: "hard",
    label: "Hard",
    hint: "Complex constraints, conflicting requirements & high-stakes dilemmas",
  },
];

const PROGRESSION_OPTIONS: {
  value: ProgressionMode;
  label: string;
  hint: string;
}[] = [
  {
    value: "adaptive",
    label: "Adaptive Practice",
    hint: "Difficulty changes dynamically based on your performance",
  },
  {
    value: "mock",
    label: "Mock Assessment",
    hint: "Follows a consistent, planned difficulty structure for benchmarking",
  },
];

const QUESTION_COUNT_OPTIONS = [5, 8, 10];

export default function InterviewSetup({
  onStart,
  onUnauthorized,
  starting,
}: InterviewSetupProps) {
  const [analyses, setAnalyses] = useState<ResumeAnalysisHistoryItem[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);

  // New configuration options
  const [interviewType, setInterviewType] = useState<InterviewType>("technical");
  const [experienceLevel, setExperienceLevel] =
    useState<ExperienceLevel>("fresher");
  const [startingDifficulty, setStartingDifficulty] =
    useState<StartingDifficulty>("medium");
  const [progressionMode, setProgressionMode] =
    useState<ProgressionMode>("adaptive");
  const [maxQuestions, setMaxQuestions] = useState<number>(8);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const list = await getResumeAnalyses(20);
        if (!cancelled) {
          setAnalyses(list);
          if (list.length > 0) {
            setSelectedId(list[0].id);
          }
        }
      } catch (err) {
        if (
          err &&
          typeof err === "object" &&
          "status" in err &&
          (err as { status: number }).status === 401
        ) {
          onUnauthorized();
          return;
        }
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : "Could not load your saved resume analyses.",
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    void load();
    return () => {
      cancelled = true;
    };
  }, [onUnauthorized]);

  const selectedResume = analyses.find((a) => a.id === selectedId);

  return (
    <section className="interview-setup-wrap">
      <header className="pm-page-header">
        <div>
          <p className="pm-eyebrow">Personalized AI Interview Configuration</p>
          <h1 className="pm-page-title">Configure Your Interview Session</h1>
          <p className="pm-page-subtitle">
            Customize interview type, candidate background, starting challenge,
            and progression pacing for a realistic practice experience.
          </p>
        </div>
      </header>

      <div className="pm-card interview-setup-card">
        {loading && (
          <div className="pm-status-banner" role="status">
            <span className="pm-spinner" aria-hidden="true" />
            <div>
              <strong>Loading your saved analyses</strong>
              <p>Fetching resume profiles...</p>
            </div>
          </div>
        )}

        {!loading && error && (
          <div className="pm-alert-error" role="alert">
            <span>{error}</span>
          </div>
        )}

        {!loading && !error && analyses.length === 0 && (
          <div className="pm-empty-state">
            <div className="pm-empty-icon">
              <FileTextIcon size={22} />
            </div>
            <h2>Analyze a resume first</h2>
            <p>
              You need at least one saved resume analysis to calibrate your
              interview questions.
            </p>
            <div className="pm-empty-actions">
              <Link to="/analyze" className="btn btn-primary">
                <span>Go to Resume Analyzer</span>
                <ArrowRightIcon size={15} />
              </Link>
            </div>
          </div>
        )}

        {!loading && !error && analyses.length > 0 && (
          <div className="setup-list">
            {/* Step 1: Interview Type Selection */}
            <div className="setup-section">
              <span className="setup-label">1. Choose Interview Type</span>
              <div className="setup-type-grid">
                <button
                  type="button"
                  className={`setup-type-card ${
                    interviewType === "technical" ? "selected" : ""
                  }`}
                  onClick={() => setInterviewType("technical")}
                >
                  <div className="setup-type-header">
                    <span className="setup-type-icon">
                      <CodeIcon size={20} />
                    </span>
                    <div className="setup-type-title-wrap">
                      <strong>Technical Interview</strong>
                      <span className="badge badge-accent">Role Fundamentals</span>
                    </div>
                  </div>
                  <p className="setup-type-desc">
                    Evaluates core data structures, system architecture, role
                    technologies, and practical debugging grounded in your resume
                    and job description.
                  </p>
                  <ul className="setup-type-tags">
                    <li>Technical Correctness</li>
                    <li>Technical Depth</li>
                    <li>Implementation Trade-offs</li>
                  </ul>
                </button>

                <button
                  type="button"
                  className={`setup-type-card ${
                    interviewType === "hr" ? "selected" : ""
                  }`}
                  onClick={() => setInterviewType("hr")}
                >
                  <div className="setup-type-header">
                    <span className="setup-type-icon">
                      <UsersIcon size={20} />
                    </span>
                    <div className="setup-type-title-wrap">
                      <strong>HR / Behavioral Interview</strong>
                      <span className="badge badge-success">Competency & Judgment</span>
                    </div>
                  </div>
                  <p className="setup-type-desc">
                    Evaluates situational judgment, critical reasoning, teamwork,
                    prioritization, and communication under realistic workplace
                    dilemmas.
                  </p>
                  <ul className="setup-type-tags">
                    <li>Critical Thinking (30%)</li>
                    <li>Decision Trade-offs (25%)</li>
                    <li>Communication & Clarity (20%)</li>
                  </ul>
                </button>
              </div>
            </div>

            {/* Step 2: Experience Level & Starting Difficulty */}
            <div className="setup-section">
              <span className="setup-label">2. Candidate Background & Challenge</span>
              <div className="setup-config-grid">
                <div className="setup-field">
                  <label
                    htmlFor="experience-level-select"
                    className="setup-sublabel"
                  >
                    Experience Level
                  </label>
                  <select
                    id="experience-level-select"
                    className="setup-select"
                    value={experienceLevel}
                    onChange={(e) =>
                      setExperienceLevel(e.target.value as ExperienceLevel)
                    }
                  >
                    {EXPERIENCE_LEVEL_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label} — {opt.hint}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="setup-field">
                  <label
                    htmlFor="starting-difficulty-select"
                    className="setup-sublabel"
                  >
                    Preferred Starting Difficulty
                  </label>
                  <select
                    id="starting-difficulty-select"
                    className="setup-select"
                    value={startingDifficulty}
                    onChange={(e) =>
                      setStartingDifficulty(
                        e.target.value as StartingDifficulty,
                      )
                    }
                  >
                    {DIFFICULTY_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label} — {opt.hint}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {/* Step 3: Progression Mode & Question Length */}
            <div className="setup-section">
              <span className="setup-label">3. Progression Mode & Length</span>
              <div className="setup-config-grid">
                <div className="setup-field">
                  <label
                    htmlFor="progression-mode-select"
                    className="setup-sublabel"
                  >
                    Interview Progression
                  </label>
                  <select
                    id="progression-mode-select"
                    className="setup-select"
                    value={progressionMode}
                    onChange={(e) =>
                      setProgressionMode(e.target.value as ProgressionMode)
                    }
                  >
                    {PROGRESSION_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label} — {opt.hint}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="setup-field">
                  <label
                    htmlFor="interview-length-select"
                    className="setup-sublabel"
                  >
                    Interview Length
                  </label>
                  <select
                    id="interview-length-select"
                    className="setup-select"
                    value={maxQuestions}
                    onChange={(e) => setMaxQuestions(Number(e.target.value))}
                  >
                    {QUESTION_COUNT_OPTIONS.map((count) => (
                      <option key={count} value={count}>
                        {count} Primary Questions{" "}
                        {count === 8 ? "(Recommended)" : ""}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {/* Step 4: Resume Profile Selection */}
            <div className="setup-section">
              <span className="setup-label">4. Select Resume Profile</span>
              <div className="setup-profiles-list">
                {analyses.map((item) => {
                  const active = selectedId === item.id;
                  return (
                    <label
                      key={item.id}
                      className={`setup-option ${active ? "selected" : ""}`}
                    >
                      <input
                        type="radio"
                        name="analysisId"
                        value={item.id}
                        checked={active}
                        onChange={() => setSelectedId(item.id)}
                      />
                      <div className="setup-option-body">
                        <strong>{item.job_role}</strong>
                        <span>
                          {item.filename} · {formatDateTime(item.created_at)}
                        </span>
                      </div>
                      <span className="badge badge-accent tabular-nums">
                        {Math.round(item.match_score)}% match
                      </span>
                    </label>
                  );
                })}
              </div>
            </div>

            {/* Step 5: Pre-Flight Configuration Summary */}
            <div className="setup-summary-card">
              <div className="summary-row">
                <div className="summary-item">
                  <span className="summary-label">Interview Type</span>
                  <strong className="summary-val">
                    {interviewType === "hr"
                      ? "HR / Behavioral"
                      : "Technical Interview"}
                  </strong>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Experience Stage</span>
                  <strong className="summary-val">
                    {EXPERIENCE_LEVEL_OPTIONS.find(
                      (o) => o.value === experienceLevel,
                    )?.label ?? experienceLevel}
                  </strong>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Starting Difficulty</span>
                  <strong className="summary-val capitalize">
                    {startingDifficulty}
                  </strong>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Progression</span>
                  <strong className="summary-val">
                    {progressionMode === "adaptive"
                      ? "Adaptive Practice"
                      : "Mock Assessment"}
                  </strong>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Questions</span>
                  <strong className="summary-val">
                    {maxQuestions} Primary Questions
                  </strong>
                </div>
              </div>
              {selectedResume && (
                <div className="summary-target">
                  Grounded in: <strong>{selectedResume.job_role}</strong> (
                  {selectedResume.filename})
                </div>
              )}
            </div>

            <div className="setup-actions">
              <button
                type="button"
                className="btn btn-primary"
                disabled={!selectedId || starting}
                onClick={() =>
                  selectedId &&
                  onStart(selectedId, {
                    interviewType,
                    experienceLevel,
                    startingDifficulty,
                    progressionMode,
                    maxQuestions,
                  })
                }
              >
                <span>
                  {starting
                    ? "Starting Interview..."
                    : `Start ${
                        interviewType === "hr" ? "HR" : "Technical"
                      } Interview`}
                </span>
                {!starting && <ArrowRightIcon size={15} />}
              </button>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
