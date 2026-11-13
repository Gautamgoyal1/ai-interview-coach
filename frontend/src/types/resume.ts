export interface ResumeAnalysisResult {
  analysis_id?: number | null;
  reused?: boolean;
  version?: number;
  status?: string;
  job_role: string;
  resume_skills: string[];
  matched_skills: string[];
  missing_skills: string[];
  match_score: number;
  skill_evidence?: Record<string, string>;
  strengths: string[];
  improvement_suggestions: string[];
  likely_interview_questions: string[];
}

export interface ResumeAnalysisHistoryItem {
  id: number;
  filename: string;
  job_role: string;
  created_at: string;
  match_score: number;
  version?: number;
  interview_count?: number;
}

export interface SavedResumeAnalysis {
  id: number;
  filename: string;
  created_at: string;
  version?: number;
  interview_count?: number;
  skill_evidence?: Record<string, string>;
  result: ResumeAnalysisResult;
}

export interface DeleteAnalysisResponse {
  deleted: boolean;
  analysis_id: number;
  mode: "archived" | "permanent";
  dependent_interviews: number;
}
