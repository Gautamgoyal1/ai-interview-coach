import { act, create, type ReactTestRenderer } from "react-test-renderer";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import ActiveSpeakerStage, { getAvatarStates, type ActiveSpeakerStageProps } from "../src/features/interview/ActiveSpeakerStage";
import InterviewRoom from "../src/pages/InterviewRoom";
import { createVoiceActivity } from "../src/features/interview/voiceActivity";

const mocks = vi.hoisted(() => ({ interview: {} as any, voice: {} as any, useVoice: vi.fn() }));
vi.mock("../src/features/interview/useInterview", () => ({ useInterview: () => mocks.interview }));
vi.mock("../src/features/interview/useVoiceInterview", () => ({ useVoiceInterview: (opts: any) => {
  mocks.useVoice(opts);
  return mocks.voice;
} }));
vi.mock("../src/hooks/useAuth", () => ({ useAuth: () => ({ logout: vi.fn() }) }));
vi.mock("../src/hooks/useUnsentAnswerWarning", () => ({ useUnsentAnswerWarning: vi.fn(), confirmDiscardAnswer: vi.fn() }));
vi.mock("../src/components/ThemeToggle", () => ({ default: () => null }));

const defaults: ActiveSpeakerStageProps = { voiceState: "ready", isMuted: false, isAudioLoading: false, microphoneLevel: 0.5, playbackLevel: 0.5 };
let tree: ReactTestRenderer | undefined;
afterEach(() => { act(() => tree?.unmount()); tree = undefined; vi.clearAllMocks(); });

it.each([
  ["ready", "idle", "idle", "Microphone off"],
  ["ai_speaking", "speaking", "listening", "Listening to question"],
  ["starting", "listening", "thinking", "Connecting microphone"],
  ["listening", "listening", "speaking", "Voice activity · recording"],
  ["stopping", "listening", "thinking", "Finalizing transcript"],
  ["review", "idle", "idle", "Review your transcript"],
  ["submitting", "thinking", "thinking", "Please wait"],
] as const)("maps %s without running audio or submission actions", (voiceState, ai, user, label) => {
  const result = getAvatarStates({ ...defaults, voiceState });
  expect(result.interviewer.state).toBe(ai);
  expect(result.candidate).toEqual({ state: user, label });
});

it("uses preparation state only while synthesis is pending, then actual playback wins", () => {
  const pending = { ...defaults, isAudioLoading: true };
  expect(getAvatarStates(pending).interviewer.state).toBe("thinking");
  expect(getAvatarStates(pending).candidate.label).toBe("Microphone off");
  expect(getAvatarStates({ ...pending, voiceState: "ai_speaking" }).interviewer.state).toBe("speaking");
});

it("never depicts muted playback as speaking and does not confuse output mute with microphone mute", () => {
  const muted = { ...defaults, isMuted: true, isAudioLoading: true };
  expect(getAvatarStates({ ...muted, voiceState: "ai_speaking" }).interviewer.state).toBe("muted");
  expect(getAvatarStates({ ...muted, voiceState: "review" }).candidate.label).toBe("Review your transcript");
  const recording = getAvatarStates({ ...muted, voiceState: "listening" });
  expect(recording.interviewer.state).toBe("listening");
  expect(recording.candidate.state).toBe("speaking");
});

it("reflects shared errors without inferring which Azure service failed, while active recording stays accurate", () => {
  const failed = { ...defaults, voiceError: "Microphone access denied" };
  expect(getAvatarStates(failed).interviewer.state).toBe("error");
  expect(getAvatarStates(failed).candidate.state).toBe("error");
  expect(getAvatarStates({ ...failed, voiceState: "listening" }).candidate.state).toBe("speaking");
  expect(getAvatarStates({ ...failed, voiceState: "stopping" }).candidate.label).toBe("Finalizing transcript");
});

it("shows waiting during generation or submission instead of a stale active speaker", () => {
  const result = getAvatarStates({ ...defaults, voiceState: "ai_speaking", processing: true });
  expect(result.interviewer.state).toBe("thinking");
  expect(result.candidate.state).toBe("thinking");
});

it("keeps portraits decorative, labels readable, and avatars out of the keyboard tab order", () => {
  act(() => { tree = create(<ActiveSpeakerStage {...defaults} voiceState="listening" />); });
  expect(tree!.root.findAllByType("svg")).toHaveLength(0);
  expect(tree!.root.findAllByType("img")).toHaveLength(2);
  for (const svg of tree!.root.findAllByType("svg")) {
    expect(svg.props["aria-hidden"]).toBe("true");
    expect(svg.props.focusable).toBe("false");
  }
  expect(tree!.root.findAllByProps({ "aria-label": "Voice interview participants" })).toHaveLength(1);
  expect(tree!.root.findAllByProps({ "data-active": true })).toHaveLength(1);
  expect(tree!.root.findAllByType("button")).toHaveLength(0);
  expect(tree!.root.findAll(node => node.props.tabIndex !== undefined)).toHaveLength(0);
});

it.each([0, null, undefined])("never animates recording silence or unavailable activity (%s) as speech", microphoneLevel => {
  act(() => { tree = create(<ActiveSpeakerStage {...defaults} voiceState="listening" microphoneLevel={microphoneLevel} />); });
  const main = tree!.root.findByProps({ "data-prominence": "main" });
  expect(main.props["data-avatar-role"]).toBe("candidate");
  expect(main.props["data-state"]).toBe("listening");
  expect(tree!.root.findAllByProps({ "data-mouth": "closed" })).toHaveLength(2);
  expect(tree!.root.findAllByProps({ "data-active": true })).toHaveLength(0);
});

it("keeps a neutral portrait during silent TTS audio and while generating audio", () => {
  act(() => { tree = create(<ActiveSpeakerStage {...defaults} voiceState="ai_speaking" playbackLevel={0} />); });
  expect(tree!.root.findByProps({ "data-prominence": "main" }).props["data-state"]).toBe("listening");
  expect(tree!.root.findAllByProps({ "data-mouth": "closed" })).toHaveLength(2);
  act(() => tree!.update(<ActiveSpeakerStage {...defaults} isAudioLoading />));
  expect(tree!.root.findByProps({ "data-prominence": "main" }).props["data-state"]).toBe("thinking");
  expect(tree!.root.findAllByProps({ "data-mouth": "closed" })).toHaveLength(2);
});

it("retains a static fallback if a base portrait cannot load", () => {
  act(() => { tree = create(<ActiveSpeakerStage {...defaults} />); });
  act(() => tree!.root.findAllByType("img")[0].props.onError());
  expect(tree!.root.findAllByProps({ "data-image-error": true })).toHaveLength(1);
  expect(tree!.root.findByProps({ className: "iv-human-fallback" }).children).toContain("AI interviewer");
});

it("uses a single audio-meter subscriber while keeping the portrait stable through activity, buffering and mute", () => {
  const activity = createVoiceActivity();
  const subscribe = activity.subscribeFrames;
  let active = 0, maximum = 0;
  activity.subscribeFrames = listener => {
    active++; maximum = Math.max(maximum, active);
    const stop = subscribe(listener);
    return () => { active--; stop(); };
  };
  const marks = Array.from({ length: 5 }, () => ({ dataset: { lit: "false" } }));
  const props = { ...defaults, voiceState: "ai_speaking" as const, playbackActivity: activity };
  act(() => { tree = create(<ActiveSpeakerStage {...props} />, {
    createNodeMock: node => node.props.className === "iv-avatar-meter" ? { querySelectorAll: () => marks } : null,
  }); });
  const image = tree!.root.findAllByType("img")[0];
  for (const level of [.2, .9, .5, 0, .7, 0]) {
    act(() => activity.setLevel(level));
    expect(marks[0].dataset.lit).toBe(String(level >= .08));
    expect(tree!.root.findAllByType("img")[0]).toBe(image);
    expect(tree!.root.findAllByType("svg")).toHaveLength(0);
  }
  for (const options of [{ voiceState: "ready" as const, isAudioLoading: true }, { isMuted: true }, { voiceError: "Audio failed" }]) {
    act(() => tree!.update(<ActiveSpeakerStage {...props} {...options} />));
    act(() => activity.setLevel(.95));
    expect(marks.every(mark => mark.dataset.lit === "false")).toBe(true);
    expect(tree!.root.findAllByType("img")[0]).toBe(image);
  }
  expect(maximum).toBe(1);
  act(() => tree!.unmount()); tree = undefined;
  expect(active).toBe(0);
  activity.setLevel(.2);
  expect(marks.every(mark => mark.dataset.lit === "false")).toBe(true);
});

it.each([
  [{ voiceState: "ready" }, "interviewer", "idle"],
  [{ voiceState: "ai_speaking" }, "interviewer", "speaking"],
  [{ voiceState: "listening" }, "candidate", "speaking"],
  [{ voiceState: "starting" }, "candidate", "thinking"],
  [{ voiceState: "stopping" }, "candidate", "thinking"],
  [{ voiceState: "review" }, "candidate", "idle"],
  [{ voiceState: "submitting" }, "interviewer", "thinking"],
  [{ voiceState: "review", isAudioLoading: true }, "interviewer", "thinking"],
  [{ voiceState: "ai_speaking", isMuted: true }, "interviewer", "muted"],
  [{ voiceState: "listening", isMuted: true }, "candidate", "speaking"],
  [{ voiceState: "ready", voiceError: "Audio unavailable" }, "interviewer", "error"],
  [{ voiceState: "review", voiceError: "Recording interrupted" }, "candidate", "error"],
  [{ voiceState: "review", processing: true }, "interviewer", "thinking"],
] as const)("keeps exactly one main portrait for %j", (options, role, state) => {
  act(() => { tree = create(<ActiveSpeakerStage {...defaults} {...options} />); });
  const main = tree!.root.findAllByProps({ "data-prominence": "main" });
  const secondary = tree!.root.findAllByProps({ "data-prominence": "secondary" });
  expect(main).toHaveLength(1);
  expect(secondary).toHaveLength(1);
  expect(main[0].props["data-avatar-role"]).toBe(role);
  expect(main[0].props["data-state"]).toBe(state);
  expect(secondary[0].props["data-avatar-role"]).not.toBe(role);
  expect(secondary[0].props["data-active"]).toBe(false);
});

it("switches focus through playback, recording, finalization and review without retaining an old speaker", () => {
  act(() => { tree = create(<ActiveSpeakerStage {...defaults} />); });
  for (const voiceState of ["ai_speaking", "listening", "stopping", "review", "submitting", "ai_speaking", "ready"] as const) {
    act(() => tree!.update(<ActiveSpeakerStage {...defaults} voiceState={voiceState} />));
    const main = tree!.root.findByProps({ "data-prominence": "main" });
    expect(main.props["data-avatar-role"]).toBe(
      ["listening", "stopping", "review"].includes(voiceState) ? "candidate" : "interviewer",
    );
    expect(tree!.root.findAllByProps({ "data-active": true })).toHaveLength(
      voiceState === "ai_speaking" || voiceState === "listening" ? 1 : 0,
    );
  }
});

beforeEach(() => {
  const microphoneActivity = createVoiceActivity(), playbackActivity = createVoiceActivity();
  microphoneActivity.setLevel(0.5); playbackActivity.setLevel(0.5);
  mocks.interview = {
    session: {
      session_id: "avatar-session", target_role: "Software Engineer", interview_type: "technical",
      status: "in_progress", experience_level: "fresher", progression_mode: "adaptive",
      question_index: 1, max_questions: 5, conversation_history: [],
      current_question: { question_id: "q1", question_text: "How would you test this API?", topic: "Testing", difficulty: "medium", is_follow_up: false },
    },
    loading: false, submitting: false, error: null, unauthorized: false,
    setError: vi.fn(), beginSession: vi.fn(), loadSession: vi.fn(), submitAnswer: vi.fn(), finishSession: vi.fn(), retryQuestion: vi.fn(),
  };
  mocks.voice = {
    microphoneActivity, playbackActivity,
    ...defaults, inputMode: "voice", interimText: "", voiceError: null,
    switchInputMode: vi.fn(), toggleMute: vi.fn(), setVoiceError: vi.fn(), replayQuestionAudio: vi.fn(),
    stopQuestionAudio: vi.fn(), startRecording: vi.fn(), stopRecording: vi.fn(), prepareSubmission: vi.fn(),
  };
});
function room() {
  return <MemoryRouter initialEntries={["/interview/avatar-session?mode=voice"]}>
    <Routes><Route path="/interview/:sessionId" element={<InterviewRoom />} /></Routes>
  </MemoryRouter>;
}

it.each([
  ["text", "technical", "Technical round"], ["voice", "technical", "Technical round"],
  ["text", "hr", "Behavioral round"], ["voice", "hr", "Behavioral round"],
])("keeps session context and progress inside the question panel in %s / %s", (mode, track, label) => {
  mocks.voice.inputMode = mode;
  mocks.interview.session.interview_type = track;
  act(() => { tree = create(room()); });
  const panel = tree!.root.findByProps({ className: "iv-question-panel" });
  expect(panel.findByType("h1").children.join("")).toBe("Software Engineer Interview");
  expect(JSON.stringify(panel.findByProps({ className: "iv-role-meta" }).children)).toContain(label);
  expect(panel.findAllByProps({ role: "progressbar" })).toHaveLength(1);
  expect(tree!.root.findAllByProps({ className: "iv-subheader" })).toHaveLength(0);
  expect(tree!.root.findAllByProps({ className: "iv-header-count tabular-nums" })).toHaveLength(0);
  expect(tree!.root.findAllByProps({ className: "iv-session-heading" })).toHaveLength(1);
  expect(tree!.root.findAllByType("header")[0].findAllByType("button").some(button =>
    JSON.stringify(button.children).includes("End interview"))).toBe(true);
  act(() => tree!.root.findByType("textarea").props.onChange({ target: { value: "An editable answer" } }));
  expect(tree!.root.findByType("textarea").props.value).toBe("An editable answer");
  expect(mocks.voice.startRecording).not.toHaveBeenCalled();
  expect(mocks.interview.submitAnswer).not.toHaveBeenCalled();
});

it.each(["technical", "hr"])("reflects %s room states, preserves editable review and removes avatars in Text mode", (track) => {
  mocks.interview.session.interview_type = track;
  act(() => { tree = create(room()); });
  const candidate = () => tree!.root.findByProps({ "data-avatar-role": "candidate" });
  const interviewer = () => tree!.root.findByProps({ "data-avatar-role": "interviewer" });
  expect(mocks.useVoice).toHaveBeenCalledWith(expect.objectContaining({ interviewType: track }));
  for (const [voiceState, ai, user] of [
    ["ai_speaking", "speaking", "listening"], ["listening", "listening", "speaking"],
    ["stopping", "listening", "thinking"], ["review", "idle", "idle"],
  ]) {
    mocks.voice.voiceState = voiceState;
    act(() => tree!.update(room()));
    expect(interviewer().props["data-state"]).toBe(ai);
    expect(candidate().props["data-state"]).toBe(user);
    expect(tree!.root.findByProps({ "data-prominence": "main" }).props["data-avatar-role"])
      .toBe(voiceState === "ai_speaking" ? "interviewer" : "candidate");
  }
  expect(tree!.root.findByType("textarea").props.disabled).toBe(false);
  mocks.interview.submitting = true;
  act(() => tree!.update(room()));
  expect(interviewer().props["data-state"]).toBe("thinking");
  expect(interviewer().props["data-prominence"]).toBe("main");
  mocks.interview.submitting = false;
  mocks.voice.voiceError = "Speech is unavailable";
  act(() => tree!.update(room()));
  expect(candidate().props["data-state"]).toBe("error");
  mocks.voice.inputMode = "text";
  act(() => tree!.update(room()));
  expect(tree!.root.findAllByProps({ "aria-label": "Voice interview participants" })).toHaveLength(0);
  expect(mocks.voice.startRecording).not.toHaveBeenCalled();
  expect(mocks.voice.replayQuestionAudio).not.toHaveBeenCalled();
  expect(mocks.voice.prepareSubmission).not.toHaveBeenCalled();
  expect(mocks.interview.submitAnswer).not.toHaveBeenCalled();
});
