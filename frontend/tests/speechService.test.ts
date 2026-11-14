import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { getSpeechToken, invalidateSpeechToken, synthesizeSpeechAudio } from "../src/services/speech.service";
const mocks = vi.hoisted(() => ({ request: vi.fn(), access: vi.fn() }));
vi.mock("../src/services/api", () => ({
  apiRequest: mocks.request,
  ApiError: class extends Error { constructor(message: string, public status: number) { super(message); } },
}));
vi.mock("../src/utils/storage", () => ({ getAccessToken: mocks.access }));
beforeEach(() => {
  vi.useFakeTimers(); invalidateSpeechToken(); mocks.access.mockReset().mockReturnValue("user-one");
  mocks.request.mockReset().mockResolvedValue({ token: "speech-token", region: "eastasia", expires_in: 600 });
});
afterEach(() => { vi.useRealTimers(); vi.unstubAllGlobals(); });
it("returns remaining token lifetime and renews before expiry", async () => {
  await getSpeechToken();
  vi.advanceTimersByTime(120000);
  expect((await getSpeechToken()).expires_in).toBe(480);
  expect(mocks.request).toHaveBeenCalledTimes(1);
  vi.advanceTimersByTime(420000);
  expect((await getSpeechToken()).expires_in).toBe(600);
  expect(mocks.request).toHaveBeenCalledTimes(2);
});
it("does not reuse authorization after a user change", async () => {
  await getSpeechToken(); mocks.access.mockReturnValue("user-two"); await getSpeechToken();
  expect(mocks.request).toHaveBeenCalledTimes(2);
});
it("does not cache an aborted token response", async () => {
  const abort = new AbortController(); abort.abort();
  await expect(getSpeechToken(abort.signal)).rejects.toThrow("authorization changed");
  await getSpeechToken(); expect(mocks.request).toHaveBeenCalledTimes(2);
});
it("passes request cancellation and no-store through TTS fetch", async () => {
  const fetcher = vi.fn().mockResolvedValue(new Response(new Blob(["audio"]), { status: 200 }));
  vi.stubGlobal("fetch", fetcher);
  const abort = new AbortController();
  await synthesizeSpeechAudio("Question?", undefined, "hr", abort.signal);
  expect(fetcher.mock.calls[0][1]).toMatchObject({ signal: abort.signal, cache: "no-store" });
  expect(JSON.parse(fetcher.mock.calls[0][1].body).interview_type).toBe("hr");
});
