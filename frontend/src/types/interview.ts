export type ExperienceLevel =
  | "internship"
  | "fresher"
  | "intermediate"
  | "experienced";

export type InterviewType = "technical" | "hr";

export type StartingDifficulty = "easy" | "medium" | "hard";

export type ProgressionMode = "adaptive" | "mock";

export interface InterviewQuestion {
  question_id: string;
  topic: string;
  difficulty: string;
  question_text: string;
  question_type: string;
  is_follow_up: boolean;
}

export interface ConversationTurn {
  question_id: string;
  question_index: number;
  is_follow_up: boolean;
  topic: string;
  difficulty: string;
  question_type: string;
  question_text: string;
  answer_text: string | null;
  created_at: string;
  answered_at: string | null;
}

export interface InterviewSession {
  session_id: string;
  analysis_id: number;
  target_role: string;
  interview_type?: InterviewType;
  experience_level?: ExperienceLevel;
  starting_difficulty?: StartingDifficulty;
  progression_mode?: ProgressionMode;
  status: "in_progress" | "completed";
  question_index: number;
  max_questions: number;
  follow_up_count: number;
  max_follow_ups: number;
  current_question: InterviewQuestion | null;
  conversation_history: ConversationTurn[];
  started_at: string;
  completed_at: string | null;
}
