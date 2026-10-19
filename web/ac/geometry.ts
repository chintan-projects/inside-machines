/** Small, pure isometric geometry. Units are drawing units, never appliance measurements. */
export type Point = readonly [number, number, number];
export type Flat = readonly [number, number];
export interface Origin {
  readonly x: number;
  readonly y: number;
}
export const INDOOR: Origin = { x: 215, y: 330 };
export const OUTDOOR: Origin = { x: 720, y: 410 };
export function project([x, y, z]: Point, origin: Origin): Flat {
  return [origin.x + (x - y) * 0.86, origin.y + (x + y) * 0.43 - z];
}
export function path(points: readonly Flat[], closed = false): string {
  return (
    points.map(([x, y], i) => `${i ? "L" : "M"}${x.toFixed(2)},${y.toFixed(2)}`).join(" ") +
    (closed ? "Z" : "")
  );
}
export function wire(points: readonly Point[], origin: Origin): string {
  return path(points.map((p) => project(p, origin)));
}
export interface BoxGeometry {
  readonly top: string;
  readonly front: string;
  readonly side: string;
}
export function box(at: Point, size: Point, origin: Origin): BoxGeometry {
  const [x, y, z] = at,
    [w, d, h] = size;
  const face = (points: Point[]): string =>
    path(
      points.map((p) => project(p, origin)),
      true,
    );
  return {
    top: face([
      [x, y, z + h],
      [x + w, y, z + h],
      [x + w, y + d, z + h],
      [x, y + d, z + h],
    ]),
    front: face([
      [x, y + d, z],
      [x + w, y + d, z],
      [x + w, y + d, z + h],
      [x, y + d, z + h],
    ]),
    side: face([
      [x + w, y, z],
      [x + w, y + d, z],
      [x + w, y + d, z + h],
      [x + w, y, z + h],
    ]),
  };
}
export function ring(cx: number, cy: number, r: number, z: number, origin: Origin): string {
  return path(
    Array.from({ length: 49 }, (_, i) =>
      project([cx + r * Math.cos((i * Math.PI) / 24), cy + r * Math.sin((i * Math.PI) / 24), z], origin),
    ),
    true,
  );
}
