import { useCallback, useRef, useState } from "react";
import { ApiError } from "../../services/api";
import {
  endInterviewSession,
  getInterviewSession,
  startInterview,
  submitInterviewAnswer,
} from "../../services/interview.service";
import type {
  ExperienceLevel,
  InterviewSession,
  InterviewType,
  ProgressionMode,
  StartingDifficulty,
} from "../../types/interview";

export interface StartInterviewOptions {
  interviewType?: InterviewType;
  experienceLevel?: ExperienceLevel;
  startingDifficulty?: StartingDifficulty;
  progressionMode?: ProgressionMode;
  maxQuestions?: number;
}

export function useInterview() {
  const [session, setSession] = useState<InterviewSession | null>(null);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [unauthorized, setUnauthorized] = useState(false);
  const inFlightRef = useRef(false);

  const handleError = useCallback((err: unknown, fallback: string) => {
    if (err instanceof ApiError && err.status === 401) {
      setUnauthorized(true);
    }
    setError(err instanceof Error ? err.message : fallback);
  }, []);

  const beginSession = useCallback(
    async (
      analysisId: number,
      options?: StartInterviewOptions,
    ): Promise<InterviewSession | null> => {
      if (inFlightRef.current) return null;
      inFlightRef.current = true;
      setLoading(true);
      setError(null);
      setUnauthorized(false);

      try {
        const created = await startInterview(
          analysisId,
          options?.maxQuestions ?? 8,
          1,
          options?.experienceLevel ?? "fresher",
          options?.interviewType ?? "technical",
          options?.startingDifficulty ?? "medium",
          options?.progressionMode ?? "adaptive",
        );
        setSession(created);
        return created;
      } catch (err) {
        handleError(err, "Could not start the interview session.");
        return null;
      } finally {
        setLoading(false);
        inFlightRef.current = false;
      }
    },
    [handleError],
  );

  const loadSession = useCallback(
    async (sessionId: string): Promise<InterviewSession | null> => {
      setLoading(true);
      setError(null);
      setUnauthorized(false);

      try {
        const loaded = await getInterviewSession(sessionId);
        setSession(loaded);
        return loaded;
      } catch (err) {
        handleError(err, "Could not load the interview session.");
        return null;
      } finally {
        setLoading(false);
      }
    },
    [handleError],
  );

  const submitAnswer = useCallback(
    async (
      sessionId: string,
      questionId: string,
      answer: string,
    ): Promise<InterviewSession | null> => {
      const trimmed = answer.trim();
      if (!trimmed) {
        setError("Please enter an answer before submitting.");
        return null;
      }
      if (inFlightRef.current) return null;

      inFlightRef.current = true;
      setSubmitting(true);
      setError(null);
      setUnauthorized(false);

      try {
        const updated = await submitInterviewAnswer(
          sessionId,
          questionId,
          trimmed,
        );
        setSession(updated);
        return updated;
      } catch (err) {
        handleError(err, "Failed to submit your answer. Please try again.");
        return null;
      } finally {
        setSubmitting(false);
        inFlightRef.current = false;
      }
    },
    [handleError],
  );

  const finishSession = useCallback(
    async (sessionId: string): Promise<InterviewSession | null> => {
      if (inFlightRef.current) return null;
      inFlightRef.current = true;
      setSubmitting(true);
      setError(null);
      setUnauthorized(false);

      try {
        const ended = await endInterviewSession(sessionId);
        setSession(ended);
        return ended;
      } catch (err) {
        handleError(err, "Could not end the interview session.");
        return null;
      } finally {
        setSubmitting(false);
        inFlightRef.current = false;
      }
    },
    [handleError],
  );

  return {
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
  };
}
