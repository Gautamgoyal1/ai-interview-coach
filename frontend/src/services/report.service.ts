import { apiRequest } from "./api";
import type {
  InterviewReport,
  InterviewReportSummary,
} from "../types/report";

export async function generateInterviewReport(
  sessionId: string,
): Promise<InterviewReport> {
  return apiRequest<InterviewReport>(
    `/reports/interviews/${encodeURIComponent(sessionId)}/generate`,
    { method: "POST" },
  );
}

export async function getInterviewReport(
  sessionId: string,
): Promise<InterviewReport> {
  return apiRequest<InterviewReport>(
    `/reports/interviews/${encodeURIComponent(sessionId)}`,
  );
}

export async function listInterviewReports(
  limit = 20,
): Promise<InterviewReportSummary[]> {
  return apiRequest<InterviewReportSummary[]>(
    `/reports?limit=${encodeURIComponent(limit)}`,
  );
}

export async function deleteInterviewReport(
  sessionId: string,
): Promise<{ deleted: boolean; session_id: string }> {
  return apiRequest<{ deleted: boolean; session_id: string }>(
    `/reports/interviews/${encodeURIComponent(sessionId)}`,
    { method: "DELETE" },
  );
}
