import { expect, it, vi } from "vitest";
import { createVoiceActivity } from "../src/features/interview/voiceActivity";

it("sends amplitude frames to refs but not repeated voiced snapshots to React", () => {
  const activity = createVoiceActivity(), status = vi.fn(), frames = vi.fn();
  activity.subscribe(status); activity.subscribeFrames(frames);
  for (let i = 0; i < 60; i++) activity.setLevel(0.2 + i / 100, "playback-capture");
  expect(frames).toHaveBeenCalledTimes(60);
  expect(status).toHaveBeenCalledTimes(1);
  expect(activity.getSource()).toBe("playback-capture");
  activity.setLevel(0); expect(status).toHaveBeenCalledTimes(2);
  activity.setLevel(null); expect(status).toHaveBeenCalledTimes(3);
});
it("unsubscribes both consumers and fails closed for invalid samples", () => {
  const activity = createVoiceActivity(), status = vi.fn(), frames = vi.fn();
  const stopStatus = activity.subscribe(status), stopFrames = activity.subscribeFrames(frames);
  activity.setLevel(2); expect(activity.getLevel()).toBe(1);
  activity.setLevel(NaN); expect(activity.getLevel()).toBeNull();
  stopStatus(); stopFrames(); activity.setLevel(.5);
  expect(status).toHaveBeenCalledTimes(2); expect(frames).toHaveBeenCalledTimes(2);
});
