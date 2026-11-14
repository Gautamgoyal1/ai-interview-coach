import { act, create } from "react-test-renderer";
import { expect, it, vi } from "vitest";
import { useInterview } from "../src/features/interview/useInterview";
const service = vi.hoisted(() => ({ submit: vi.fn() }));
vi.mock("../src/services/interview.service", () => ({
  startInterview: vi.fn(), getInterviewSession: vi.fn(), endInterviewSession: vi.fn(),
  submitInterviewAnswer: service.submit,
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
