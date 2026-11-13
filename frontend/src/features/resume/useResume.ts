import { useState } from "react";
import { ApiError } from "../../services/api";
import { analyzeResume } from "../../services/resume.service";
import type { ResumeAnalysisResult } from "../../types/resume";

export function useResume() {
  const [result, setResult] = useState<ResumeAnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [unauthorized, setUnauthorized] = useState(false);

  async function submitResume(
    file: File,
    jobRole: string,
    jobDescription: string,
    forceReanalyze = false,
  ) {
    setLoading(true);
    setError(null);
    setUnauthorized(false);
    if (!forceReanalyze) {
      setResult(null);
    }

    try {
      const data = await analyzeResume(
        file,
        jobRole,
        jobDescription,
        forceReanalyze,
      );
      setResult(data);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        setUnauthorized(true);
      }
      setError(
        err instanceof Error ? err.message : "Resume analysis failed.",
      );
    } finally {
      setLoading(false);
    }
  }

  return { result, loading, error, unauthorized, submitResume };
}
