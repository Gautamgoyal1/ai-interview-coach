import type { ActivitySource } from "./voiceActivity";
export type ActivityReporter = (level: number | null, source?: ActivitySource) => void;

export function activityFromSamples(samples: Float32Array): number {
  if (!samples.length) return 0;
  let sum = 0, energy = 0;
  for (const value of samples) {
    const sample = Number.isFinite(value) ? value : 0;
    sum += sample; energy += sample * sample;
  }
  // Remove DC bias, then use local energy, not linguistic speech recognition.
  const mean = sum / samples.length;
  const rms = Math.sqrt(Math.max(0, energy / samples.length - mean * mean));
  return Math.min(1, Math.max(0, (rms - 0.007) * 8));
}

export function createActivityFilter() {
  let value = 0, voiced = false, previous: number | undefined;
  return {
    reset() { value = 0; voiced = false; previous = undefined; },
    sample(raw: number, now: number) {
      const elapsed = previous === undefined ? 16 : Math.max(0, Math.min(80, now - previous));
      previous = now;
      if (raw >= 0.10) voiced = true;
      else if (raw <= 0.05) voiced = false;
      const target = voiced ? raw : 0;
      value += (target - value) * (1 - Math.exp(-elapsed / (target > value ? 8 : 24)));
      if (target === 0 && value < 0.035) value = 0;
      return value;
    },
  };
}

type Frame = { id: number; raf: boolean };
function requestFrame(callback: (now: number) => void): Frame {
  return typeof requestAnimationFrame === "function"
    ? { id: requestAnimationFrame(callback), raf: true }
    : { id: setTimeout(() => callback(performance.now()), 16) as unknown as number, raf: false };
}
function cancelFrame(frame?: Frame) {
  if (!frame) return;
  if (frame.raf) cancelAnimationFrame(frame.id);
  else clearTimeout(frame.id);
}
const hidden = () => typeof document !== "undefined" && document.hidden;

export function observeMicrophoneActivity(stream: MediaStream, report: ActivityReporter): () => void {
  let active = true, context: AudioContext | undefined;
  let source: MediaStreamAudioSourceNode | undefined, analyser: AnalyserNode | undefined, frame: Frame | undefined;
  const filter = createActivityFilter();
  const stop = () => {
    if (!active) return;
    active = false; cancelFrame(frame);
    if (typeof document !== "undefined") document.removeEventListener("visibilitychange", visibility);
    try { source?.disconnect(); analyser?.disconnect(); } catch { /* Optional observer. */ }
    if (context && context.state !== "closed") void context.close().catch(() => {});
    report(null, "unavailable");
  };
  const visibility = () => {
    cancelFrame(frame); frame = undefined; filter.reset(); report(0, "microphone");
    if (!hidden() && active) frame = requestFrame(sample);
  };
  let samples: Float32Array<ArrayBuffer>;
  const sample = (now: number) => {
    frame = undefined;
    if (!active || hidden()) return;
    try {
      const tracks = stream.getAudioTracks?.() ?? stream.getTracks();
      if (tracks.every(track => track.enabled === false || track.muted || track.readyState === "ended")) {
        filter.reset(); report(0, "microphone");
      } else if (context?.state === "running") {
        analyser!.getFloatTimeDomainData(samples);
        report(filter.sample(activityFromSamples(samples), now), "microphone");
      } else { filter.reset(); report(null, "unavailable"); }
    } catch { stop(); return; }
    if (active) frame = requestFrame(sample);
  };
  try {
    if (!globalThis.AudioContext) { report(null, "unavailable"); return stop; }
    context = new AudioContext({ latencyHint: "interactive" });
    source = context.createMediaStreamSource(stream);
    analyser = context.createAnalyser(); analyser.fftSize = 512;
    samples = new Float32Array(analyser.fftSize);
    source.connect(analyser); // Never connect microphone audio to speakers.
    void context.resume().catch(() => {});
    if (typeof document !== "undefined") document.addEventListener("visibilitychange", visibility);
    sample(performance.now());
  } catch { stop(); }
  return stop;
}

export function observePlaybackActivity(audio: HTMLAudioElement, blob: Blob, report: ActivityReporter): () => void {
  type CapturableAudio = HTMLAudioElement & { captureStream?: () => MediaStream };
  let active = true, playing = false, captureAttempted = false, decodeStarted = false, decodeFailed = false;
  let context: AudioContext | undefined, decoded: Float32Array<ArrayBufferLike>[] | undefined, sampleRate = 0;
  let captured: MediaStream | undefined, source: MediaStreamAudioSourceNode | undefined, analyser: AnalyserNode | undefined;
  let samples: Float32Array<ArrayBuffer> | undefined, frame: Frame | undefined;
  const filter = createActivityFilter();
  const getContext = () => context ??= new AudioContext({ latencyHint: "interactive" });
  const decode = () => {
    if (decodeStarted || !active) return;
    decodeStarted = true;
    void (async () => {
      try {
        const data = await blob.arrayBuffer(); if (!active) return;
        // Offline decoding needs no output device/resume permission and avoids
        // captureStream's measured buffering delay. This never gates audio.play().
        const decoder = globalThis.OfflineAudioContext
          ? new OfflineAudioContext(1, 1, 16000) : getContext();
        const buffer = await decoder.decodeAudioData(data); if (!active) return;
        sampleRate = buffer.sampleRate;
        decoded = Array.from({ length: buffer.numberOfChannels }, (_, channel) => buffer.getChannelData(channel));
      } catch {
        decodeFailed = true;
        if (active) {
          report(null, "unavailable");
          if (playing && typeof (audio as CapturableAudio).captureStream === "function") void capture();
        }
      }
    })();
  };
  const capture = async () => {
    if (captureAttempted || !active) return;
    captureAttempted = true;
    try {
      const ctx = getContext();
      if (ctx.state !== "running") decode();
      await ctx.resume();
      if (!active) return;
      if (ctx.state !== "running") { decode(); return; }
      captured = (audio as CapturableAudio).captureStream!();
      if (!captured.getAudioTracks().length) { decode(); return; }
      source = ctx.createMediaStreamSource(captured);
      analyser = ctx.createAnalyser(); analyser.fftSize = 512;
      samples = new Float32Array(analyser.fftSize);
      source.connect(analyser); // Read a captured copy; native playback is untouched.
      if (playing && !frame && !hidden()) frame = requestFrame(sample);
    } catch { decode(); }
  };
  const halt = () => {
    playing = false; cancelFrame(frame); frame = undefined; filter.reset(); report(0);
  };
  const sample = (now: number) => {
    frame = undefined;
    if (!active || !playing || hidden()) return;
    if (audio.paused || audio.ended || audio.seeking || audio.readyState < 3 || audio.muted || audio.volume === 0) {
      filter.reset(); report(0);
    } else {
      try {
        if (decoded) {
          // A causal 12ms window anchored to the media clock. No future samples,
          // advancing timers, or whole-file 80ms quantization that can lead speech.
          const end = Math.min(decoded[0].length, Math.floor(audio.currentTime * sampleRate));
          const start = Math.max(0, end - Math.ceil(sampleRate * 0.012));
          const raw = Math.max(...decoded.map(channel => activityFromSamples(channel.subarray(start, end))));
          report(filter.sample(raw, now), "playback-pcm");
        } else if (analyser && samples && context?.state === "running") {
          analyser.getFloatTimeDomainData(samples);
          report(filter.sample(activityFromSamples(samples), now), "playback-capture");
        } else {
          report(null, "unavailable");
          if (decodeFailed && !analyser) return;
        }
      } catch {
        try { source?.disconnect(); } catch { /* Optional observer. */ }
        analyser = undefined; filter.reset(); report(null, "unavailable"); decode();
      }
    }
    if (active && playing) frame = requestFrame(sample);
  };
  const start = () => {
    if (!active) return;
    playing = true;
    decode();
    if (decodeFailed && typeof (audio as CapturableAudio).captureStream === "function") void capture();
    if (!frame && !hidden()) frame = requestFrame(sample);
  };
  const visibility = () => { cancelFrame(frame); frame = undefined; filter.reset(); report(0); if (!hidden() && playing && active) frame = requestFrame(sample); };
  const stopEvents = ["pause", "waiting", "seeking", "ended", "error", "emptied"] as const;
  const stop = () => {
    if (!active) return;
    active = false; halt();
    audio.removeEventListener("playing", start);
    for (const event of stopEvents) audio.removeEventListener(event, halt);
    if (typeof document !== "undefined") document.removeEventListener("visibilitychange", visibility);
    try { source?.disconnect(); analyser?.disconnect(); } catch { /* Optional observer. */ }
    captured?.getTracks().forEach(track => track.stop()); // Only the observer's copy.
    if (context && context.state !== "closed") void context.close().catch(() => {});
    report(null, "unavailable");
  };
  if ((!globalThis.AudioContext && !globalThis.OfflineAudioContext) || typeof audio.addEventListener !== "function") { report(null, "unavailable"); return () => {}; }
  audio.addEventListener("playing", start);
  for (const event of stopEvents) audio.addEventListener(event, halt);
  if (typeof document !== "undefined") document.addEventListener("visibilitychange", visibility);
  decode();
  // Attaching during established playback is supported; onplay alone is not enough.
  if (!audio.paused && audio.readyState >= 3) start();
  else report(null, "unavailable");
  return stop;
}
