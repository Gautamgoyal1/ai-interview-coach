export interface PracticeOrigin {
  interviewType?: "technical" | "hr";
  reportId?: number;
  reportSessionId?: string;
  targetRole?: string;
}

export function practiceLink(topic: string, origin: PracticeOrigin = {}, gap?: string): string {
  const params = new URLSearchParams({ topic, type: origin.interviewType || "technical" });
  if (origin.reportId) params.set("reportId", String(origin.reportId));
  if (origin.reportSessionId) params.set("reportSessionId", origin.reportSessionId);
  if (origin.targetRole) params.set("role", origin.targetRole);
  if (gap) params.set("gap", gap);
  return `/practice?${params}`;
}
