import React, { useState } from "react";
import { act, create, type ReactTestRenderer } from "react-test-renderer";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { useVoiceInterview } from "../src/features/interview/useVoiceInterview";
import AnswerBox from "../src/features/interview/AnswerBox";

const mocks = vi.hoisted(() => ({ token: vi.fn(), invalidate: vi.fn(), synthesize: vi.fn(), observeMic: vi.fn(), observePlayback: vi.fn(), playPending: false, startPending: false, startFailure: false, instances: [] as any[], configs: [] as any[] }));
vi.mock("../src/features/interview/audioActivity", () => ({ observeMicrophoneActivity: mocks.observeMic, observePlaybackActivity: mocks.observePlayback }));
vi.mock("../src/services/speech.service", () => ({
  getSpeechToken: mocks.token, invalidateSpeechToken: mocks.invalidate, synthesizeSpeechAudio: mocks.synthesize,
}));
vi.mock("microsoft-cognitiveservices-speech-sdk", () => ({
  SpeechConfig: { fromAuthorizationToken: vi.fn(() => ({})) },
  AudioConfig: { fromStreamInput: vi.fn(stream => {
    const config = { stream, close: vi.fn() }; mocks.configs.push(config); return config;
  }) },
  ResultReason: { RecognizedSpeech: 3 },
  SpeechRecognizer: class {
    recognized: any; recognizing: any; canceled: any; sessionStopped: any;
    stopSuccess: any; stopError: any; authorizationToken = "initial";
    startSuccess: any;
    startContinuousRecognitionAsync = vi.fn((ok: any, err: any) => {
      this.startSuccess = ok;
      if (mocks.startFailure) err("private SDK diagnostics");
      else if (!mocks.startPending) ok();
    });
    stopContinuousRecognitionAsync = vi.fn((ok: any, err: any) => { this.stopSuccess = ok; this.stopError = err; });
    close = vi.fn();
    constructor() { mocks.instances.push(this); }
  },
}));

function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (reason: unknown) => void;
  const promise = new Promise<T>((ok, fail) => { resolve = ok; reject = fail; });
  return { promise, resolve, reject };
}
let api: ReturnType<typeof useVoiceInterview>;
let renderer: ReactTestRenderer | undefined;
let options: Record<string, any>;
let mic: ReturnType<typeof vi.fn>;
let track: { stop: ReturnType<typeof vi.fn> };
let stream: any;
let players: any[];
let hookRenders: number;
function Harness({ opts }: { opts: any }) {
  hookRenders++;
  const [answer, setAnswer] = useState("");
  api = useVoiceInterview({ initialMode: "voice", ...opts, answerText: answer, onAnswerChange: setAnswer });
  return <span>{answer}</span>;
}
async function mount(opts: Record<string, any> = {}) {
  options = opts;
  await act(async () => { renderer = create(<Harness opts={options} />); });
}
async function update(opts: Record<string, any>) {
  options = { ...options, ...opts };
  await act(async () => { renderer!.update(<Harness opts={options} />); });
}
async function start() { await act(async () => { await api.startRecording(); }); return mocks.instances.at(-1); }
function final(recognizer: any, text: string) { recognizer.recognized(null, { result: { reason: 3, text } }); }

beforeEach(() => {
  vi.useFakeTimers();
  mocks.instances.length = mocks.configs.length = 0;
  mocks.startPending = mocks.startFailure = false;
  mocks.playPending = false; hookRenders = 0;
  mocks.token.mockReset().mockResolvedValue({ token: "token-one", region: "eastasia", expires_in: 600 });
  mocks.invalidate.mockReset();
  mocks.synthesize.mockReset().mockResolvedValue(new Blob(["mp3"]));
  mocks.observeMic.mockReset().mockImplementation(() => vi.fn());
  mocks.observePlayback.mockReset().mockImplementation(() => vi.fn());
  track = { stop: vi.fn() };
  stream = { getTracks: () => [track] };
  mic = vi.fn().mockResolvedValue(stream);
  vi.stubGlobal("navigator", { mediaDevices: { getUserMedia: mic } });
  players = [];
  vi.stubGlobal("Audio", class {
    onplay: any; onended: any; onerror: any;
    pause = vi.fn(); load = vi.fn(); removeAttribute = vi.fn();
    play = vi.fn(() => {
      this.onplay?.();
      if (mocks.playPending) return new Promise<void>(done => { (this as any).finishPlay = () => { (this as any).onplaying?.(); done(); }; });
      (this as any).onplaying?.(); return Promise.resolve();
    });
    constructor(public src: string) { players.push(this); }
  });
  vi.spyOn(URL, "createObjectURL").mockReturnValue("blob:offline");
  vi.spyOn(URL, "revokeObjectURL").mockImplementation(() => {});
});
afterEach(async () => {
  await act(async () => { renderer?.unmount(); });
  renderer = undefined;
  vi.useRealTimers(); vi.restoreAllMocks(); vi.unstubAllGlobals();
});

describe("recognition lifecycle", () => {
  it("observes the existing stream without extra permissions and rejects late activity after review", async () => {
    let report!: (level: number) => void;
    const stopActivity = vi.fn();
    mocks.observeMic.mockImplementation((_stream, callback) => { report = callback; return stopActivity; });
    await mount(); const rec = await start();
    expect(mocks.observeMic).toHaveBeenCalledWith(stream, expect.any(Function));
    act(() => report(0.5)); expect(api.microphoneLevel).toBe(0.5);
    act(() => report(0)); expect(api.microphoneLevel).toBe(0);
    let completion!: Promise<void>;
    act(() => { completion = api.stopRecording(); });
    expect(stopActivity).toHaveBeenCalledTimes(1);
    expect(api.microphoneLevel).toBeNull();
    expect(rec.close).not.toHaveBeenCalled(); expect(track.stop).not.toHaveBeenCalled();
    await act(async () => { final(rec, "The final words still arrive."); rec.stopSuccess(); await completion; });
    expect(api.voiceState).toBe("review");
    expect(track.stop).toHaveBeenCalledTimes(1);
    act(() => report(1)); expect(api.microphoneLevel).toBeNull();
    expect(mic).toHaveBeenCalledTimes(1);
  });

  it("clears visual playback activity on pause, mute and stale callbacks", async () => {
    let report!: (level: number) => void;
    const stopActivity = vi.fn();
    mocks.observePlayback.mockImplementation((_audio, _blob, callback) => { report = callback; return stopActivity; });
    await mount({ questionText: "A question", questionId: "q1" });
    expect(api.voiceState).toBe("ai_speaking");
    act(() => report(0.5)); expect(api.playbackLevel).toBe(0.5);
    act(() => players[0].onpause());
    expect(api.voiceState).toBe("ready"); expect(api.playbackLevel).toBe(0);
    act(() => players[0].onplaying()); expect(api.voiceState).toBe("ai_speaking");
    act(() => api.toggleMute());
    expect(api.playbackLevel).toBeNull();
    expect(stopActivity).toHaveBeenCalledTimes(1);
    act(() => report(1)); expect(api.playbackLevel).toBeNull();
    expect(players[0].onplaying).toBeNull();
  });

  it("waits for actual playing and handles buffering, completion and error without a frozen mouth", async () => {
    mocks.playPending = true;
    await mount({ questionText: "Question?", questionId: "q1" });
    expect(api.voiceState).toBe("ready"); expect(api.isAudioLoading).toBe(true);
    act(() => players[0].onwaiting()); expect(api.voiceState).toBe("ready");
    await act(async () => { players[0].finishPlay(); });
    expect(api.voiceState).toBe("ai_speaking"); expect(api.isAudioLoading).toBe(false);
    act(() => players[0].onwaiting());
    expect(api.voiceState).toBe("ready"); expect(api.playbackLevel).toBe(0); expect(api.isAudioLoading).toBe(true);
    act(() => { players[0].paused = true; players[0].onseeking(); players[0].onseeked(); });
    expect(api.isAudioLoading).toBe(false); expect(api.voiceState).toBe("ready");
    players[0].paused = false;
    act(() => players[0].onplaying()); expect(api.voiceState).toBe("ai_speaking");
    act(() => players[0].onended()); expect(api.playbackLevel).toBeNull(); expect(api.voiceState).toBe("ready");
    mocks.playPending = false;
    await act(async () => { await api.replayQuestionAudio(); });
    act(() => players.at(-1).onerror()); expect(api.voiceError).toContain("Unable to play");
    expect(api.playbackLevel).toBeNull(); expect(api.voiceState).toBe("ready");
  });

  it("does not rerender the interview hook host for high-frequency amplitude changes", async () => {
    let report!: (level: number) => void;
    mocks.observePlayback.mockImplementation((_audio, _blob, callback) => { report = callback; return vi.fn(); });
    await mount({ questionText: "Question?", questionId: "q1" });
    const count = hookRenders;
    act(() => { for (let i = 0; i < 120; i++) report((i % 60) / 60); });
    expect(hookRenders).toBe(count);
    expect(api.playbackActivity.getLevel()).toBeGreaterThan(.9);
  });
  it("releases the one stream on SDK startup failure", async () => {
    mocks.startFailure = true;
    await mount(); const rec = await start();
    expect(rec.close).toHaveBeenCalledTimes(1);
    expect(track.stop).toHaveBeenCalledTimes(1);
    expect(api.voiceError).toContain("Unable to start");
    expect(api.voiceError).not.toContain("private");
  });

  it("handles stop while the SDK is starting and ignores its late start callback", async () => {
    mocks.startPending = true;
    await mount(); const rec = await start();
    expect(api.voiceState).toBe("starting");
    act(() => { api.stopRecording(); rec.startSuccess(); });
    expect(api.voiceState).toBe("stopping");
    act(() => rec.stopSuccess());
    expect(api.voiceState).toBe("review");
    expect(track.stop).toHaveBeenCalledTimes(1);
  });

  it("releases the microphone when SDK startup hangs", async () => {
    mocks.startPending = true;
    await mount(); await start();
    await act(async () => { await vi.advanceTimersByTimeAsync(15000); });
    expect(track.stop).toHaveBeenCalledTimes(1);
    expect(api.voiceError).toContain("timed out");
  });

  it("drains final results before review, requires a separate submit action, never submits interim text", async () => {
    await mount(); const rec = await start();
    act(() => { final(rec, "First"); final(rec, "second"); rec.recognizing(null, { result: { text: "interim" } }); });
    let result: string | null | undefined;
    let completion!: Promise<void>;
    act(() => { completion = api.prepareSubmission().then(value => { result = value; }); });
    expect(api.voiceState).toBe("stopping"); expect(result).toBeUndefined();
    act(() => { rec.sessionStopped(); final(rec, "last words"); });
    expect(rec.close).not.toHaveBeenCalled();
    await act(async () => { rec.stopSuccess(); await completion; });
    expect(result).toBeNull(); expect(api.voiceState).toBe("review");
    expect(await api.prepareSubmission()).toBe("First second last words");
    expect(api.interimText).toBe(""); expect(track.stop).toHaveBeenCalledTimes(1);
    expect(mocks.configs[0].stream).toBe(stream); expect(mic).toHaveBeenCalledTimes(1);
  });

  it("does not open a microphone when token fetching fails", async () => {
    mocks.token.mockRejectedValue(new Error("private details"));
    await mount(); await start();
    expect(mic).not.toHaveBeenCalled(); expect(api.voiceState).toBe("review");
    expect(api.voiceError).not.toContain("private details");
  });

  it("handles denied microphone permission without starting recognition", async () => {
    mic.mockRejectedValue(new DOMException("denied", "NotAllowedError"));
    await mount(); await start();
    expect(api.micPermission).toBe("denied"); expect(mocks.instances).toHaveLength(0);
    expect(api.voiceError).toContain("denied");
  });

  it("serializes rapid starts and releases a late permission stream after stopping", async () => {
    const permission = deferred<any>(); mic.mockReturnValue(permission.promise);
    await mount();
    let pending!: Promise<void>;
    await act(async () => { pending = api.startRecording(); });
    await act(async () => { await api.startRecording(); await api.stopRecording(); });
    await act(async () => { permission.resolve(stream); await pending; });
    expect(mic).toHaveBeenCalledTimes(1); expect(track.stop).toHaveBeenCalledTimes(1);
    expect(mocks.instances).toHaveLength(0);
  });

  it("ignores a late token after switching to text", async () => {
    const token = deferred<any>(); mocks.token.mockReturnValue(token.promise);
    await mount(); let pending!: Promise<void>;
    act(() => { pending = api.startRecording(); api.switchInputMode("text"); });
    await act(async () => { token.resolve({ token: "late", region: "eastasia", expires_in: 600 }); await pending; });
    expect(mic).not.toHaveBeenCalled(); expect(api.inputMode).toBe("text");
  });

  it("keeps final segments during rapid mode switching and prevents a second recognizer until drained", async () => {
    await mount(); const rec = await start();
    act(() => { api.switchInputMode("text"); api.switchInputMode("voice"); });
    await act(async () => { await api.startRecording(); });
    expect(mocks.instances).toHaveLength(1);
    act(() => { final(rec, "retained"); rec.stopSuccess(); });
    const next = await start();
    act(() => { final(rec, "stale"); rec.sessionStopped(); final(next, "new"); });
    expect(next.close).not.toHaveBeenCalled();
    let completion!: Promise<void>;
    act(() => { completion = api.stopRecording(); });
    await act(async () => { next.stopSuccess(); await completion; });
    expect(await api.prepareSubmission()).toBe("retained new");
  });

  it("renews the active recognizer token and stops renewal after release", async () => {
    await mount(); const rec = await start();
    mocks.token.mockResolvedValue({ token: "renewed", region: "eastasia", expires_in: 600 });
    await act(async () => { await vi.advanceTimersByTimeAsync(540000); });
    expect(rec.authorizationToken).toBe("renewed");
    act(() => { api.stopRecording(); rec.stopSuccess(); });
    await act(async () => { await vi.advanceTimersByTimeAsync(600000); });
    expect(mocks.token).toHaveBeenCalledTimes(2);
  });

  it("refreshes a token that expires while waiting for permission", async () => {
    const permission = deferred<any>(); mic.mockReturnValue(permission.promise);
    await mount(); let pending!: Promise<void>;
    await act(async () => { pending = api.startRecording(); });
    await act(async () => { await vi.advanceTimersByTimeAsync(600000); });
    await act(async () => { permission.resolve(stream); await pending; });
    expect(mocks.token).toHaveBeenCalledTimes(2);
    expect(api.voiceState).toBe("listening");
  });

  it("preserves captured words and releases the microphone on renewal failure", async () => {
    await mount(); const rec = await start(); act(() => final(rec, "saved"));
    mocks.token.mockRejectedValue(new Error("private"));
    await act(async () => { await vi.advanceTimersByTimeAsync(540000); });
    expect(track.stop).toHaveBeenCalledTimes(1); expect(api.voiceState).toBe("review");
    expect(await api.prepareSubmission()).toBe("saved"); expect(api.voiceError).toContain("renewed");
  });

  it("stops at token expiry if renewal hangs", async () => {
    await mount(); await start(); mocks.token.mockReturnValue(new Promise(() => {}));
    await act(async () => { await vi.advanceTimersByTimeAsync(600000); });
    expect(track.stop).toHaveBeenCalledTimes(1); expect(api.voiceError).toContain("expired");
  });

  it("times out a stalled stop without automatically submitting", async () => {
    await mount(); const rec = await start(); act(() => final(rec, "captured"));
    let result: any;
    act(() => { void api.prepareSubmission().then(value => { result = value; }); });
    await act(async () => { await vi.advanceTimersByTimeAsync(15000); });
    expect(result).toBeNull(); expect(track.stop).toHaveBeenCalledTimes(1);
    expect(api.voiceError).toContain("missing words");
  });

  it("cleans up cancellation, unmount, and ignores late callbacks", async () => {
    await mount(); const rec = await start();
    act(() => { final(rec, "saved"); rec.canceled(); });
    expect(mocks.invalidate).toHaveBeenCalled(); expect(track.stop).toHaveBeenCalledTimes(1);
    const next = await start();
    await act(async () => { renderer!.unmount(); renderer = undefined; });
    expect(next.close).toHaveBeenCalledTimes(1);
    expect(() => final(next, "late")).not.toThrow();
  });
});

describe("question audio", () => {
  it("aborts stale synthesis on question changes and ignores even an uncancellable response", async () => {
    const old = deferred<Blob>(); mocks.synthesize.mockReturnValueOnce(old.promise);
    await mount({ questionId: "one", questionText: "First?" });
    const signal = mocks.synthesize.mock.calls[0][3];
    await update({ questionId: "two", questionText: "Second?" });
    expect(signal.aborted).toBe(true); expect(players).toHaveLength(1);
    await act(async () => { old.resolve(new Blob(["late"])); });
    expect(players).toHaveLength(1);
  });

  it("aborts pending TTS before recording and blocks replay while recording", async () => {
    const old = deferred<Blob>(); mocks.synthesize.mockReturnValueOnce(old.promise);
    await mount({ questionId: "one", questionText: "First?" });
    const signal = mocks.synthesize.mock.calls[0][3];
    await start(); expect(signal.aborted).toBe(true);
    await act(async () => { await api.replayQuestionAudio(); old.resolve(new Blob(["late"])); });
    expect(players).toHaveLength(0); expect(mocks.synthesize).toHaveBeenCalledTimes(1);
  });

  it("stops playback and releases URLs on mute, replay, text mode, and unmount", async () => {
    await mount({ questionId: "one", questionText: "First?" });
    const first = players[0]; act(() => api.toggleMute());
    expect(first.pause).toHaveBeenCalled(); expect(URL.revokeObjectURL).toHaveBeenCalledTimes(1);
    await act(async () => { api.toggleMute(); });
    await act(async () => { await api.replayQuestionAudio(); });
    expect(players[1].pause).toHaveBeenCalled();
    act(() => api.switchInputMode("text")); expect(players.at(-1).pause).toHaveBeenCalled();
    await act(async () => { api.switchInputMode("voice"); });
    const signal = mocks.synthesize.mock.calls.at(-1)![3];
    await act(async () => { renderer!.unmount(); renderer = undefined; });
    expect(signal.aborted).toBe(true); expect(players.at(-1).pause).toHaveBeenCalled();
  });

  it("ignores stale audio after switching to text and reports synthesis failures safely", async () => {
    const old = deferred<Blob>(); mocks.synthesize.mockReturnValueOnce(old.promise);
    await mount({ questionId: "one", questionText: "First?" });
    act(() => api.switchInputMode("text"));
    await act(async () => { old.resolve(new Blob(["late"])); });
    expect(players).toHaveLength(0);
    mocks.synthesize.mockRejectedValue(new Error("Azure private diagnostics"));
    await act(async () => { api.switchInputMode("voice"); });
    expect(api.voiceError).toContain("unavailable"); expect(api.voiceError).not.toContain("private");
  });

  it("respects the text selection when setup navigation updates initial mode", async () => {
    await mount(); await update({ initialMode: "text", questionId: "one", questionText: "Question?" });
    expect(api.inputMode).toBe("text"); expect(mocks.synthesize).not.toHaveBeenCalled();
  });
});

it("AnswerBox prevents submit during recognition and finalization, and submits edited text once", async () => {
  const submit = vi.fn(); const stop = vi.fn(); const change = vi.fn();
  const props = { questionId: "q", answer: "captured", onChange: change, onSubmit: submit,
    submitting: false, disabled: false, inputMode: "voice" as const, onStopRecording: stop };
  for (const state of ["starting", "listening", "stopping"] as const) {
    act(() => { renderer = create(<AnswerBox {...props} voiceState={state} />); });
    act(() => { renderer!.root.findByType("form").props.onSubmit({ preventDefault() {} }); });
    expect(submit).not.toHaveBeenCalled();
    act(() => renderer!.unmount()); renderer = undefined;
  }
  act(() => { renderer = create(<AnswerBox {...props} voiceState="review" />); });
  act(() => renderer!.root.findByType("textarea").props.onChange({ target: { value: "edited final answer" } }));
  expect(change).toHaveBeenCalledWith("edited final answer");
  act(() => renderer!.root.findByType("form").props.onSubmit({ preventDefault() {} }));
  expect(submit).toHaveBeenCalledTimes(1);
});
