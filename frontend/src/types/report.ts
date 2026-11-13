export interface DimensionSummary {
  dimension: string;
  label: string;
  weight: number;
  average_score: number | null;
  percentage: number | null;
  evaluated_count: number;
}

export interface TopicPerformance {
  topic: string;
  score: number | null;
  questions_asked: number;
  evaluated_questions: number;
}

export interface RecommendationItem {
  area: string;
  observed_gap: string;
  action: string;
  priority: "high" | "medium" | "low";
}

export interface QuestionFeedbackItem {
  question_id: string;
  question_index: number;
  is_follow_up: boolean;
  parent_question_id: string | null;
  topic: string;
  difficulty: string;
  question_text: string;
  answer_text: string | null;
  overall_score: number | null;
  grading_status: string;
  dimension_scores: Record<string, { score: number; explanation: string }>;
  strengths: string[];
  missing_concepts: string[];
  improvement_suggestions: string[];
}

export interface CompletionStats {
  questions_answered: number;
  primary_questions_completed: number;
  follow_ups_answered: number;
  total_primary_questions: number;
}

export interface EvaluationCoverage {
  evaluated_count: number;
  unavailable_count: number;
  total_answered: number;
  coverage_ratio: number;
  is_partial: boolean;
}

export interface InterviewReport {
  id: number;
  session_id: string;
  target_role: string;
  interview_type?: "technical" | "hr";
  interview_date: string;
  status: "pending" | "processing" | "completed" | "partial" | "failed";
  overall_score: number | null;
  dimension_scores: Record<string, DimensionSummary>;
  topic_scores: TopicPerformance[];
  strengths: string[];
  weaknesses: string[];
  missing_concepts: string[];
  recommendations: RecommendationItem[];
  question_feedback: QuestionFeedbackItem[];
  completion_stats: CompletionStats;
  evaluation_coverage: EvaluationCoverage;
  rubric_version: string;
  rubric_weights: Record<string, number>;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface InterviewReportSummary {
  id: number;
  session_id: string;
  target_role: string;
  interview_type?: "technical" | "hr";
  interview_date: string;
  status: string;
  overall_score: number | null;
  rubric_version: string;
  created_at: string;
}
