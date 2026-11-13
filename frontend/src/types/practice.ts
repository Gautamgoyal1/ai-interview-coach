export type InterviewType = "technical" | "hr";
export type PracticeDifficulty = "easy" | "medium" | "hard";
export type AssistanceLevel = "independent" | "hint_assisted" | "reference_assisted";

export interface CreatePracticeSessionPayload {
  topic: string;
  interview_type?: InterviewType;
  target_role?: string;
  experience_level?: string;
  source_report_id?: number | null;
  weakness_context?: string | null;
  difficulty?: PracticeDifficulty;
}

export interface GeneratePracticeQuestionPayload {
  difficulty?: PracticeDifficulty;
  focus_concept?: string | null;
}

export interface SubmitPracticeAttemptPayload {
  answer_text: string;
}

export interface PracticeFeedback {
  correct_points: string[];
  missing_points: string[];
  improvement_suggestions: string[];
  suggested_structure: string[];
  improved_example_answer: string;
  next_action: string;
  evaluation_status: "completed" | "unavailable";
  evaluation_confidence: "high" | "medium" | "low" | "unavailable";
  improvements_from_previous?: string[];
}

export interface PracticeAttempt {
  id: string;
  question_id: string;
  attempt_number: number;
  answer_text: string;
  assistance_level: AssistanceLevel;
  hints_used: number[];
  reference_revealed: boolean;
  feedback: PracticeFeedback;
  created_at: string;
}

export interface PracticeQuestion {
  id: string;
  session_id: string;
  question_text: string;
  topic: string;
  difficulty: string;
  hints_revealed: number[];
  revealed_hints: Record<string, string>;
  reference_revealed: boolean;
  reference_answer: string | null;
  reference_explanation: string | null;
  attempts: PracticeAttempt[];
  created_at: string;
}

export interface PracticeSessionDetail {
  id: string;
  user_id: number;
  interview_type: InterviewType;
  target_role: string;
  topic: string;
  source_report_id: number | null;
  experience_level: string;
  weakness_context: string | null;
  status: string;
  questions: PracticeQuestion[];
  created_at: string;
  updated_at: string;
}

export interface PracticeSessionSummary {
  id: string;
  interview_type: InterviewType;
  target_role: string;
  topic: string;
  source_report_id: number | null;
  status: string;
  question_count: number;
  attempt_count: number;
  latest_attempt_at: string | null;
  created_at: string;
}

export interface RevealHintResponse {
  question_id: string;
  level: number;
  hint_text: string;
  hints_revealed: number[];
  assistance_level: AssistanceLevel;
}

export interface RevealReferenceResponse {
  question_id: string;
  reference_answer: string;
  reference_explanation: string | null;
  reference_revealed: boolean;
  assistance_level: AssistanceLevel;
}

export interface PracticeRecommendationItem {
  topic: string;
  interview_type: InterviewType;
  target_role: string;
  observed_gap: string;
  suggested_action: string;
  source_report_id: number;
  priority: string;
}
