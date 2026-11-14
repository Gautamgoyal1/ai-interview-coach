import { act, create } from "react-test-renderer";
import { MemoryRouter } from "react-router-dom";
import { afterEach, expect, it, vi } from "vitest";
import { practiceLink } from "../src/utils/practiceNavigation";
import TopicScores from "../src/features/reports/TopicScores";
import PracticePlan from "../src/features/reports/PracticePlan";
import MissedPoints from "../src/features/reports/MissedPoints";
import ResumeReport from "../src/features/resume/ResumeReport";
import Dashboard from "../src/pages/Dashboard";
const mocks = vi.hoisted(() => ({ logout:vi.fn(), analyses: vi.fn(), reports: vi.fn(), recommendations: vi.fn() }));
vi.mock("../src/hooks/useAuth", () => ({ useAuth: () => ({user:{full_name:"Alex"},logout:mocks.logout}) }));
vi.mock("../src/services/resume.service", () => ({getResumeAnalyses:mocks.analyses}));
vi.mock("../src/services/report.service", () => ({listInterviewReports:mocks.reports}));
vi.mock("../src/services/practice.service", () => ({getPracticeRecommendations:mocks.recommendations}));
let root: ReturnType<typeof create> | undefined;
afterEach(() => { act(() => root?.unmount()); root=undefined; vi.clearAllMocks(); });
const origin={interviewType:"hr" as const,reportId:7,reportSessionId:"session-uuid",targetRole:"Product Manager"};
function render(element: any) { act(() => { root=create(<MemoryRouter>{element}</MemoryRouter>); }); return root!; }
it("encodes full report context without substituting the numeric report ID for session ID", () => {
 const params=new URL(practiceLink("Conflict & resolution",origin,"Trade-offs"),"http://test").searchParams;
 expect(Object.fromEntries(params)).toEqual({topic:"Conflict & resolution",type:"hr",reportId:"7",reportSessionId:"session-uuid",role:"Product Manager",gap:"Trade-offs"});
});
it("all report practice entry points preserve HR and report provenance", () => {
 const tree=render(<><TopicScores topics={[{topic:"Teamwork",score:74,questions_asked:1,evaluated_questions:1}]} origin={origin}/><PracticePlan recommendations={[{area:"Teamwork",priority:"high",observed_gap:"Conflict",action:"Retry"}]} origin={origin}/><MissedPoints strengths={[]} weaknesses={["Teamwork: conflict"]} missingConcepts={["Reflection"]} origin={origin}/></>);
 const text=JSON.stringify(tree.toJSON());expect(text).toContain("Behavioral Topic Performance");expect(text).toContain("74.0%");expect(text).toContain("Checkmarks are temporary");
 for(const link of tree.root.findAllByType("a")){
   const query=new URL(link.props.href,"http://test").searchParams;
   expect(query.get("type")).toBe("hr");expect(query.get("reportId")).toBe("7");expect(query.get("reportSessionId")).toBe("session-uuid");
 }
});
it("missing evidence metadata never promotes a matched skill to demonstrated", () => {
 const tree=render(<ResumeReport result={{job_role:"Engineer",match_score:70,resume_skills:["Python"],matched_skills:["Python"],missing_skills:[],strengths:[],improvement_suggestions:[],likely_interview_questions:[]}}/>);
 expect(JSON.stringify(tree.toJSON())).toContain("Demonstrated (0)");
 const skill=tree.root.findAllByType("button").find(b=>b.props.className?.includes("skill-chip-unknown"))!;
 act(()=>skill.props.onClick());
 expect(JSON.stringify(tree.toJSON())).toContain("A skill match alone does not establish practical experience.");
});
it("one dashboard failure preserves other panels and does not turn unavailable history into zero", async () => {
 mocks.analyses.mockRejectedValue(new Error("offline"));mocks.recommendations.mockResolvedValue([]);
 mocks.reports.mockResolvedValue([{id:7,session_id:"uuid",target_role:"Engineer",interview_date:"2026-11-14T09:30:00Z",status:"completed",overall_score:72}]);
 await act(async()=>{root=create(<MemoryRouter><Dashboard/></MemoryRouter>);});
 const text=JSON.stringify(root!.toJSON());expect(text).toContain("72 / 100");expect(text).toContain("Resume history unavailable.");expect(text).toContain("Recent Reports");expect(text).not.toContain("No resume analyses yet.");
 mocks.analyses.mockResolvedValue([]);
 const retry=root!.root.findAllByType("button").find(b=>b.children.includes("Retry"))!;
 await act(async()=>retry.props.onClick());
 expect(mocks.analyses).toHaveBeenCalledTimes(2);expect(JSON.stringify(root!.toJSON())).toContain("No resume analyses yet.");
});
it("all failed dashboard requests show unavailable guidance instead of first-use guidance", async () => {
 mocks.analyses.mockRejectedValue(new Error("offline"));mocks.reports.mockRejectedValue(new Error("offline"));mocks.recommendations.mockRejectedValue(new Error("offline"));
 await act(async()=>{root=create(<MemoryRouter><Dashboard/></MemoryRouter>);});
 const text=JSON.stringify(root!.toJSON());expect(text).toContain("Your workspace is temporarily incomplete");expect(text).not.toContain("Analyze your resume to begin");
});
