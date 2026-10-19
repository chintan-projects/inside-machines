import type { LessonSpec } from "./contracts";

export function duration(spec: LessonSpec): number {
  return spec.stages.reduce((n, s) => n + s.duration, 0);
}
export function stageAt(spec: LessonSpec, seconds: number): [number, number] {
  let elapsed = 0;
  for (let i = 0; i < spec.stages.length; i++) {
    const stage = spec.stages[i];
    if (seconds < elapsed + stage.duration || i === spec.stages.length - 1)
      return [i, Math.max(0, Math.min(1, (seconds - elapsed) / stage.duration))];
    elapsed += stage.duration;
  }
  return [0, 0];
}

interface MediaClockSnapshot {
  readonly paused: boolean;
  readonly readyState: number;
  readonly currentTime: number;
}
/** Canceled/undecoded media cannot rewind a manually selected chapter. */
export function playingMediaTime(media: MediaClockSnapshot): number | null {
  // HTML media readyState 2 means the current frame has decoded data.
  if (media.paused || media.readyState < 2 || !Number.isFinite(media.currentTime) || media.currentTime < 0)
    return null;
  return media.currentTime;
}
