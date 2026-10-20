import * as k from '../../vendor/anatomy/kit/iso-kit.mjs';
import * as G from '../../vendor/anatomy/kit/lathe.mjs';
import {tubePieces, tubeSvg} from '../../vendor/anatomy/kit/tube.mjs';

/** @typedef {import('./model.ts').FrameState} FrameState */
/** @typedef {readonly [number, number, number]} Point3 */
const W = 960, H = 720;
const P = k.fitProjection(k.boxCorners({x:-244,y:-55,w:410,d:150},0,125), W, H, {pad: 103, headroom: 5, azimuth: 55, elevation: 26});
const BODY = {x: -65, y: -45, w: 200, d: 90, r: 21};
const HOSE = [[-195, 65, 8], [-195, 65, 72], [-160, 65, 94], [-127, 65, 94], [-106, 32, 58], [-65, 0, 42]];
const at = (/** @type {number[]} */ point) => k.iso(point, P);
const S = (/** @type {ReturnType<typeof k.slabOf>} */ paths, /** @type {object} */ style = {}) => k.solidSvg(paths, style);
const L = (/** @type {string} */ path, /** @type {object} */ style = {}) => k.lineSvg(path, style);
const lathe = (/** @type {ReturnType<typeof G.frameAlong>} */ frame, /** @type {number[][]} */ profile) => G.lathe(profile, frame, P);
const disc = (/** @type {ReturnType<typeof G.frameAlong>} */ frame, /** @type {number} */ start, /** @type {number} */ radius, /** @type {number} */ length) => G.disc(start, start + length, radius, frame, P);
/** @param {number[]} center @param {number} r @param {string} fill @returns {string} */
const dot = (center, r, fill) => `<circle cx="${center[0]}" cy="${center[1]}" r="${r}" fill="${fill}"/>`;

/** Project a labeled anchor with a deliberately short leader; project override to Anatomy. */
function label(/** @type {string} */ text, /** @type {number[]} */ anchor, /** @type {number} */ x, /** @type {number} */ y) {
  const [ax, ay] = at(anchor);
  return `<path d="M${ax},${ay} L${x},${y + 12}" fill="none" stroke="#8796a5" stroke-width="1.8"/><circle cx="${ax}" cy="${ay}" r="3.5" fill="#172432"/><text x="${x}" y="${y}" text-anchor="middle" font-family="Arial,sans-serif" font-size="36" font-weight="500" fill="#172432" stroke="#fbfcfe" stroke-width="7" paint-order="stroke">${text}</text>`;
}

/** @returns {string} */
function body() {
  const out = [];
  out.push(`<path class="iso-halo" d="${k.haloOf(BODY, -3, 6, P)}"/>`);
  for (const x of [-30, 102]) {
    const F = G.frameAlong([x, 45, 11], [0, 1, 0]);
    out.push(S(lathe(F, [[0, 15], [5, 15], [7, 13]]), {tone: 'lo'}));
    out.push(S(disc(F, 7.2, 7, 2), {tone: 'mid'}));
  }
  out.push(S(k.slabOf(BODY, 15, 8, P, 12, 1.2), {tone: 'mid'}));
  // The rear wall and a low front sill expose the air chamber; no transparent solid.
  out.push(S(k.slabOf({x: -60, y: -43, w: 188, d: 8, r: 3}, 23, 69, P), {tone: 'mid'}));
  out.push(S(k.slabOf({x: 122, y: -38, w: 8, d: 75, r: 3}, 23, 69, P), {tone: 'mid'}));
  out.push(S(k.slabOf({x: -59, y: 34, w: 181, d: 8, r: 3}, 23, 10, P), {tone: 'mid'}));
  // Opened crown retains a recognizable rounded body and grounded handle fittings.
  out.push(S(k.slabOf({x: -54, y: -40, w: 174, d: 9, r: 3}, 92, 6, P), {tone: 'hi'}));
  for (const x of [-28, 47]) {
    out.push(S(k.slabOf({x, y: -35, w: 8, d: 8, r: 2}, 98, 14, P), {tone: 'mid'}));
  }
  out.push(S(k.slabOf({x: -28, y: -35, w: 83, d: 8, r: 3}, 112, 7, P), {tone: 'hi'}));
  for (const x of [-52, 115]) for (const y of [-35, 34]) {
    out.push(k.dotsSvg([at([x, y, 24])], {size: 1.1, tone: 'hi'}));
  }
  return out.join('');
}

/** @returns {string} */
function bag() {
  const out = [];
  const plan = {x: -43, y: -24, w: 64, d: 49, r: 7};
  out.push(S(k.slabOf(plan, 28, 52, P, 10, 1), {tone: 'hi'}));
  for (let x = -36; x < 19; x += 6) {
    out.push(L(k.segment([x, 25, 32], [x, 25, 75], P), {tone: 'faint'}));
  }
  out.push(S(k.slabOf({x: -47, y: -28, w: 72, d: 56, r: 7}, 79, 3, P), {tone: 'mid'}));
  const inlet = G.frameAlong([-65, 0, 42], [1, 0, 0]);
  out.push(S(lathe(inlet, [[0, 12], [5, 12], [6, 8], [23, 8]]), {tone: 'hi'}));
  // Dirt is visible at the cut bag face. It stays before the porous right wall.
  for (let i = 0; i < 12; i++) out.push(dot(at([-35 + (i % 4) * 12, 26, 35 + Math.floor(i / 4) * 6]), 3.2, '#78513b'));
  return out.join('');
}

/** @param {number} angle @returns {string} */
function motorFan(angle) {
  const out = [];
  const F = G.frameAlong([55, 0, 50], [1, 0, 0]);
  out.push(S(k.slabOf({x: 45, y: -17, w: 63, d: 34, r: 3}, 24, 6, P), {tone: 'mid'}));
  out.push(S(lathe(F, [[21, 17], [25, 19], [51, 19], [55, 16]]), {tone: 'hi'}));
  for (let x = 29; x < 51; x += 4) out.push(S(G.ringBand(x, x + 1, 19, 20, F, P), {tone: 'lo'}));
  out.push(S(lathe(F, [[0, 3], [26, 3]]), {tone: 'lo'}));
  out.push(S(disc(F, -2, 25, 2.2), {tone: 'mid'}));
  for (let i = 0; i < 8; i++) {
    const a = angle * Math.PI / 180 + i * Math.PI / 4;
    const points = [G.pointOf(F, -3, 6, a), G.pointOf(F, -3, 22, a + 0.28), G.pointOf(F, -3, 22, a + 0.52), G.pointOf(F, -3, 6, a + 0.35)];
    out.push(`<path d="${k.pathOf(points.map(p => at(p)), true)}" fill="#697f90" stroke="#293f50" stroke-width="1.1"/>`);
  }
  out.push(S(disc(F, -4, 6, 2), {tone: 'hi', lit: true}));
  // Outlet louvers are openings in the cut rear grille, not an external magic pipe.
  for (let z = 38; z < 73; z += 7) {
    out.push(S(k.slabOf({x: 130, y: -17, w: 8, d: 35, r: 2}, z, 2, P), {tone: 'mid'}));
  }
  return out.join('');
}

/** @param {FrameState} state @returns {string} */
export function anatomySvg(state) {
  const out = [body()];
  const hose = tubePieces(HOSE, 8, P, {rings: {step: 5, width: 0.55}, maxLength: 15});
  for (const piece of hose) out.push(tubeSvg(piece));
  const nozzle = {x: -224, y: 33, w: 57, d: 58, r: 5};
  out.push(S(k.slabOf(nozzle, 2, 8, P, 8, 1.2), {tone: 'hi'}));
  out.push(S(k.slabOf({x: -213, y: 39, w: 35, d: 12, r: 3}, 10, 10, P), {tone: 'mid'}));
  out.push(L(k.lineOnTop([-218, 90], [-173, 90], 4, P), {tone: 'hi'}));
  out.push(bag(), motorFan(state.angle));
  // The cutaway path is on the exposed passage centerline. Marker size is symbolic.
  const route = [[-237, 65, 4], ...HOSE, [-39, 0, 45], [5, 0, 50], [28, 0, 50], [48, 0, 50], [61, 0, 75], [111, 0, 75], [140, 0, 67], [164, 0, 67]];
  const poly = route.map(p => at(p));
  const path = k.pathOf(poly);
  out.push(`<path d="${path}" fill="none" stroke="#4267d5" stroke-width="3" opacity=".26"/>`);
  /** @param {number} t @returns {number[]} */
  function along(t, path = poly) {
    const lengths = path.slice(1).map((p, i) => Math.hypot(p[0] - path[i][0], p[1] - path[i][1]));
    let left = t * lengths.reduce((a, b) => a + b, 0);
    for (let i = 0; i < lengths.length; i++) {
      if (left <= lengths[i]) return [path[i][0] + (path[i + 1][0] - path[i][0]) * left / lengths[i], path[i][1] + (path[i + 1][1] - path[i][1]) * left / lengths[i]];
      left -= lengths[i];
    }
    return path[path.length - 1];
  }
  for (const t of state.air) out.push(dot(along(t), 5.5, '#4267d5'));
  for (const t of state.dirt) {
    const p = along(t, [...route.slice(0, 8), [-12, 15, 40]].map(p => at(p)));
    out.push(`<rect x="${p[0] - 4}" y="${p[1] + 7}" width="8" height="8" rx="1.5" fill="#78513b"/>`);
  }
  if (state.blocked) {
    const [x, y] = at([-225, 65, 8]);
    out.push(`<path d="M${x - 25},${y - 26} l50,50 M${x + 25},${y - 26} l-50,50" stroke="#a43e32" stroke-width="10" stroke-linecap="round"/>`);
  }
  out.push(label('Nozzle', [-205, 66, 8], 175, 570));
  out.push(label('Porous bag', [-8, 25, 62], 380, 200));
  out.push(label('Fan', [55, 0, 50], 690, 230));
  out.push(label('Motor', [96, 0, 50], 610, 590));
  out.push(label('Air out', [145, 0, 67], 810, 330));
  const title = ['The fan supplies the motion', 'Air takes a connected path', 'Dirt stays. Air passes through.', 'The whole air-moving machine'][state.beat];
  const heading = state.blocked ? 'A turning fan needs an open path' : title;
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" class="iso" data-theme="light"><style>${k.ISO_CSS}.iso{--anatomy-paper:#f2f5f8;--anatomy-top:#fafbfd;--anatomy-weight:1.1px}.iso-line{stroke-width:1.1px}</style><rect width="960" height="720" fill="#fbfcfe"/><text x="480" y="70" text-anchor="middle" font-family="Arial,sans-serif" font-size="32" fill="#526372">${heading}</text>${out.join('')}<text x="480" y="662" text-anchor="middle" font-family="Arial,sans-serif" font-size="26" fill="#667583">Cutaway · illustrative motion · bagged cleaner</text></svg>`;
  // resvg does not resolve CSS custom properties. Resolve the kit's actual light
  // tokens for export, preserving the same four-tone geometry and shading.
  const tokens = {paper:'#f2f5f8',face:'#ffffff',top:'#fafbfd','shade-0':'#c5d0dc','shade-1':'#d5dfe8',
    'shade-2':'#e3eaf1','shade-3':'#edf2f7','lit-top':'#ffffff','lit-shade':'#e8eef4',hi:'#293d50',
    mid:'#8194a6',lo:'#a9b7c4',faint:'#cdd7e0',lit:'#172432',halo:'#64778a','halo-opacity':'.2',
    dot:'#3a5268',weight:'1.1px',mono:'Arial,sans-serif'};
  return svg.replace('viewBox="0 0 960 720"','viewBox="90 130 800 600"')
    .replace(/var\(--anatomy-([a-z0-9-]+)\)/g, (match, name) => tokens[name] ?? match);
}
