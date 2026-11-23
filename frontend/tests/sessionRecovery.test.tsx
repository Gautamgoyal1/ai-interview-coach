import { act, create, type ReactTestRenderer } from "react-test-renderer";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { AuthProvider } from "../src/hooks/AuthContext";
import ProtectedRoute from "../src/components/ProtectedRoute";
import { ApiError } from "../src/services/api";

const mocks = vi.hoisted(() => ({ current: vi.fn(), logout: vi.fn(), token: vi.fn() }));
vi.mock("../src/services/auth.service", () => ({ getCurrentUser: mocks.current, logout: mocks.logout }));
vi.mock("../src/utils/storage", () => ({ getAccessToken: mocks.token }));
let tree: ReactTestRenderer | undefined;
beforeEach(() => { vi.clearAllMocks(); mocks.token.mockReturnValue("synthetic-saved-token"); });
afterEach(() => { act(() => tree?.unmount()); tree = undefined; vi.unstubAllGlobals(); });
async function mount() {
  await act(async () => { tree = create(<AuthProvider><MemoryRouter initialEntries={["/dashboard"]}><Routes>
    <Route element={<ProtectedRoute />}><Route path="/dashboard" element={<p>Saved workspace</p>} /></Route>
    <Route path="/login" element={<p>Sign in</p>} />
  </Routes></MemoryRouter></AuthProvider>); });
}

it.each([new ApiError("Service waking up", 503), new TypeError("Network interrupted")])("preserves a valid stored token during recoverable startup failures (%s)", async error => {
  mocks.current.mockRejectedValue(error); const reload = vi.fn();
  vi.stubGlobal("window", { location: { reload } });
  await mount();
  expect(mocks.logout).not.toHaveBeenCalled();
  expect(tree!.root.findAllByProps({ role: "alert" })).toHaveLength(1);
  expect(JSON.stringify(tree!.toJSON())).not.toContain("Saved workspace");
  const button = tree!.root.findByType("button");
  expect(button.children.join("")).toBe("Retry session");
  act(() => button.props.onClick()); expect(reload).toHaveBeenCalledTimes(1);
});

it("clears genuinely expired credentials and returns to sign in", async () => {
  mocks.current.mockRejectedValue(new ApiError("Expired", 401));
  await mount(); expect(mocks.logout).toHaveBeenCalledTimes(1);
  expect(JSON.stringify(tree!.toJSON())).toContain("Sign in");
});

it("opens the saved workspace after successful session restoration", async () => {
  mocks.current.mockResolvedValue({ id: 1, email: "synthetic@example.com" });
  await mount(); expect(JSON.stringify(tree!.toJSON())).toContain("Saved workspace");
  expect(mocks.logout).not.toHaveBeenCalled();
});

it("never sends an anonymous restoration request", async () => {
  mocks.token.mockReturnValue(null); await mount();
  expect(mocks.current).not.toHaveBeenCalled();
  expect(JSON.stringify(tree!.toJSON())).toContain("Sign in");
});
