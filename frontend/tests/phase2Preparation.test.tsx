import { act, create } from "react-test-renderer";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import Dashboard from "../src/pages/Dashboard";
import InterviewSetup from "../src/features/interview/InterviewSetup";
const mocks = vi.hoisted(() => ({
  user: {
    full_name: "Alex",
    target_role: "Engineer",
    experience_level: "internship",
  },
  logout: vi.fn(),
  analyses: vi.fn(),
  reports: vi.fn(),
  recs: vi.fn(),
}));
vi.mock("../src/hooks/useAuth", () => ({
  useAuth: () => ({ user: mocks.user, logout: mocks.logout }),
}));
vi.mock("../src/services/resume.service", () => ({
  getResumeAnalyses: mocks.analyses,
}));
vi.mock("../src/services/report.service", () => ({
  listInterviewReports: mocks.reports,
}));
vi.mock("../src/services/practice.service", () => ({
  getPracticeRecommendations: mocks.recs,
}));
let root: ReturnType<typeof create> | undefined;
const analysis = {
  id: 1,
  job_role: "Engineer",
  filename: "resume.pdf",
  match_score: 70,
  created_at: "2026-11-14T09:00:00Z",
};
const report = {
  id: 5,
  session_id: "uuid",
  target_role: "Engineer",
  overall_score: 68,
  status: "completed",
  interview_type: "technical",
  interview_date: analysis.created_at,
};
const rec = {
  topic: "SQL",
  interview_type: "technical",
  target_role: "Engineer",
  priority: "high",
  observed_gap: "Explain joins",
  suggested_action: "Compare joins",
  source_report_id: 5,
};
const noop = vi.fn();
beforeEach(() => {
  mocks.analyses.mockReset().mockResolvedValue([analysis]);
  mocks.reports.mockReset().mockResolvedValue([report]);
  mocks.recs.mockReset().mockResolvedValue([rec]);
  noop.mockClear();
});
afterEach(() => {
  act(() => root?.unmount());
  root = undefined;
});
async function render(element: any) {
  await act(async () => {
    root = create(<MemoryRouter>{element}</MemoryRouter>);
  });
  return root!;
}
const text = () => JSON.stringify(root!.toJSON());
const primary = () =>
  root!.root
    .findAllByType("a")
    .find((a) => a.props.className === "btn btn-primary")!;
it("prioritizes a matching actionable gap over report review and unrelated recommendations", async () => {
  mocks.recs.mockResolvedValue([
    { ...rec, topic: "Other goal", target_role: "Designer" },
    { ...rec, topic: "Low priority", priority: "low" },
    rec,
  ]);
  await render(<Dashboard />);
  expect(primary().children).toContain("Practice This Topic");
  expect(primary().props.href).toContain("topic=SQL");
  expect(primary().props.href).toContain("reportId=5");
  expect(text()).not.toContain("View Latest Report");
  expect(text()).not.toContain("Other goal");
});
it("recommends an explicit setup when a resume is ready and there is no targeted gap", async () => {
  mocks.recs.mockResolvedValue([]);
  await render(<Dashboard />);
  expect(primary().props.href).toBe("/interview?analysisId=1");
  expect(primary().children).toContain("Set Up Interview");
});
it("new users receive a meaningful resume action without fabricated scores", async () => {
  mocks.analyses.mockResolvedValue([]);
  mocks.reports.mockResolvedValue([]);
  mocks.recs.mockResolvedValue([]);
  await render(<Dashboard />);
  expect(primary().props.href).toBe("/analyze");
  expect(text()).not.toContain("0 / 100");
  expect(text()).toContain("Your first completed round");
});
it("healthy evidence becomes available while a different panel is still loading", async () => {
  let resolve!: (value: any) => void;
  mocks.recs.mockReturnValue(
    new Promise((done) => {
      resolve = done;
    }),
  );
  await render(<Dashboard />);
  expect(text()).toContain("resume.pdf");
  expect(text()).toContain("68 / 100");
  expect(text()).toContain("Loading practice recommendations");
  await act(async () => resolve([rec]));
  expect(primary().props.href).toContain("topic=SQL");
});
it("setup preselects the requested resume, uses profile calibration and defaults to Text", async () => {
  mocks.analyses.mockResolvedValue([
    analysis,
    { ...analysis, id: 2, filename: "other.pdf" },
  ]);
  const tree = await render(
    <InterviewSetup
      initialAnalysisId={2}
      starting={false}
      onStart={noop}
      onUnauthorized={noop}
    />,
  );
  expect(tree.root.findByProps({ id: "setup-resume" }).props.value).toBe(2);
  expect(tree.root.findByProps({ id: "setup-experience" }).props.value).toBe(
    "internship",
  );
  expect(tree.root.findByProps({ id: "setup-difficulty" }).props.value).toBe(
    "easy",
  );
  expect(
    tree.root.findByProps({ name: "answer-format", value: "text" }).props
      .checked,
  ).toBe(true);
  expect(noop).not.toHaveBeenCalled();
});
it("native selections submit the full existing options only after explicit form submission", async () => {
  const start = vi.fn();
  const tree = await render(
    <InterviewSetup starting={false} onStart={start} onUnauthorized={noop} />,
  );
  act(() => {
    tree.root
      .findByProps({ name: "interview-track", value: "hr" })
      .props.onChange();
    tree.root
      .findByProps({ name: "answer-format", value: "voice" })
      .props.onChange();
    tree.root
      .findByProps({ name: "progression-mode", value: "mock" })
      .props.onChange();
    tree.root
      .findByProps({ name: "question-count", value: 10 })
      .props.onChange();
    tree.root
      .findByProps({ id: "setup-difficulty" })
      .props.onChange({ target: { value: "hard" } });
  });
  expect(start).not.toHaveBeenCalled();
  await act(async () =>
    tree.root.findByType("form").props.onSubmit({ preventDefault() {} }),
  );
  expect(start).toHaveBeenCalledExactlyOnceWith(1, {
    interviewType: "hr",
    inputMode: "voice",
    experienceLevel: "internship",
    startingDifficulty: "hard",
    progressionMode: "mock",
    maxQuestions: 10,
  });
});
it("a deliberately chosen difficulty survives experience changes", async () => {
  const tree = await render(
    <InterviewSetup starting={false} onStart={noop} onUnauthorized={noop} />,
  );
  act(() =>
    tree.root
      .findByProps({ id: "setup-difficulty" })
      .props.onChange({ target: { value: "hard" } }),
  );
  act(() =>
    tree.root
      .findByProps({ id: "setup-experience" })
      .props.onChange({ target: { value: "fresher" } }),
  );
  expect(tree.root.findByProps({ id: "setup-difficulty" }).props.value).toBe(
    "hard",
  );
});
it("a failed resume fetch is retryable without losing configuration", async () => {
  mocks.analyses.mockRejectedValueOnce(new Error("offline"));
  const tree = await render(
    <InterviewSetup starting={false} onStart={noop} onUnauthorized={noop} />,
  );
  act(() =>
    tree.root
      .findByProps({ name: "interview-track", value: "hr" })
      .props.onChange(),
  );
  const retry = tree.root
    .findAllByType("button")
    .find((b) => b.children.includes("Retry"))!;
  await act(async () => retry.props.onClick());
  expect(mocks.analyses).toHaveBeenCalledTimes(2);
  expect(
    tree.root.findByProps({ name: "interview-track", value: "hr" }).props
      .checked,
  ).toBe(true);
  expect(tree.root.findByProps({ id: "setup-resume" }).props.value).toBe(1);
});
