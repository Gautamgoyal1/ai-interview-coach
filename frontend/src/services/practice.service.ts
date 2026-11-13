import { apiRequest } from "./api";
import type {
  CreatePracticeSessionPayload,
  GeneratePracticeQuestionPayload,
  PracticeAttempt,
  PracticeQuestion,
  PracticeRecommendationItem,
  PracticeSessionDetail,
  PracticeSessionSummary,
  RevealHintResponse,
  RevealReferenceResponse,
  SubmitPracticeAttemptPayload,
} from "../types/practice";

export async function createPracticeSession(
  payload: CreatePracticeSessionPayload,
): Promise<PracticeSessionDetail> {
  return apiRequest<PracticeSessionDetail>("/practice/sessions", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function listPracticeSessions(
  limit = 20,
  offset = 0,
): Promise<PracticeSessionSummary[]> {
  return apiRequest<PracticeSessionSummary[]>(
    `/practice/sessions?limit=${limit}&offset=${offset}`,
  );
}

export async function getPracticeSession(
  sessionId: string,
): Promise<PracticeSessionDetail> {
  return apiRequest<PracticeSessionDetail>(
    `/practice/sessions/${encodeURIComponent(sessionId)}`,
  );
}

export async function deletePracticeSession(
  sessionId: string,
): Promise<{ status: string; session_id: string }> {
  return apiRequest<{ status: string; session_id: string }>(
    `/practice/sessions/${encodeURIComponent(sessionId)}`,
    {
      method: "DELETE",
    },
  );
}

export async function generateNextQuestion(
  sessionId: string,
  payload: GeneratePracticeQuestionPayload = {},
): Promise<PracticeQuestion> {
  return apiRequest<PracticeQuestion>(
    `/practice/sessions/${encodeURIComponent(sessionId)}/questions`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}

export async function revealHint(
  questionId: string,
  level: number,
): Promise<RevealHintResponse> {
  return apiRequest<RevealHintResponse>(
    `/practice/questions/${encodeURIComponent(questionId)}/hints/${level}/reveal`,
    {
      method: "POST",
    },
  );
}

export async function revealReference(
  questionId: string,
): Promise<RevealReferenceResponse> {
  return apiRequest<RevealReferenceResponse>(
    `/practice/questions/${encodeURIComponent(questionId)}/reference/reveal`,
    {
      method: "POST",
    },
  );
}

export async function submitPracticeAttempt(
  questionId: string,
  payload: SubmitPracticeAttemptPayload,
): Promise<PracticeAttempt> {
  return apiRequest<PracticeAttempt>(
    `/practice/questions/${encodeURIComponent(questionId)}/attempts`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}

export async function listQuestionAttempts(
  questionId: string,
): Promise<PracticeAttempt[]> {
  return apiRequest<PracticeAttempt[]>(
    `/practice/questions/${encodeURIComponent(questionId)}/attempts`,
  );
}

export async function getPracticeRecommendations(
  limit = 5,
): Promise<PracticeRecommendationItem[]> {
  return apiRequest<PracticeRecommendationItem[]>(
    `/practice/recommendations?limit=${limit}`,
  );
}
