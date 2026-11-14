import { act, create, type ReactTestRenderer } from "react-test-renderer";
import {
  MemoryRouter,
  Route,
  Routes,
  useLocation,
  useNavigate,
} from "react-router-dom";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import PracticeWorkspace from "../src/pages/PracticeWorkspace";
import PracticeCoaching from "../src/features/practice/PracticeCoaching";
import AnswerBox from "../src/features/interview/AnswerBox";
import ProgressBar from "../src/features/interview/ProgressBar";
import { useUnsentAnswerWarning } from "../src/hooks/useUnsentAnswerWarning";
const mocks = vi.hoisted(() => ({
  get: vi.fn(),
  hint: vi.fn(),
  reference: vi.fn(),
  submit: vi.fn(),
  next: vi.fn(),
  reports: vi.fn(),
}));
vi.mock("../src/hooks/useAuth", () => ({
  useAuth: () => ({ logout: vi.fn() }),
}));
vi.mock("../src/services/report.service", () => ({
  listInterviewReports: mocks.reports,
}));
vi.mock("../src/services/practice.service", () => ({
  getPracticeSession: mocks.get,
  revealHint: mocks.hint,
  revealReference: mocks.reference,
  submitPracticeAttempt: mocks.submit,
  generateNextQuestion: mocks.next,
  listPracticeSessions: vi.fn(),
  getPracticeRecommendations: vi.fn(),
  createPracticeSession: vi.fn(),
  deletePracticeSession: vi.fn(),
}));
const feedback = {
  correct_points: ["Clear context"],
  missing_points: ["Quantify the result"],
  improvement_suggestions: ["Use a concrete result"],
  suggested_structure: ["Context", "Action", "Result"],
  improved_example_answer: "An example",
  next_action: "Add a measurable result",
  evaluation_status: "completed" as const,
  evaluation_confidence: "high" as const,
  improvements_from_previous: [],
};
const attempt = {
  id: "a1",
  question_id: "q1",
  attempt_number: 1,
  answer_text: "My previous answer",
  assistance_level: "hint_assisted" as const,
  hints_used: [1],
  reference_revealed: false,
  feedback,
  created_at: "2026-11-14",
};
let tree: ReactTestRenderer | undefined;
let listeners: Record<string, any>;
let confirm: ReturnType<typeof vi.fn>;
let session: any;
beforeEach(() => {
  listeners = {};
  confirm = vi.fn(() => false);
  vi.stubGlobal("window", {
    confirm,
    history: { state: { idx: 2 }, go: vi.fn() },
    addEventListener: vi.fn((name, fn) => {
      listeners[name] = fn;
    }),
    removeEventListener: vi.fn(),
  });
  vi.stubGlobal("document", {
    getElementById: vi.fn(() => ({ focus: vi.fn() })),
  });
  session = {
    id: "s1",
    topic: "Conflict resolution",
    interview_type: "hr",
    target_role: "Product Manager",
    source_report_id: 7,
    questions: [
      {
        id: "q1",
        question_text: "How did you resolve a disagreement?",
        difficulty: "medium",
        hints_revealed: [],
        revealed_hints: {},
        reference_revealed: false,
        attempts: [],
      },
    ],
  };
  mocks.get.mockImplementation(async () => structuredClone(session));
  mocks.reports.mockResolvedValue([{ id: 7, session_id: "origin-session" }]);
});
afterEach(() => {
  act(() => tree?.unmount());
  tree = undefined;
  vi.clearAllMocks();
  vi.unstubAllGlobals();
});
async function mountPractice() {
  await act(async () => {
    tree = create(
      <MemoryRouter
        initialEntries={[
          "/practice/s1?reportId=7&reportSessionId=origin-session",
        ]}
      >
        <Routes>
          <Route path="/practice/:sessionId" element={<PracticeWorkspace />} />
        </Routes>
      </MemoryRouter>,
    );
  });
}
function button(text: string) {
  return tree!.root
    .findAllByType("button")
    .find((b) => JSON.stringify(b.children).includes(text))!;
}
function text() {
  return JSON.stringify(tree!.toJSON());
}
it("warns on router navigation, cancels without losing the answer, and permits confirmed departure", async () => {
  function Harness() {
    const nav = useNavigate();
    const loc = useLocation();
    useUnsentAnswerWarning(true);
    return <button onClick={() => nav("/dashboard")}>{loc.pathname}</button>;
  }
  act(() => {
    tree = create(
      <MemoryRouter initialEntries={["/interview/s1"]}>
        <Harness />
      </MemoryRouter>,
    );
  });
  act(() => tree!.root.findByType("button").props.onClick());
  expect(text()).toContain("/interview/s1");
  expect(confirm).toHaveBeenCalledTimes(1);
  confirm.mockReturnValue(true);
  act(() => tree!.root.findByType("button").props.onClick());
  expect(text()).toContain("/dashboard");
});
it("guards refresh and cancelled browser Back without adding history entries", () => {
  function Harness() {
    useUnsentAnswerWarning(true);
    return null;
  }
  act(() => {
    tree = create(
      <MemoryRouter>
        <Harness />
      </MemoryRouter>,
    );
  });
  const refresh = { preventDefault: vi.fn(), returnValue: undefined };
  listeners.beforeunload(refresh);
  expect(refresh.preventDefault).toHaveBeenCalled();
  expect(refresh.returnValue).toBe("");
  const pop = { state: { idx: 1 }, stopImmediatePropagation: vi.fn() };
  listeners.popstate(pop);
  expect(pop.stopImmediatePropagation).toHaveBeenCalled();
  expect(window.history.go).toHaveBeenCalledWith(1);
  const restored = { state: { idx: 2 }, stopImmediatePropagation: vi.fn() };
  listeners.popstate(restored);
  expect(restored.stopImmediatePropagation).toHaveBeenCalled();
  expect(confirm).toHaveBeenCalledTimes(1);
});
it("displays all voice states and keeps recording/finalization read-only with separate submission", () => {
  const submit = vi.fn();
  const stop = vi.fn();
  for (const state of [
    "starting",
    "listening",
    "stopping",
    "review",
    "ai_speaking",
    "submitting",
  ] as const) {
    act(() => {
      tree = create(
        <AnswerBox
          questionId="q"
          answer="Final words"
          onChange={vi.fn()}
          onSubmit={submit}
          submitting={state === "submitting"}
          disabled={false}
          inputMode="voice"
          voiceState={state}
          onStopRecording={stop}
        />,
      );
    });
    if (["starting", "listening", "stopping", "submitting"].includes(state))
      expect(tree!.root.findByType("textarea").props.disabled).toBe(true);
    if (state === "review")
      expect(tree!.root.findByType("textarea").props.disabled).toBe(false);
    expect(submit).not.toHaveBeenCalled();
    act(() => tree!.unmount());
    tree = undefined;
  }
});
it("does not claim completion while the final primary question is unanswered", () => {
  act(() => {
    tree = create(
      <ProgressBar
        questionIndex={8}
        maxQuestions={8}
        isFollowUp={false}
        answeredCount={9}
      />,
    );
  });
  const bar = tree!.root.findByProps({ role: "progressbar" });
  expect(bar.props["aria-valuenow"]).toBe(7);
  expect(bar.props.title).toContain("9 responses submitted");
  expect(bar.props.title).not.toContain("complete");
});
it("reveals hints progressively and preserves HR/report context without submitting", async () => {
  mocks.hint.mockImplementation(async (_id, level) => ({
    hints_revealed: level === 1 ? [1] : [1, 2],
    hint_text: "Consider the outcome",
  }));
  await mountPractice();
  await act(async () => button("Get Hint 1").props.onClick());
  expect(mocks.hint).toHaveBeenLastCalledWith("q1", 1);
  expect(text()).toContain("Hint-assisted");
  await act(async () => button("Get Hint 2").props.onClick());
  expect(mocks.hint).toHaveBeenLastCalledWith("q1", 2);
  expect(mocks.submit).not.toHaveBeenCalled();
  expect(
    tree!.root
      .findAllByType("a")
      .find((a) => a.props.href.includes("/reports/"))?.props.href,
  ).toBe("/reports/origin-session");
});
it("serializes coaching submissions, retains failed edits, and retries using the same question", async () => {
  let reject!: (e: Error) => void;
  mocks.submit.mockReturnValueOnce(
    new Promise((_ok, fail) => {
      reject = fail;
    }),
  );
  await mountPractice();
  act(() =>
    tree!.root
      .findByType("textarea")
      .props.onChange({ target: { value: "Unsent example" } }),
  );
  const event = { preventDefault() {} };
  await act(async () => {
    tree!.root.findByType("form").props.onSubmit(event);
    tree!.root.findByType("form").props.onSubmit(event);
  });
  expect(mocks.submit).toHaveBeenCalledTimes(1);
  await act(async () => reject(new Error("Temporary network failure")));
  expect(tree!.root.findByType("textarea").props.value).toBe("Unsent example");
  expect(text()).toContain("Use the same action to retry");
  mocks.submit.mockResolvedValue({ ...attempt, answer_text: "Unsent example" });
  await act(async () => tree!.root.findByType("form").props.onSubmit(event));
  expect(mocks.submit).toHaveBeenLastCalledWith("q1", {
    answer_text: "Unsent example",
  });
  expect(text()).toContain("Add a measurable result");
});
it("makes revision primary, discloses AI examples, and compares actual saved attempts", () => {
  act(() => {
    tree = create(
      <PracticeCoaching
        attempt={{
          ...attempt,
          attempt_number: 2,
          answer_text: "An improved answer",
        }}
        previous={attempt}
        onImprove={vi.fn()}
        onNext={vi.fn()}
        busy={false}
        generating={false}
      />,
    );
  });
  const primary = tree!.root
    .findAllByType("button")
    .filter((b) => b.props.className.includes("btn-primary"));
  expect(primary).toHaveLength(1);
  expect(primary[0].children).toContain("Improve my answer");
  expect(text()).toContain("not an authoritative benchmark");
  expect(text()).toContain("My previous answer");
  expect(text()).toContain("An improved answer");
});
it("shows unavailable coaching explicitly without inventing positive coverage", () => {
  act(() => {
    tree = create(
      <PracticeCoaching
        attempt={{
          ...attempt,
          feedback: { ...feedback, evaluation_status: "unavailable" },
        }}
        onImprove={vi.fn()}
        onNext={vi.fn()}
        busy={false}
        generating={false}
      />,
    );
  });
  expect(text()).toContain("Coaching is unavailable");
  expect(text()).not.toContain("Clear context");
  expect(text()).not.toContain("Quantify the result");
});
