import { apiRequest } from "./api";
import type {
  DeleteAnalysisResponse,
  ResumeAnalysisHistoryItem,
  ResumeAnalysisResult,
  SavedResumeAnalysis,
} from "../types/resume";

export async function analyzeResume(
  file: File,
  jobRole: string,
  jobDescription?: string,
  forceReanalyze = false,
): Promise<ResumeAnalysisResult> {
  const formData = new FormData();

  formData.append("file", file);
  formData.append("job_role", jobRole);

  if (jobDescription?.trim()) {
    formData.append("job_description", jobDescription.trim());
  }

  if (forceReanalyze) {
    formData.append("force_reanalyze", "true");
  }

  return apiRequest<ResumeAnalysisResult>("/resume/analyze", {
    method: "POST",
    body: formData,
  });
}

export async function getResumeAnalyses(
  limit = 20,
): Promise<ResumeAnalysisHistoryItem[]> {
  return apiRequest<ResumeAnalysisHistoryItem[]>(
    `/resume/analyses?limit=${encodeURIComponent(limit)}`,
  );
}

export async function getResumeAnalysisById(
  analysisId: number,
): Promise<SavedResumeAnalysis> {
  return apiRequest<SavedResumeAnalysis>(
    `/resume/analyses/${encodeURIComponent(analysisId)}`,
  );
}

export async function deleteResumeAnalysis(
  analysisId: number,
  cascade = false,
): Promise<DeleteAnalysisResponse> {
  return apiRequest<DeleteAnalysisResponse>(
    `/resume/analyses/${encodeURIComponent(analysisId)}?cascade=${cascade ? "true" : "false"}`,
    { method: "DELETE" },
  );
}
