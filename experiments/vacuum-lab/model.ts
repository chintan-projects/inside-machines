import rawStory from './story.json';

export interface Beat {
  readonly id: string; readonly start: number; readonly duration: number;
  readonly title: string; readonly short: string; readonly explanation: string;
  readonly narration: string; readonly claims: readonly string[];
}
export interface Story {
  readonly version: string; readonly question: string; readonly scope: string;
  readonly width: number; readonly height: number; readonly fps: number;
  readonly beats: readonly Beat[];
  readonly experiment: { readonly duration: number; readonly title: string;
    readonly explanation: string; readonly narration: string; readonly claims: readonly string[] };
}
export interface FrameState {
  readonly time: number; readonly beat: number; readonly angle: number;
  readonly blocked: boolean; readonly air: readonly number[]; readonly dirt: readonly number[];
}
export type Point = readonly [number, number];
export const story: Story = rawStory;
export const duration = story.beats.reduce((sum, beat) => sum + beat.duration, 0);
export const ink = '#172432';
export const airInk = '#4267d5';
export const dirtInk = '#78513b';
export const paper = '#fbfcfe';

/** One qualitative rule shared by all local render adapters; no measured flow/RPM. */
export function stateAt(time: number, blocked = false): FrameState {
  if (!Number.isFinite(time) || time < 0) throw new Error('Invalid timeline time');
  let beat = story.beats.findLastIndex(item => time >= item.start);
  if (blocked) beat = 3;
  return {
    time, beat: Math.max(0, beat), angle: time * 140,
    blocked,
    air: blocked ? [] : Array.from({length: 12}, (_, i) => (i / 12 + time * 0.072) % 1),
    dirt: blocked ? [] : Array.from({length: 5}, (_, i) => (i / 5 + time * 0.105) % 1),
  };
}

/** Map normalized material progress onto adapter-owned geometry. */
export function pointAt(points: readonly Point[], progress: number): Point {
  if (points.length < 2 || !Number.isFinite(progress)) throw new Error('Invalid path');
  const lengths = points.slice(1).map((point, i) => Math.hypot(point[0] - points[i][0], point[1] - points[i][1]));
  let remaining = Math.max(0, Math.min(1, progress)) * lengths.reduce((sum, length) => sum + length, 0);
  for (let i = 0; i < lengths.length; i++) {
    if (remaining <= lengths[i] || i === lengths.length - 1) {
      const ratio = lengths[i] === 0 ? 0 : remaining / lengths[i];
      return [points[i][0] + (points[i + 1][0] - points[i][0]) * ratio,
        points[i][1] + (points[i + 1][1] - points[i][1]) * ratio];
    }
    remaining -= lengths[i];
  }
  return points[points.length - 1];
}

/** Fixed collection marks illustrate retained dirt without claiming filtration efficiency. */
export const retained: readonly Point[] = Array.from({length: 13}, (_, i) => [
  446 + (i % 5) * 14 + (Math.floor(i / 5) % 2) * 5,
  430 - Math.floor(i / 5) * 12,
]);
