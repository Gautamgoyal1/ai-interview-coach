import { apiRequest } from "./api";
import type {
  ExperienceLevel,
  InterviewSession,
  InterviewType,
  ProgressionMode,
  StartingDifficulty,
} from "../types/interview";

export async function startInterview(
  analysisId: number,
  maxQuestions = 8,
  maxFollowUps = 1,
  experienceLevel: ExperienceLevel = "fresher",
  interviewType: InterviewType = "technical",
  startingDifficulty: StartingDifficulty = "medium",
  progressionMode: ProgressionMode = "adaptive",
): Promise<InterviewSession> {
  return apiRequest<InterviewSession>("/interview/start", {
    method: "POST",
    body: JSON.stringify({
      analysis_id: analysisId,
      interview_type: interviewType,
      experience_level: experienceLevel,
      starting_difficulty: startingDifficulty,
      progression_mode: progressionMode,
      max_questions: maxQuestions,
      max_follow_ups: maxFollowUps,
    }),
  });
}

export async function getInterviewSession(
  sessionId: string,
): Promise<InterviewSession> {
  return apiRequest<InterviewSession>(
    `/interview/${encodeURIComponent(sessionId)}`,
  );
}

export async function submitInterviewAnswer(
  sessionId: string,
  questionId: string,
  answer: string,
): Promise<InterviewSession> {
  return apiRequest<InterviewSession>(
    `/interview/${encodeURIComponent(sessionId)}/answer`,
    {
      method: "POST",
      body: JSON.stringify({
        question_id: questionId,
        answer,
      }),
    },
  );
}

export async function endInterviewSession(
  sessionId: string,
): Promise<InterviewSession> {
  return apiRequest<InterviewSession>(
    `/interview/${encodeURIComponent(sessionId)}/end`,
    {
      method: "POST",
    },
  );
}

export async function deleteInterviewSession(
  sessionId: string,
): Promise<{ deleted: boolean; session_id: string }> {
  return apiRequest<{ deleted: boolean; session_id: string }>(
    `/interview/${encodeURIComponent(sessionId)}`,
    {
      method: "DELETE",
    },
  );
}
