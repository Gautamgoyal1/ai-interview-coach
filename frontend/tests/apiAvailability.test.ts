import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { apiRequest, ApiError } from "../src/services/api";

vi.mock("../src/utils/storage", () => ({ getAccessToken: () => "synthetic-access-token" }));
const fetcher = vi.fn();
beforeEach(() => { fetcher.mockReset(); vi.stubGlobal("fetch", fetcher); });
afterEach(() => { vi.unstubAllGlobals(); });

it("preserves bearer auth, JSON bodies and successful API responses", async () => {
  fetcher.mockResolvedValue(Response.json({ id: 12 }));
  await expect(apiRequest("/auth/register", { method: "POST", body: JSON.stringify({ name: "Candidate" }) })).resolves.toEqual({ id: 12 });
  const request = fetcher.mock.calls[0][1];
  expect(request.headers.get("Authorization")).toBe("Bearer synthetic-access-token");
  expect(request.headers.get("Content-Type")).toBe("application/json");
  expect(fetcher).toHaveBeenCalledTimes(1);
});

it("leaves multipart boundaries and caller authorization unchanged", async () => {
  fetcher.mockResolvedValue(Response.json({ ok: true }));
  const body = new FormData(); body.append("file", new Blob(["synthetic-pdf"]), "resume.pdf");
  await apiRequest("/resume/analyze", { method: "POST", body, headers: { Authorization: "Bearer explicit-token" } });
  expect(fetcher.mock.calls[0][1].headers.has("Content-Type")).toBe(false);
  expect(fetcher.mock.calls[0][1].headers.get("Authorization")).toBe("Bearer explicit-token");
});

it.each([200, 502, 503, 504])("explains a host loading/error page (%i) without replaying submissions", async status => {
  fetcher.mockResolvedValue(new Response("<html>provider internal loading page</html>", { status }));
  const failure = await apiRequest("/interview/session/answer", { method: "POST", body: "{}" }).catch(error => error);
  expect(failure).toBeInstanceOf(ApiError);
  expect(failure.message).toContain("server may be starting");
  expect(failure.message).toContain("check your interview before resubmitting");
  expect(failure.message).not.toMatch(/<html>|Unexpected token|provider internal/);
  expect(fetcher).toHaveBeenCalledTimes(1);
});

it("preserves meaningful JSON failures, including authentication and AI kill switches", async () => {
  for (const [status, detail] of [[401, "Invalid credentials"], [503, "AI requests are temporarily disabled."], [429, "Daily usage limit reached"]] as const) {
    fetcher.mockResolvedValueOnce(Response.json({ detail }, { status }));
    await expect(apiRequest("/auth/me")).rejects.toMatchObject({ status, message: detail });
  }
  expect(fetcher).toHaveBeenCalledTimes(3);
});

it("returns an actionable network failure without automatic polling or retries", async () => {
  fetcher.mockRejectedValue(new TypeError("Failed to fetch"));
  await expect(apiRequest("/auth/me")).rejects.toMatchObject({ status: 0, message: expect.stringContaining("wait about a minute") });
  expect(fetcher).toHaveBeenCalledTimes(1);
});

it("preserves cancellation so voice and navigation cancellation stay silent", async () => {
  const controller = new AbortController(); controller.abort();
  const error = new DOMException("Cancelled", "AbortError");
  fetcher.mockRejectedValue(error);
  await expect(apiRequest("/speech/token", { method: "POST", signal: controller.signal })).rejects.toBe(error);
  expect(fetcher.mock.calls[0][1].signal).toBe(controller.signal);
  expect(fetcher).toHaveBeenCalledTimes(1);
});

it("preserves cancellation while reading the response body", async () => {
  const controller = new AbortController();
  const error = new DOMException("Cancelled while reading", "AbortError");
  fetcher.mockResolvedValue({ ok: true, json: async () => { controller.abort(); throw error; } });
  await expect(apiRequest("/speech/token", { method: "POST", signal: controller.signal })).rejects.toBe(error);
  expect(fetcher).toHaveBeenCalledTimes(1);
});
