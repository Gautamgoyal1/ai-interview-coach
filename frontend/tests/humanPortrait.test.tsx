import { act, create, type ReactTestRenderer } from "react-test-renderer";
import { readFileSync } from "node:fs";
import { afterEach, expect, it, vi } from "vitest";
import HumanPortrait from "../src/features/interview/HumanPortrait";

let tree: ReactTestRenderer | undefined;
afterEach(() => { act(() => tree?.unmount()); tree = undefined; vi.useRealTimers(); });

it.each(["interviewer", "candidate"] as const)("uses only the original neutral %s portrait without expression overlays", role => {
  vi.useFakeTimers();
  act(() => { tree = create(<HumanPortrait role={role} />); });
  expect(tree!.root.findByType("img").props.src).toBe(`/avatars/${role}-neutral.webp`);
  expect(tree!.root.findAllByType("img")).toHaveLength(1);
  expect(tree!.root.findAllByType("svg")).toHaveLength(0);
  expect(tree!.root.findAllByProps({ "data-mouth": "closed", "data-renderer": "static" })).toHaveLength(1);
  act(() => vi.advanceTimersByTime(60000));
  expect(vi.getTimerCount()).toBe(0);
  expect(tree!.root.findByType("img").props.src).toBe(`/avatars/${role}-neutral.webp`);
});

it("keeps the same image mounted across parent renders rather than alternating photographs", () => {
  act(() => { tree = create(<HumanPortrait role="interviewer" />); });
  const image = tree!.root.findByType("img");
  for (let i = 0; i < 30; i++) act(() => tree!.update(<HumanPortrait role="interviewer" />));
  expect(tree!.root.findByType("img")).toBe(image);
  expect(image.props.alt).toBe("");
  expect(tree!.root.findByProps({ className: "iv-human-portrait" }).props["aria-hidden"]).toBe("true");
});

it("falls back without retry loops on image failure and keeps the other identity usable", () => {
  vi.useFakeTimers();
  act(() => { tree = create(<HumanPortrait role="interviewer" />); });
  act(() => tree!.root.findByType("img").props.onError());
  expect(tree!.root.findAllByType("img")).toHaveLength(0);
  expect(tree!.root.findByProps({ className: "iv-human-fallback" }).children).toContain("AI interviewer");
  act(() => tree!.update(<HumanPortrait role="candidate" />));
  expect(tree!.root.findByType("img").props.src).toBe("/avatars/candidate-neutral.webp");
  expect(vi.getTimerCount()).toBe(0);
});

it("has no photographic animation rules, timers, frame subscriptions or expression requests to restart", () => {
  const portrait = readFileSync("src/features/interview/HumanPortrait.tsx", "utf8");
  const css = readFileSync("src/features/interview/ActiveSpeakerStage.css", "utf8");
  expect(portrait).not.toMatch(/subscribeFrames|requestAnimationFrame|setTimeout|setInterval|<svg|<image|mouthBlend/);
  expect(portrait).not.toMatch(/-(?:soft|open|blink)\.webp/);
  expect(css).not.toMatch(/iv-human-(?:mouth|blink|settle|expressions)|@keyframes|animation\s*:/);
});
