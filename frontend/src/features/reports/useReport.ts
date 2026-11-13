import { useCallback, useState } from "react";
import { ApiError } from "../../services/api";
import {
  generateInterviewReport,
  getInterviewReport,
  listInterviewReports,
} from "../../services/report.service";
import type {
  InterviewReport,
  InterviewReportSummary,
} from "../../types/report";

export function useReport() {
  const [report, setReport] = useState<InterviewReport | null>(null);
  const [summaries, setSummaries] = useState<InterviewReportSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [notGenerated, setNotGenerated] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [unauthorized, setUnauthorized] = useState(false);

  const handleError = useCallback((err: unknown, fallback: string) => {
    if (err instanceof ApiError && err.status === 401) {
      setUnauthorized(true);
    }
    setError(err instanceof Error ? err.message : fallback);
  }, []);

  const loadOrGenerateReport = useCallback(
    async (sessionId: string) => {
      setLoading(true);
      setError(null);
      setNotGenerated(false);
      setUnauthorized(false);

      try {
        const existing = await getInterviewReport(sessionId);
        setReport(existing);
      } catch (err) {
        if (err instanceof ApiError && err.status === 401) {
          setUnauthorized(true);
          return;
        }
        if (err instanceof ApiError && err.status === 404) {
          setNotGenerated(true);
          setGenerating(true);
          try {
            const created = await generateInterviewReport(sessionId);
            setReport(created);
            setNotGenerated(false);
          } catch (genErr) {
            handleError(genErr, "Could not generate the interview report.");
          } finally {
            setGenerating(false);
          }
          return;
        }
        handleError(err, "Could not load the interview report.");
      } finally {
        setLoading(false);
      }
    },
    [handleError],
  );

  const retryGenerate = useCallback(
    async (sessionId: string) => {
      setGenerating(true);
      setError(null);
      setUnauthorized(false);
      try {
        const created = await generateInterviewReport(sessionId);
        setReport(created);
        setNotGenerated(false);
      } catch (err) {
        handleError(err, "Could not generate the interview report.");
      } finally {
        setGenerating(false);
      }
    },
    [handleError],
  );

  const loadReportHistory = useCallback(async () => {
    setLoading(true);
    setError(null);
    setUnauthorized(false);
    try {
      const list = await listInterviewReports();
      setSummaries(list);
    } catch (err) {
      handleError(err, "Could not load your interview reports.");
    } finally {
      setLoading(false);
    }
  }, [handleError]);

  const removeSummary = useCallback((sessionId: string) => {
    setSummaries((prev) => prev.filter((item) => item.session_id !== sessionId));
  }, []);

  const clearReport = useCallback(() => {
    setReport(null);
  }, []);

  return {
    report,
    summaries,
    loading,
    generating,
    notGenerated,
    error,
    unauthorized,
    loadOrGenerateReport,
    retryGenerate,
    loadReportHistory,
    removeSummary,
    clearReport,
  };
}
