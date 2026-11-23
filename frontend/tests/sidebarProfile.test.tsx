import { act, create, type ReactTestRenderer } from "react-test-renderer";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import Layout from "../src/components/Layout";

const auth = vi.hoisted(() => ({
  user: { full_name: "Alex", email: "alex@an-example-with-a-long-domain.example", target_role: "" },
}));
vi.mock("../src/hooks/useAuth", () => ({ useAuth: () => ({ user: auth.user, logout: vi.fn() }) }));
vi.mock("../src/components/ThemeToggle", () => ({ default: () => <button aria-label="Toggle theme" /> }));
let tree: ReactTestRenderer | undefined;
beforeEach(() => {
  vi.stubGlobal("window", { matchMedia: () => ({ matches: false, addEventListener: vi.fn(), removeEventListener: vi.fn() }) });
  auth.user.target_role = "";
});
afterEach(() => { act(() => tree?.unmount()); tree = undefined; vi.unstubAllGlobals(); });

it("keeps the complete fallback email available in a title while marking it for single-line truncation", () => {
  act(() => { tree = create(<MemoryRouter><Layout /></MemoryRouter>); });
  const email = tree!.root.findByProps({ className: "profile-email" });
  expect(email.props.title).toBe(auth.user.email);
  expect(email.children).toEqual([auth.user.email]);
});

it("preserves the existing target-role text and wrapping when an email is not displayed", () => {
  auth.user.target_role = "Machine Learning Engineer";
  act(() => { tree = create(<MemoryRouter><Layout /></MemoryRouter>); });
  expect(tree!.root.findAllByProps({ className: "profile-email" })).toHaveLength(0);
  const details = tree!.root.findByProps({ className: "profile-details" });
  expect(details.findByType("span").children).toEqual([auth.user.target_role]);
  expect(details.findByType("span").props.title).toBeUndefined();
});
