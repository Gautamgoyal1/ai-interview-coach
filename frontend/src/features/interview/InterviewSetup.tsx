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
import { useAuth } from "../../hooks/useAuth";

interface InterviewSetupProps {
  onStart: (analysisId: number, options: StartInterviewOptions) => void;
  onUnauthorized: () => void;
  starting: boolean;
}

interface ExperienceOption {
  value: ExperienceLevel;
  label: string;
  badge: string;
  hint: string;
}

const EXPERIENCE_LEVEL_OPTIONS: ExperienceOption[] = [
  {
    value: "internship",
    label: "Student / Internship",
    badge: "Foundation",
    hint: "Foundational concepts, coursework & campus projects",
  },
  {
    value: "fresher",
    label: "Fresher / Entry Level",
    badge: "Entry",
    hint: "Core role fundamentals, projects & practical application",
  },
  {
    value: "intermediate",
    label: "Experienced: 1–3 years",
    badge: "Mid",
    hint: "Applied trade-offs, real-world debugging & collaboration",
  },
  {
    value: "experienced",
    label: "Experienced: 3+ years",
    badge: "Senior",
    hint: "Deep architectural trade-offs, leadership & production dilemmas",
  },
];

interface DifficultyOption {
  value: StartingDifficulty;
  label: string;
  pill: string;
  hint: string;
}

const DIFFICULTY_OPTIONS: DifficultyOption[] = [
  {
    value: "easy",
    label: "Easy",
    pill: "Gentle",
    hint: "Approachable fundamentals & straightforward scenarios",
  },
  {
    value: "medium",
    label: "Medium",
    pill: "Standard",
    hint: "Realistic trade-offs, standard depth & balanced challenge",
  },
  {
    value: "hard",
    label: "Hard",
    pill: "Advanced",
    hint: "Complex constraints, conflicting requirements & high-stakes dilemmas",
  },
];

interface ProgressionOption {
  value: ProgressionMode;
  label: string;
  tag: string;
  hint: string;
}

const PROGRESSION_OPTIONS: ProgressionOption[] = [
  {
    value: "adaptive",
    label: "Adaptive Practice",
    tag: "Dynamic AI",
    hint: "Difficulty recalibrates dynamically based on your answer quality",
  },
  {
    value: "mock",
    label: "Mock Assessment",
    tag: "Benchmark",
    hint: "Follows a consistent, planned difficulty curve for benchmarking",
  },
];

interface LengthOption {
  count: number;
  label: string;
  duration: string;
  recommended?: boolean;
}

const QUESTION_LENGTH_OPTIONS: LengthOption[] = [
  {
    count: 5,
    label: "5 Questions",
    duration: "~15 min drill",
  },
  {
    count: 8,
    label: "8 Questions",
    duration: "~25 min session",
    recommended: true,
  },
  {
    count: 10,
    label: "10 Questions",
    duration: "~35 min deep-dive",
  },
];

export default function InterviewSetup({
  onStart,
  onUnauthorized,
  starting,
}: InterviewSetupProps) {
  const { user } = useAuth();
  const [analyses, setAnalyses] = useState<ResumeAnalysisHistoryItem[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);

  // Configuration options
  const [interviewType, setInterviewType] = useState<InterviewType>("technical");
  const [experienceLevel, setExperienceLevel] = useState<ExperienceLevel>(
    (user?.experience_level as ExperienceLevel) || "fresher"
  );
  const [startingDifficulty, setStartingDifficulty] =
    useState<StartingDifficulty>("medium");
  const [progressionMode, setProgressionMode] =
    useState<ProgressionMode>("adaptive");
  const [maxQuestions, setMaxQuestions] = useState<number>(8);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (user?.experience_level && experienceLevel === "fresher") {
      setExperienceLevel(user.experience_level as ExperienceLevel);
    }
  }, [user?.experience_level]);

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
            Customize interview track, candidate background level, starting difficulty,
            and progression pacing for a realistic, calibrated practice experience.
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
              <FileTextIcon size={24} />
            </div>
            <h2>Analyze a resume first</h2>
            <p>
              You need at least one saved resume analysis to calibrate your
              interview questions against your actual background.
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
              <div className="setup-section-heading">
                <span className="setup-step-num">01</span>
                <div>
                  <h2 className="setup-label">Choose Interview Track</h2>
                  <p className="setup-hint">
                    Select whether to focus on core technical mastery or behavioral leadership competencies.
                  </p>
                </div>
              </div>

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
                      <CodeIcon size={22} />
                    </span>
                    <div className="setup-type-title-wrap">
                      <strong>Technical Interview</strong>
                      <span className="badge badge-accent">Role Fundamentals</span>
                    </div>
                  </div>
                  <p className="setup-type-desc">
                    Evaluates core data structures, system architecture, role
                    technologies, and practical debugging grounded in your resume
                    and target role.
                  </p>
                  <ul className="setup-type-tags">
                    <li>Technical Correctness</li>
                    <li>Technical Depth</li>
                    <li>Implementation Trade-offs</li>
                  </ul>
                  {interviewType === "technical" && (
                    <span className="setup-selected-badge">
                      <CheckCircleIcon size={14} /> Selected Track
                    </span>
                  )}
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
                      <UsersIcon size={22} />
                    </span>
                    <div className="setup-type-title-wrap">
                      <strong>HR & Behavioral Interview</strong>
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
                  {interviewType === "hr" && (
                    <span className="setup-selected-badge">
                      <CheckCircleIcon size={14} /> Selected Track
                    </span>
                  )}
                </button>
              </div>
            </div>

            {/* Step 2: Candidate Background & Challenge Level */}
            <div className="setup-section">
              <div className="setup-section-heading">
                <span className="setup-step-num">02</span>
                <div>
                  <h2 className="setup-label">Candidate Background & Challenge Level</h2>
                  <p className="setup-hint">
                    Calibrate the depth of questions and starting expectations for this practice round.
                  </p>
                </div>
              </div>

              <div className="setup-block-group">
                {/* Experience Level Cards */}
                <div className="setup-subgroup">
                  <label className="setup-sublabel">Experience Stage</label>
                  <div className="setup-experience-grid">
                    {EXPERIENCE_LEVEL_OPTIONS.map((opt) => {
                      const isSelected = experienceLevel === opt.value;
                      return (
                        <button
                          key={opt.value}
                          type="button"
                          className={`setup-choice-card ${
                            isSelected ? "selected" : ""
                          }`}
                          onClick={() => setExperienceLevel(opt.value)}
                        >
                          <div className="setup-choice-head">
                            <span className="setup-choice-radio" aria-hidden="true">
                              {isSelected && <span className="setup-choice-radio-dot" />}
                            </span>
                            <strong>{opt.label}</strong>
                            <span className="setup-choice-badge">{opt.badge}</span>
                          </div>
                          <p className="setup-choice-hint">{opt.hint}</p>
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Starting Difficulty Buttons */}
                <div className="setup-subgroup">
                  <label className="setup-sublabel">Preferred Starting Difficulty</label>
                  <div className="setup-difficulty-grid">
                    {DIFFICULTY_OPTIONS.map((opt) => {
                      const isSelected = startingDifficulty === opt.value;
                      return (
                        <button
                          key={opt.value}
                          type="button"
                          className={`setup-difficulty-card difficulty-${opt.value} ${
                            isSelected ? "selected" : ""
                          }`}
                          onClick={() => setStartingDifficulty(opt.value)}
                        >
                          <div className="setup-difficulty-head">
                            <span className="difficulty-indicator-dot" />
                            <strong>{opt.label}</strong>
                            <span className="difficulty-pill">{opt.pill}</span>
                          </div>
                          <p className="setup-difficulty-hint">{opt.hint}</p>
                        </button>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>

            {/* Step 3: Progression Mode & Question Length */}
            <div className="setup-section">
              <div className="setup-section-heading">
                <span className="setup-step-num">03</span>
                <div>
                  <h2 className="setup-label">Progression Mode & Session Length</h2>
                  <p className="setup-hint">
                    Choose whether the interview adapts question difficulty in real time and set your target pacing.
                  </p>
                </div>
              </div>

              <div className="setup-progression-row">
                {/* Progression Mode Cards */}
                <div className="setup-progression-group">
                  <label className="setup-sublabel">Interview Progression Engine</label>
                  <div className="setup-progression-grid">
                    {PROGRESSION_OPTIONS.map((opt) => {
                      const isSelected = progressionMode === opt.value;
                      return (
                        <button
                          key={opt.value}
                          type="button"
                          className={`setup-choice-card ${
                            isSelected ? "selected" : ""
                          }`}
                          onClick={() => setProgressionMode(opt.value)}
                        >
                          <div className="setup-choice-head">
                            <span className="setup-choice-radio" aria-hidden="true">
                              {isSelected && <span className="setup-choice-radio-dot" />}
                            </span>
                            <strong>{opt.label}</strong>
                            <span className="setup-choice-badge">{opt.tag}</span>
                          </div>
                          <p className="setup-choice-hint">{opt.hint}</p>
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Question Count Options */}
                <div className="setup-length-group">
                  <label className="setup-sublabel">Session Length</label>
                  <div className="setup-length-grid">
                    {QUESTION_LENGTH_OPTIONS.map((opt) => {
                      const isSelected = maxQuestions === opt.count;
                      return (
                        <button
                          key={opt.count}
                          type="button"
                          className={`setup-length-card ${
                            isSelected ? "selected" : ""
                          }`}
                          onClick={() => setMaxQuestions(opt.count)}
                        >
                          <div className="setup-length-header">
                            <strong className="setup-length-count">{opt.label}</strong>
                            {opt.recommended && (
                              <span className="setup-rec-badge">Recommended</span>
                            )}
                          </div>
                          <span className="setup-length-duration">{opt.duration}</span>
                        </button>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>

            {/* Step 4: Resume Profile Grounding */}
            <div className="setup-section">
              <div className="setup-section-heading">
                <span className="setup-step-num">04</span>
                <div>
                  <h2 className="setup-label">Select Resume Profile</h2>
                  <p className="setup-hint">
                    The AI calibrator grounds technical questions, project dilemmas, and architecture trade-offs in this saved profile.
                  </p>
                </div>
              </div>

              <div className="setup-profiles-container">
                <div className="setup-profiles-grid">
                  {analyses.map((item) => {
                    const active = selectedId === item.id;
                    return (
                      <div
                        key={item.id}
                        role="button"
                        tabIndex={0}
                        className={`setup-profile-card ${active ? "selected" : ""}`}
                        onClick={() => setSelectedId(item.id)}
                        onKeyDown={(e) => {
                          if (e.key === "Enter" || e.key === " ") {
                            e.preventDefault();
                            setSelectedId(item.id);
                          }
                        }}
                      >
                        <div className="setup-profile-left">
                          <span
                            className={`setup-profile-radio ${active ? "active" : ""}`}
                            aria-hidden="true"
                          >
                            {active && <span className="setup-profile-radio-dot" />}
                          </span>
                          <div className="setup-profile-info">
                            <strong className="setup-profile-role">{item.job_role}</strong>
                            <div className="setup-profile-meta">
                              <span className="setup-profile-filename">{item.filename}</span>
                              <span className="setup-profile-dot">·</span>
                              <span className="setup-profile-date">
                                {formatDateTime(item.created_at)}
                              </span>
                            </div>
                          </div>
                        </div>

                        <div className="setup-profile-right">
                          <span className="badge badge-accent tabular-nums">
                            {Math.round(item.match_score)}% match
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Step 5: Pre-Flight Configuration Summary & Launch Action */}
            <div className="setup-summary-card">
              <div className="setup-summary-header">
                <span className="setup-summary-eyebrow">Session Summary</span>
                <span className="setup-summary-status">Ready to initialize</span>
              </div>

              <div className="summary-pillars-grid">
                <div className="summary-pillar">
                  <span className="summary-label">Interview Track</span>
                  <strong className="summary-val">
                    {interviewType === "hr"
                      ? "HR & Behavioral"
                      : "Technical Interview"}
                  </strong>
                </div>
                <div className="summary-pillar">
                  <span className="summary-label">Experience Stage</span>
                  <strong className="summary-val">
                    {EXPERIENCE_LEVEL_OPTIONS.find(
                      (o) => o.value === experienceLevel,
                    )?.label ?? experienceLevel}
                  </strong>
                </div>
                <div className="summary-pillar">
                  <span className="summary-label">Starting Difficulty</span>
                  <strong className="summary-val">
                    {startingDifficulty.charAt(0).toUpperCase() +
                      startingDifficulty.slice(1)}
                  </strong>
                </div>
                <div className="summary-pillar">
                  <span className="summary-label">Progression Mode</span>
                  <strong className="summary-val">
                    {progressionMode === "adaptive"
                      ? "Adaptive Practice"
                      : "Mock Assessment"}
                  </strong>
                </div>
                <div className="summary-pillar">
                  <span className="summary-label">Length</span>
                  <strong className="summary-val">
                    {maxQuestions} Questions
                  </strong>
                </div>
              </div>

              {selectedResume && (
                <div className="summary-target-banner">
                  <FileTextIcon size={16} />
                  <span>
                    Grounded in: <strong>{selectedResume.job_role}</strong> (
                    {selectedResume.filename})
                  </span>
                </div>
              )}

              <div className="setup-launch-footer">
                <div className="setup-launch-tip">
                  💡 Questions adapt as you answer. You can ask for progressive hints anytime during the session.
                </div>
                <button
                  type="button"
                  className="btn btn-primary setup-launch-btn"
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
                      ? "Initializing Session..."
                      : `Start ${
                          interviewType === "hr" ? "HR" : "Technical"
                        } Interview`}
                  </span>
                  {!starting && <ArrowRightIcon size={16} />}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
