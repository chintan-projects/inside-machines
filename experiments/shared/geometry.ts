/** Shared normalized path geometry; no material, computation or provider rules. */
export type Point = readonly [number, number];
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

