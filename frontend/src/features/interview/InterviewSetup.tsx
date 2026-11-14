import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type FormEvent,
} from "react";
import { Link } from "react-router-dom";
import { ArrowRightIcon, FileTextIcon } from "../../components/Icons";
import { getResumeAnalyses } from "../../services/resume.service";
import { useAuth } from "../../hooks/useAuth";
import type {
  ExperienceLevel,
  InterviewType,
  ProgressionMode,
  StartingDifficulty,
} from "../../types/interview";
import type { InterviewInputMode } from "../../types/speech";
import type { ResumeAnalysisHistoryItem } from "../../types/resume";
import type { StartInterviewOptions } from "./useInterview";
import { formatDateTime } from "../../utils/formatters";
import "./InterviewSetup.css";

interface InterviewSetupProps {
  onStart: (
    analysisId: number,
    options: StartInterviewOptions,
  ) => void | Promise<void>;
  onUnauthorized: () => void;
  starting: boolean;
  initialAnalysisId?: number;
}
const levels: Array<{ value: ExperienceLevel; label: string }> = [
  { value: "internship", label: "Student / Internship" },
  { value: "fresher", label: "Fresher / Entry Level" },
  { value: "intermediate", label: "Intermediate" },
  { value: "experienced", label: "Experienced / Senior" },
];
const recommendedDifficulty = (level: ExperienceLevel): StartingDifficulty =>
  level === "internship" ? "easy" : "medium";

export default function InterviewSetup({
  onStart,
  onUnauthorized,
  starting,
  initialAnalysisId,
}: InterviewSetupProps) {
  const { user } = useAuth();
  const profileLevel = levels.some(
    (level) => level.value === user?.experience_level,
  )
    ? (user!.experience_level as ExperienceLevel)
    : "fresher";
  const [analyses, setAnalyses] = useState<ResumeAnalysisHistoryItem[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [interviewType, setInterviewType] =
    useState<InterviewType>("technical");
  const [inputMode, setInputMode] = useState<InterviewInputMode>("text");
  const [experienceLevel, setExperienceLevel] =
    useState<ExperienceLevel>(profileLevel);
  const [startingDifficulty, setStartingDifficulty] =
    useState<StartingDifficulty>(recommendedDifficulty(profileLevel));
  const [progressionMode, setProgressionMode] =
    useState<ProgressionMode>("adaptive");
  const [maxQuestions, setMaxQuestions] = useState(8);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [launching, setLaunching] = useState(false);
  const launchLock = useRef(false);
  const customDifficulty = useRef(false);
  const generation = useRef(0);
  const load = useCallback(async () => {
    const run = ++generation.current;
    setLoading(true);
    setError(null);
    try {
      const list = await getResumeAnalyses(20);
      if (run !== generation.current) return;
      setAnalyses(list);
      setSelectedId((previous) => {
        if (
          initialAnalysisId &&
          list.some((item) => item.id === initialAnalysisId)
        )
          return initialAnalysisId;
        if (previous && list.some((item) => item.id === previous))
          return previous;
        return (
          list.find(
            (item) =>
              item.job_role.toLowerCase() === user?.target_role?.toLowerCase(),
          )?.id ||
          list[0]?.id ||
          null
        );
      });
    } catch (failure) {
      if (run !== generation.current) return;
      if (
        failure &&
        typeof failure === "object" &&
        "status" in failure &&
        failure.status === 401
      ) {
        onUnauthorized();
        return;
      }
      setError(
        "Your saved resumes could not be loaded. Retry to choose a profile; your saved work has not been removed.",
      );
    } finally {
      if (run === generation.current) setLoading(false);
    }
  }, [initialAnalysisId, onUnauthorized, user?.target_role]);
  useEffect(() => {
    void load();
    return () => {
      generation.current++;
    };
  }, [load]);
  const selected = analyses.find((item) => item.id === selectedId);
  const busy = starting || launching;
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selected || loading || error || busy || launchLock.current) return;
    launchLock.current = true;
    setLaunching(true);
    try {
      await onStart(selected.id, {
        interviewType,
        inputMode,
        experienceLevel,
        startingDifficulty,
        progressionMode,
        maxQuestions,
      });
    } finally {
      launchLock.current = false;
      setLaunching(false);
    }
  }

  return (
    <section className="setup-workbench">
      <header className="setup-intro">
        <p className="pm-eyebrow">Interview preparation</p>
        <h1>Set up your interview</h1>
        <p>
          A focused round, built around your experience. Choose how you want to
          practice.
        </p>
      </header>
      {loading && (
        <div className="pm-status-banner" role="status">
          <span className="pm-spinner" aria-hidden="true" />
          <div>
            <strong>Loading your saved analyses</strong>
            <p>Your preferences are kept while we load your resumes.</p>
          </div>
        </div>
      )}
      {error && (
        <div className="pm-alert-error" role="alert">
          <span>{error}</span>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => void load()}
            disabled={loading}
          >
            Retry
          </button>
        </div>
      )}
      {!loading && !error && !analyses.length ? (
        <div className="setup-first-step">
          <FileTextIcon size={28} />
          <p className="pm-eyebrow">A little context first</p>
          <h2>Start with your resume</h2>
          <p>
            Analyze a PDF for your target role. Your saved analysis gives the
            interview relevant skills and gaps to explore.
          </p>
          <Link to="/analyze" className="btn btn-primary">
            Analyze Resume
            <ArrowRightIcon size={15} />
          </Link>
          <Link to="/practice" className="setup-secondary-link">
            Prefer a quick topic drill? Open Practice Hub
          </Link>
        </div>
      ) : (
        <form
          className="setup-layout"
          onSubmit={(event) => void submit(event)}
          aria-label="Interview configuration"
          aria-busy={loading || busy}
        >
          <div className="setup-configuration">
            <section className="setup-profile-section">
              <div className="setup-field-heading">
                <span>01</span>
                <h2>Your starting point</h2>
              </div>
              <label htmlFor="setup-resume">Resume profile</label>
              <select
                id="setup-resume"
                className="pm-select"
                value={selectedId || ""}
                onChange={(event) => setSelectedId(Number(event.target.value))}
                disabled={loading || busy || !!error}
                required
              >
                <option value="" disabled>
                  Choose a saved resume
                </option>
                {analyses.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.job_role} - {item.filename}
                  </option>
                ))}
              </select>
              {selected && (
                <div className="setup-profile-context">
                  <FileTextIcon size={18} />
                  <div>
                    <strong>{selected.job_role}</strong>
                    <p>{selected.filename}</p>
                    <span>
                      Analyzed {formatDateTime(selected.created_at)} &middot;{" "}
                      {selected.match_score.toFixed(0)}% resume match
                    </span>
                  </div>
                  <Link to={`/history/${selected.id}`}>View analysis</Link>
                </div>
              )}
            </section>
            <section>
              <div className="setup-field-heading">
                <span>02</span>
                <h2>Choose your round</h2>
              </div>
              <fieldset className="setup-radio-field" disabled={busy}>
                <legend>Interview track</legend>
                <div className="setup-choice-pair">
                  {(
                    [
                      [
                        "technical",
                        "Technical",
                        "Skills, problem solving and practical trade-offs.",
                      ],
                      [
                        "hr",
                        "HR / Behavioral",
                        "Decisions, teamwork and your experience.",
                      ],
                    ] as const
                  ).map(([value, label, hint]) => (
                    <label className="setup-choice" key={value}>
                      <input
                        type="radio"
                        name="interview-track"
                        value={value}
                        checked={interviewType === value}
                        onChange={() => setInterviewType(value)}
                      />
                      <span>
                        <strong>{label}</strong>
                        <small>{hint}</small>
                      </span>
                    </label>
                  ))}
                </div>
              </fieldset>
              <fieldset className="setup-radio-field" disabled={busy}>
                <legend>Answer format</legend>
                <div className="setup-choice-pair">
                  {(
                    [
                      ["text", "Text", "Type and edit your answers."],
                      [
                        "voice",
                        "Voice",
                        "Speak, review your transcript, then submit.",
                      ],
                    ] as const
                  ).map(([value, label, hint]) => (
                    <label className="setup-choice" key={value}>
                      <input
                        type="radio"
                        name="answer-format"
                        value={value}
                        checked={inputMode === value}
                        onChange={() => setInputMode(value)}
                      />
                      <span>
                        <strong>{label}</strong>
                        <small>{hint}</small>
                      </span>
                    </label>
                  ))}
                </div>
                <p className="setup-field-help">
                  {inputMode === "voice"
                    ? "Questions are spoken after you start. Recording only begins when you choose Start Speaking."
                    : "No microphone needed. You can switch formats inside the interview."}
                </p>
              </fieldset>
            </section>
            <section>
              <div className="setup-field-heading">
                <span>03</span>
                <h2>Set the pace</h2>
              </div>
              <div className="setup-settings-row">
                <div>
                  <label htmlFor="setup-experience">Experience level</label>
                  <select
                    id="setup-experience"
                    className="pm-select"
                    value={experienceLevel}
                    disabled={busy}
                    onChange={(event) => {
                      const level = event.target.value as ExperienceLevel;
                      setExperienceLevel(level);
                      if (!customDifficulty.current)
                        setStartingDifficulty(recommendedDifficulty(level));
                    }}
                  >
                    {levels.map((level) => (
                      <option value={level.value} key={level.value}>
                        {level.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label htmlFor="setup-difficulty">Starting difficulty</label>
                  <select
                    id="setup-difficulty"
                    className="pm-select"
                    value={startingDifficulty}
                    disabled={busy}
                    onChange={(event) => {
                      customDifficulty.current = true;
                      setStartingDifficulty(
                        event.target.value as StartingDifficulty,
                      );
                    }}
                  >
                    {["easy", "medium", "hard"].map((value) => (
                      <option key={value} value={value}>
                        {value[0].toUpperCase() + value.slice(1)}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <p className="setup-field-help">
                {customDifficulty.current
                  ? "Custom starting difficulty."
                  : `Recommended for ${levels.find((level) => level.value === experienceLevel)?.label.toLowerCase()}.`}
                {user?.experience_level === experienceLevel
                  ? " Experience from your profile."
                  : ""}
              </p>
              <fieldset
                className="setup-radio-field setup-length"
                disabled={busy}
              >
                <legend>Interview length</legend>
                <div>
                  {[5, 8, 10].map((count) => (
                    <label className="setup-choice" key={count}>
                      <input
                        type="radio"
                        name="question-count"
                        value={count}
                        checked={maxQuestions === count}
                        onChange={() => setMaxQuestions(count)}
                      />
                      <span>
                        <strong>{count} questions</strong>
                        <small>
                          {count === 8
                            ? "Recommended"
                            : count === 5
                              ? "Short round"
                              : "More depth"}
                        </small>
                      </span>
                    </label>
                  ))}
                </div>
                <p className="setup-field-help">
                  Follow-up questions may extend the round. Take the time you
                  need.
                </p>
              </fieldset>
              <details className="setup-advanced">
                <summary>
                  Advanced settings
                  <span>
                    {progressionMode === "adaptive"
                      ? "Adaptive practice"
                      : "Mock assessment"}
                  </span>
                </summary>
                <fieldset className="setup-radio-field" disabled={busy}>
                  <legend>Question progression</legend>
                  {(
                    [
                      [
                        "adaptive",
                        "Adaptive Practice",
                        "Difficulty responds to your answers.",
                      ],
                      [
                        "mock",
                        "Mock Assessment",
                        "A planned difficulty curve for a consistent round.",
                      ],
                    ] as const
                  ).map(([value, label, hint]) => (
                    <label className="setup-choice" key={value}>
                      <input
                        type="radio"
                        name="progression-mode"
                        value={value}
                        checked={progressionMode === value}
                        onChange={() => setProgressionMode(value)}
                      />
                      <span>
                        <strong>{label}</strong>
                        <small>{hint}</small>
                      </span>
                    </label>
                  ))}
                </fieldset>
              </details>
            </section>
          </div>
          <aside className="setup-launch" aria-label="Interview summary">
            <p className="pm-eyebrow">Ready when you are</p>
            <h2>
              {interviewType === "hr"
                ? "Your behavioral round"
                : "Your technical round"}
            </h2>
            <p>{selected?.job_role || "Choose a resume to continue."}</p>
            <dl>
              <div>
                <dt>Format</dt>
                <dd>
                  {inputMode === "voice"
                    ? "Voice + editable transcript"
                    : "Text answers"}
                </dd>
              </div>
              <div>
                <dt>Starting point</dt>
                <dd>
                  {startingDifficulty[0].toUpperCase() +
                    startingDifficulty.slice(1)}{" "}
                  &middot;{" "}
                  {
                    levels.find((level) => level.value === experienceLevel)
                      ?.label
                  }
                </dd>
              </div>
              <div>
                <dt>Round</dt>
                <dd>
                  {maxQuestions} questions &middot;{" "}
                  {progressionMode === "adaptive" ? "Adaptive" : "Mock"}
                </dd>
              </div>
            </dl>
            <button
              className="btn btn-primary setup-start"
              type="submit"
              disabled={!selected || loading || !!error || busy}
            >
              {busy
                ? "Preparing interview..."
                : `Start ${interviewType === "hr" ? "HR" : "Technical"} Interview`}
              {!busy && <ArrowRightIcon size={16} />}
            </button>
            <p className="setup-launch-note">
              Review your choices, then start. Hints and answer coaching are
              available separately in Practice Mode.
            </p>
            <Link className="setup-secondary-link" to="/history">
              Manage saved resumes
            </Link>
          </aside>
        </form>
      )}
    </section>
  );
}
