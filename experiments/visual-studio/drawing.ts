/** Small trusted vector primitives for mathematical/information views, not domain rules. */
export const ink = '#292924', paper = '#fffdf5', teal = '#286b65', rust = '#a74325';
export const escape = (s: string | number): string => String(s).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
export function text(x: number, y: number, value: string | number, size = 30, fill = ink, anchor = 'middle'): string {
  return `<text x="${x}" y="${y}" text-anchor="${anchor}" fill="${fill}" font-family="Georgia,serif" font-size="${size}">${escape(value)}</text>`;
}
export function box(x: number, y: number, w: number, h: number, fill = paper, stroke = '#a9afa3', radius = 10): string {
  return `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${radius}" fill="${fill}" stroke="${stroke}" stroke-width="2"/>`;
}
export function arrow(points: string, color = teal): string {
  return `<path d="${points}" fill="none" stroke="${color}" stroke-width="3" marker-end="url(#flow-head)"/>`;
}
export function figure(content: string): string {
  return `<defs><marker id="flow-head" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="context-stroke"/></marker></defs>${content}`;
}
/** A declared toy brightness mapping; text carries the number independently of shade. */
export function pixel(x: number, y: number, size: number, value: number | null, label = ''): string {
  const shade = value === null ? 247 : Math.round(235 - value * 20);
  const color = value !== null && value >= 6 ? paper : '#171712';
  return box(x, y, size, size, `rgb(${shade},${shade},${shade})`, '#9ba398', 7) +
    (label ? text(x + size / 2, y + 30, label, 28, color) : '') +
    text(x + size / 2, y + (label ? size - 12 : size / 2 + 12), value ?? '·', label ? 30 : 38, color);
}
export function pixelRow(values: readonly (number | null)[], y: number): string {
  return values.map((value, i) => pixel(48 + i * 78, y, 66, value, 'ABCDEFGH'[i])).join('');
}
export function picture(values: readonly (number | null)[], y: number, size = 78): string {
  const width = 4 * (size + 8) - 8, x = (720 - width) / 2;
  return values.map((value, i) => pixel(x + i % 4 * (size + 8), y + Math.floor(i / 4) * (size + 8), size, value)).join('');
}
