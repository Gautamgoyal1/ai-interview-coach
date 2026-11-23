export type ActivitySource = "microphone" | "playback-capture" | "playback-pcm" | "unavailable";
export interface VoiceActivity {
  getLevel: () => number | null;
  getStatus: () => number | null;
  getSource: () => ActivitySource;
  setLevel: (level: number | null, source?: ActivitySource) => void;
  subscribe: (listener: () => void) => () => void;
  subscribeFrames: (listener: (level: number | null) => void) => () => void;
}

// A local measurement channel, not a second interview lifecycle. Only changes
// between unavailable/silent/voiced notify React; amplitudes go directly to refs.
export function createVoiceActivity(): VoiceActivity {
  let level: number | null = null;
  let source: ActivitySource = "unavailable";
  const statuses = new Set<() => void>();
  const frames = new Set<(value: number | null) => void>();
  const getStatus = () => level === null ? null : level >= 0.08 ? 1 : 0;
  return {
    getLevel: () => level, getStatus, getSource: () => source,
    setLevel(next, nextSource) {
      const oldStatus = getStatus();
      const valid = next !== null && Number.isFinite(next) ? Math.max(0, Math.min(1, next)) : null;
      if (nextSource) source = nextSource;
      if (valid === level) return;
      level = valid;
      for (const listener of frames) listener(level);
      if (getStatus() !== oldStatus) for (const listener of statuses) listener();
    },
    subscribe(listener) { statuses.add(listener); return () => { statuses.delete(listener); }; },
    subscribeFrames(listener) { frames.add(listener); return () => { frames.delete(listener); }; },
  };
}
