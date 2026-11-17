import { act, create } from "react-test-renderer";
import { expect, it, vi } from "vitest";
import { useInterview } from "../src/features/interview/useInterview";
import { ApiError } from "../src/services/api";
const service = vi.hoisted(() => ({ submit: vi.fn(), get: vi.fn(), retry: vi.fn() }));
vi.mock("../src/services/interview.service", () => ({
  startInterview: vi.fn(), getInterviewSession: service.get, endInterviewSession: vi.fn(),
  submitInterviewAnswer: service.submit,
  retryInterviewQuestion: service.retry,
}));
it("submits the final edited answer exactly once despite rapid repeated submits", async () => {
  let api!: ReturnType<typeof useInterview>;
  function Harness() { api = useInterview(); return null; }
  let resolve!: (value: any) => void;
  service.submit.mockReset().mockReturnValue(new Promise(done => { resolve = done; }));
  let root!: ReturnType<typeof create>;
  act(() => { root = create(<Harness />); });
  let first!: ReturnType<typeof api.submitAnswer>;
  let second!: ReturnType<typeof api.submitAnswer>;
  act(() => {
    first = api.submitAnswer("session", "question", "  edited final transcript  ");
    second = api.submitAnswer("session", "question", "edited final transcript");
  });
  expect(service.submit).toHaveBeenCalledTimes(1);
  expect(service.submit).toHaveBeenCalledWith("session", "question", "edited final transcript");
  await expect(second).resolves.toBeNull();
  await act(async () => { resolve({ session_id: "session", status: "in_progress" }); await first; });
  expect(api.submitting).toBe(false);
  act(() => root.unmount());
});

it("refreshes a saved-answer recovery state after generation fails, then retries only generation once", async () => {
  let api!: ReturnType<typeof useInterview>;
  function Harness() { api = useInterview(); return null; }
  const pending = { session_id: "session", status: "in_progress", generation_unavailable: true, current_question: null };
  service.submit.mockReset().mockRejectedValue(new ApiError("Your answer was saved.", 503));
  service.get.mockReset().mockResolvedValue(pending);
  let finish!: (value: any) => void;
  service.retry.mockReset().mockReturnValue(new Promise(done => { finish = done; }));
  let root!: ReturnType<typeof create>;
  act(() => { root = create(<Harness />); });
  await act(async () => { await api.submitAnswer("session", "q1", "final answer"); });
  expect(api.session?.generation_unavailable).toBe(true);
  expect(service.get).toHaveBeenCalledWith("session");
  let first!: ReturnType<typeof api.retryQuestion>;
  let duplicate!: ReturnType<typeof api.retryQuestion>;
  act(() => { first = api.retryQuestion("session"); duplicate = api.retryQuestion("session"); });
  expect(service.retry).toHaveBeenCalledTimes(1);
  expect(service.submit).toHaveBeenCalledTimes(1);
  await expect(duplicate).resolves.toBeNull();
  await act(async () => { finish({ ...pending, generation_unavailable: false, current_question: { question_id: "q2" } }); await first; });
  expect(api.session?.current_question?.question_id).toBe("q2");
  expect(api.submitting).toBe(false);
  act(() => root.unmount());
});

it("retains the pending session when a generation retry is unavailable", async () => {
  let api!: ReturnType<typeof useInterview>;
  function Harness() { api = useInterview(); return null; }
  service.get.mockReset().mockResolvedValue({ session_id: "session", generation_unavailable: true, current_question: null });
  service.retry.mockReset().mockRejectedValue(new ApiError("Saved answer is safe.", 503));
  let root!: ReturnType<typeof create>;
  act(() => { root = create(<Harness />); });
  await act(async () => { await api.loadSession("session"); });
  await act(async () => { await api.retryQuestion("session"); });
  expect(api.session?.generation_unavailable).toBe(true);
  expect(api.error).toBe("Saved answer is safe.");
  expect(api.submitting).toBe(false);
  act(() => root.unmount());
});
