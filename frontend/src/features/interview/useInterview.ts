import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError } from "../../services/api";
import {
  endInterviewSession,
  getInterviewSession,
  startInterview,
  submitInterviewAnswer,
  retryInterviewQuestion,
} from "../../services/interview.service";
import type {
  ExperienceLevel,
  InterviewSession,
  InterviewType,
  ProgressionMode,
  StartingDifficulty,
} from "../../types/interview";
import type { InterviewInputMode } from "../../types/speech";

export interface StartInterviewOptions {
  interviewType?: InterviewType;
  experienceLevel?: ExperienceLevel;
  startingDifficulty?: StartingDifficulty;
  progressionMode?: ProgressionMode;
  maxQuestions?: number;
  inputMode?: InterviewInputMode;
}

export function useInterview() {
  const [session, setSession] = useState<InterviewSession | null>(null);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [unauthorized, setUnauthorized] = useState(false);
  const inFlightRef = useRef(false);
  const loadRequestRef = useRef(0);
  useEffect(() => () => { loadRequestRef.current++; }, []);

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
      const request = ++loadRequestRef.current;
      setLoading(true);
      setError(null);
      setUnauthorized(false);

      try {
        const loaded = await getInterviewSession(sessionId);
        if (request !== loadRequestRef.current) return null;
        setSession(loaded);
        return loaded;
      } catch (err) {
        if (request === loadRequestRef.current) handleError(err, "Could not load the interview session.");
        return null;
      } finally {
        if (request === loadRequestRef.current) setLoading(false);
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
        if (err instanceof ApiError && err.status === 503) {
          // A completed grade may already be saved. Refresh the public recovery
          // flag rather than inviting a duplicate answer submission.
          try {
            const saved = await getInterviewSession(sessionId);
            if (saved.generation_unavailable) setSession(saved);
          } catch (refreshError) {
            if (refreshError instanceof ApiError && refreshError.status === 401) {
              handleError(refreshError, "Please sign in again.");
            }
          }
        }
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

  const retryQuestion = useCallback(async (sessionId: string): Promise<InterviewSession | null> => {
    if (inFlightRef.current) return null;
    inFlightRef.current = true;
    setSubmitting(true);
    setError(null);
    try {
      const updated = await retryInterviewQuestion(sessionId);
      setSession(updated);
      return updated;
    } catch (err) {
      handleError(err, "The next question is still unavailable. Your answer is saved.");
      return null;
    } finally {
      setSubmitting(false);
      inFlightRef.current = false;
    }
  }, [handleError]);

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
    retryQuestion,
  };
}
