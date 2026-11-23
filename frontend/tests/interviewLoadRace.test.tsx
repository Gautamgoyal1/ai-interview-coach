import { act, create, type ReactTestRenderer } from "react-test-renderer";
import { afterEach, expect, it, vi } from "vitest";
import { useInterview } from "../src/features/interview/useInterview";

const requests = vi.hoisted(() => ({ get: vi.fn() }));
vi.mock("../src/services/interview.service", () => ({ getInterviewSession: requests.get }));
let tree: ReactTestRenderer | undefined;
let state: ReturnType<typeof useInterview>;
function Harness() { state = useInterview(); return null; }
afterEach(() => { act(() => tree?.unmount()); tree = undefined; vi.clearAllMocks(); });
it.each([false, true])("ignores an old interview response after navigating to a newer session (failure=%s)", async fail => {
  let resolve!: (value: any) => void, reject!: (reason: unknown) => void;
  requests.get.mockReturnValueOnce(new Promise((yes, no) => { resolve = yes; reject = no; }))
    .mockResolvedValueOnce({ session_id: "new-session", current_question: { question_id: "new-question" } });
  act(() => { tree = create(<Harness />); });
  let old!: Promise<unknown>;
  act(() => { old = state.loadSession("old-session"); });
  await act(async () => { await state.loadSession("new-session"); });
  await act(async () => { if (fail) reject(new Error("Late old failure")); else resolve({ session_id: "old-session" }); await old; });
  expect(state.session?.session_id).toBe("new-session");
  expect(state.error).toBeNull(); expect(state.loading).toBe(false);
});
