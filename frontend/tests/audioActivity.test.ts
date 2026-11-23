import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { activityFromSamples, createActivityFilter, observeMicrophoneActivity, observePlaybackActivity } from "../src/features/interview/audioActivity";

const wave = (size = 512, amplitude = .1) => Float32Array.from({ length: size }, (_, i) => (i % 2 ? -1 : 1) * amplitude);
const track = () => ({ enabled: true, muted: false, readyState: "live", stop: vi.fn() });
function stream() { const audioTrack = track(); return { audioTrack, getTracks: () => [audioTrack], getAudioTracks: () => [audioTrack] }; }
class AudioFixture extends EventTarget {
  paused = true; ended = false; seeking = false; readyState = 0; muted = false; volume = 1; currentTime = .04;
  event(name: string) { this.dispatchEvent(new Event(name)); }
  playing() { this.paused = false; this.readyState = 4; this.event("playing"); }
}
let signal: number, contexts: any[], decode: ReturnType<typeof vi.fn>, documentFixture: EventTarget & { hidden: boolean };
const level = (report: ReturnType<typeof vi.fn>) => report.mock.calls.at(-1)?.[0];
beforeEach(() => {
  vi.useFakeTimers(); vi.setSystemTime(0); vi.stubGlobal("performance", { now: () => Date.now() });
  signal = 0; contexts = [];
  documentFixture = Object.assign(new EventTarget(), { hidden: false }); vi.stubGlobal("document", documentFixture);
  decode = vi.fn(async () => ({ sampleRate: 1000, numberOfChannels: 1, getChannelData: () => {
    const data = wave(160); data.fill(0, 80); return data;
  } }));
  vi.stubGlobal("AudioContext", class {
    state = "running";
    analyser = { fftSize: 512, getFloatTimeDomainData: vi.fn((data: Float32Array) => data.set(wave(data.length, signal))), disconnect: vi.fn() };
    source = { connect: vi.fn(), disconnect: vi.fn() };
    createMediaStreamSource = vi.fn(() => this.source);
    createMediaElementSource = vi.fn(() => { throw new Error("Original audio output must not be rerouted"); });
    createAnalyser = vi.fn(() => this.analyser);
    resume = vi.fn(async () => {}); decodeAudioData = decode;
    close = vi.fn(async () => { this.state = "closed"; });
    constructor() { contexts.push(this); }
  });
});
afterEach(() => { vi.useRealTimers(); vi.unstubAllGlobals(); });

it("rejects silence, DC bias, low background noise and invalid values without quantizing voiced energy", () => {
  expect(activityFromSamples(new Float32Array(20))).toBe(0);
  expect(activityFromSamples(new Float32Array(20).fill(.5))).toBe(0);
  expect(activityFromSamples(wave(512, .003))).toBe(0);
  expect(activityFromSamples(wave())).toBeGreaterThan(.4);
  expect(activityFromSamples(new Float32Array([NaN, Infinity]))).toBe(0);
  expect(activityFromSamples(new Float32Array([1000, -1000]))).toBe(1);
});
it("smooths attack/release with hysteresis and closes within 100ms of silence", () => {
  const filter = createActivityFilter();
  expect(filter.sample(.5, 0)).toBeGreaterThan(.4);
  expect(filter.sample(.07, 16)).toBeGreaterThan(0);
  for (let t = 32; t <= 112; t += 16) filter.sample(0, t);
  expect(filter.sample(0, 128)).toBe(0);
  filter.reset(); expect(filter.sample(.07, 0)).toBe(0);
});
it("observes only the supplied mic stream and releases analysis without stopping its tracks", async () => {
  const mic = stream(), report = vi.fn(); const stop = observeMicrophoneActivity(mic as any, report);
  expect(level(report)).toBe(0); signal = .1; await vi.advanceTimersByTimeAsync(32);
  expect(level(report)).toBeGreaterThan(.4);
  signal = 0; await vi.advanceTimersByTimeAsync(112); expect(level(report)).toBe(0);
  stop(); stop(); expect(mic.audioTrack.stop).not.toHaveBeenCalled();
  expect(contexts[0].createMediaStreamSource).toHaveBeenCalledWith(mic);
  expect(contexts[0].source.disconnect).toHaveBeenCalledTimes(1);
  expect(contexts[0].close).toHaveBeenCalledTimes(1);
  const count = report.mock.calls.length; await vi.advanceTimersByTimeAsync(1000);
  expect(report).toHaveBeenCalledTimes(count);
});
it.each(["enabled", "muted", "readyState"])("stops mouth activity for a disabled/muted/ended mic (%s)", async key => {
  const mic = stream(), report = vi.fn(); signal = .1;
  const stop = observeMicrophoneActivity(mic as any, report);
  expect(level(report)).toBeGreaterThan(.4);
  Object.assign(mic.audioTrack, { [key]: key === "enabled" ? false : key === "muted" ? true : "ended" });
  await vi.advanceTimersByTimeAsync(16); expect(level(report)).toBe(0); stop();
});
it("keeps unsupported, suspended or failed mic analysis independent of recognition", async () => {
  const report = vi.fn(), stop = observeMicrophoneActivity(stream() as any, report);
  contexts[0].state = "suspended"; await vi.advanceTimersByTimeAsync(16); expect(level(report)).toBeNull(); stop();
  vi.stubGlobal("AudioContext", undefined);
  observeMicrophoneActivity(stream() as any, report)(); expect(level(report)).toBeNull();
  vi.stubGlobal("AudioContext", class { constructor() { throw new Error("Unavailable"); } });
  expect(() => observeMicrophoneActivity(stream() as any, report)()).not.toThrow();
});
it("falls back to a captured playback copy when decoding fails, without changing native output", async () => {
  const audio = new AudioFixture(), copy = stream(); signal = .1;
  Object.assign(audio, { captureStream: vi.fn(() => copy) });
  decode.mockRejectedValue(new Error("Unsupported offline codec"));
  const report = vi.fn(), stop = observePlaybackActivity(audio as any, new Blob(["wav"]), report);
  audio.playing(); await vi.advanceTimersByTimeAsync(32);
  expect(level(report)).toBeGreaterThan(.4);
  expect(report.mock.calls.at(-1)?.[1]).toBe("playback-capture");
  expect(decode).toHaveBeenCalledTimes(1); expect(contexts[0].createMediaElementSource).not.toHaveBeenCalled();
  stop(); expect(copy.audioTrack.stop).toHaveBeenCalledTimes(1); expect(audio.paused).toBe(false);
  expect(contexts[0].close).toHaveBeenCalledTimes(1);
});
it("uses offline PCM decoding without creating a live playback context", async () => {
  vi.stubGlobal("OfflineAudioContext", class { decodeAudioData = decode; });
  const audio = new AudioFixture(), report = vi.fn();
  const stop = observePlaybackActivity(audio as any, new Blob(["wav"]), report);
  audio.playing(); await vi.advanceTimersByTimeAsync(32);
  expect(level(report)).toBeGreaterThan(.4); expect(contexts).toHaveLength(0);
  expect(report.mock.calls.at(-1)?.[1]).toBe("playback-pcm"); stop();
});
it("waits for playing, not play, and never animates while generating or buffering audio", async () => {
  const audio = new AudioFixture(), report = vi.fn(), stop = observePlaybackActivity(audio as any, new Blob(["wav"]), report);
  audio.paused = false; audio.readyState = 1; audio.event("play");
  await vi.advanceTimersByTimeAsync(200); expect(report.mock.calls.some(([v]) => v > 0)).toBe(false);
  audio.playing(); await vi.advanceTimersByTimeAsync(32); expect(level(report)).toBeGreaterThan(.4); stop();
});
it.each(["pause", "waiting", "seeking", "ended", "error", "emptied"])("closes immediately on %s and leaves no progressing frame loop", async event => {
  const audio = new AudioFixture(), report = vi.fn(), stop = observePlaybackActivity(audio as any, new Blob(["wav"]), report);
  audio.playing(); await vi.advanceTimersByTimeAsync(32); expect(level(report)).toBeGreaterThan(.4);
  audio.event(event); expect(level(report)).toBe(0);
  const count = report.mock.calls.length; await vi.advanceTimersByTimeAsync(200); expect(report).toHaveBeenCalledTimes(count);
  stop();
});
it("resumes and seeks using the real media clock with a causal sample window", async () => {
  const audio = new AudioFixture(), report = vi.fn(), stop = observePlaybackActivity(audio as any, new Blob(["wav"]), report);
  audio.playing(); await vi.advanceTimersByTimeAsync(32); expect(level(report)).toBeGreaterThan(.4);
  audio.event("pause"); audio.currentTime = .12; audio.playing();
  await vi.advanceTimersByTimeAsync(64); expect(level(report)).toBe(0);
  audio.event("seeking"); audio.currentTime = .04; audio.playing();
  await vi.advanceTimersByTimeAsync(32); expect(level(report)).toBeGreaterThan(.4); stop();
});
it.each(["muted", "volume"])("closes for muted/zero-volume playback (%s)", async key => {
  const audio = new AudioFixture(), report = vi.fn(), stop = observePlaybackActivity(audio as any, new Blob(["wav"]), report);
  audio.playing(); await vi.advanceTimersByTimeAsync(32);
  Object.assign(audio, { [key]: key === "muted" ? true : 0 });
  await vi.advanceTimersByTimeAsync(16); expect(level(report)).toBe(0); stop();
});
it("suspends animation while hidden and resumes without timer drift", async () => {
  const audio = new AudioFixture(), report = vi.fn(), stop = observePlaybackActivity(audio as any, new Blob(["wav"]), report);
  audio.playing(); await vi.advanceTimersByTimeAsync(32);
  documentFixture.hidden = true; documentFixture.dispatchEvent(new Event("visibilitychange"));
  expect(level(report)).toBe(0); const count = report.mock.calls.length;
  await vi.advanceTimersByTimeAsync(1000); expect(report).toHaveBeenCalledTimes(count);
  audio.currentTime = .12; documentFixture.hidden = false; documentFixture.dispatchEvent(new Event("visibilitychange"));
  await vi.advanceTimersByTimeAsync(32); expect(level(report)).toBe(0); stop();
});
it("fails closed when decoding fails, without a runaway polling loop", async () => {
  decode.mockRejectedValue(new Error("Unsupported codec"));
  const audio = new AudioFixture(), report = vi.fn(), stop = observePlaybackActivity(audio as any, new Blob(["bad"]), report);
  audio.playing(); await vi.advanceTimersByTimeAsync(80); expect(level(report)).toBeNull();
  const count = report.mock.calls.length; await vi.advanceTimersByTimeAsync(1000); expect(report).toHaveBeenCalledTimes(count); stop();
});
it("ignores decoded samples and playing callbacks after cleanup", async () => {
  let resolve!: (value: any) => void;
  decode.mockReturnValue(new Promise(done => { resolve = done; }));
  const audio = new AudioFixture(), report = vi.fn(), stop = observePlaybackActivity(audio as any, new Blob(["wav"]), report);
  await vi.advanceTimersByTimeAsync(1); stop(); const count = report.mock.calls.length;
  resolve({ sampleRate: 1000, numberOfChannels: 1, getChannelData: vi.fn() }); audio.playing();
  await vi.advanceTimersByTimeAsync(1000); expect(report).toHaveBeenCalledTimes(count);
  expect(contexts[0].close).toHaveBeenCalledTimes(1);
});

it("keeps one analysis loop through repeated playing events and releases it after backgrounding or cancellation", async () => {
  const pending = new Map<number, FrameRequestCallback>();
  let next = 0;
  vi.stubGlobal("requestAnimationFrame", (callback: FrameRequestCallback) => { pending.set(++next, callback); return next; });
  vi.stubGlobal("cancelAnimationFrame", (id: number) => pending.delete(id));
  const audio = new AudioFixture(), report = vi.fn();
  const stop = observePlaybackActivity(audio as any, new Blob(["wav"]), report);
  audio.playing();
  for (let i = 0; i < 20; i++) audio.event("playing");
  await vi.advanceTimersByTimeAsync(1);
  expect(pending.size).toBe(1);
  documentFixture.hidden = true; documentFixture.dispatchEvent(new Event("visibilitychange"));
  expect(pending.size).toBe(0); expect(level(report)).toBe(0);
  documentFixture.hidden = false; documentFixture.dispatchEvent(new Event("visibilitychange"));
  expect(pending.size).toBe(1);
  stop(); expect(pending.size).toBe(0);
  audio.playing(); expect(pending.size).toBe(0);
});
