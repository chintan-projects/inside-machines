/** Domain truth for complete pixel flow, data supply and exact matrix arithmetic. */
import type { Controls, FrameState, NarrationPlan } from '../visual-studio/contracts.ts';
import { cueAt } from '../visual-studio/narration.ts';
import { coreNarration, memoryNarration, matrixNarration } from './depth-narration.ts';
import { schedule, type Schedule } from './model.ts';

export const INPUT = Object.freeze([0, 1, 2, 3, 4, 5, 6, 7]);
const clamp = (n: number, end: number): number => Math.max(0, Math.min(end, Number.isFinite(n) ? n : 0));
function frame(time: number, plan: NarrationPlan): FrameState {
  const t = clamp(time, plan.duration), cue = cueAt(plan, t);
  return { time: t, beatId: `${plan.id}-${cue.start}`, description: cue.text };
}
export interface CoreState extends FrameState {
  readonly kind: 'core';
  readonly phase: 'board' | 'pixels' | 'program' | 'load' | 'compute' | 'result' | 'whole';
  readonly increment: 1 | 2;
  readonly schedule: Schedule;
  readonly results: readonly (number | null)[];
  readonly transferProgress: number;
}
/** Four illustrative slots; phase order teaches attention, not exclusive hardware timing. */
export function coreStateAt(time: number, controls: Controls): CoreState {
  const f = frame(time, coreNarration), t = f.time, increment = controls.add === '2' ? 2 : 1;
  const phase = t < 10 ? 'board' : t < 22 ? 'pixels' : t < 34 ? 'program' : t < 46 ? 'load' :
    t < 62 ? 'compute' : t < 74 ? 'result' : 'whole';
  const s = schedule('independent', 4, t >= 46, t >= 62 ? 2 : Math.max(0, (t - 46) / 8));
  const results = s.jobs.map(j => j.output === null ? null : (j.input ?? 0) + increment);
  const description = controls.add === '2' && t >= 46
    ? 'The instruction now adds 2. Each result follows from its original input; the pixel identities stay the same.' : f.description;
  return { ...f, description, kind: 'core', phase, increment, schedule: s, results,
    transferProgress: phase === 'program' ? clamp((t - 22) / 12, 1) : phase === 'load' ? clamp((t - 34) / 12, 1) : 0 };
}
export interface FeedState extends FrameState {
  readonly kind: 'memory';
  readonly supply: 1 | 4;
  readonly round: number;
  readonly rounds: number;
  readonly progress: number;
  readonly working: readonly number[];
  readonly results: readonly (number | null)[];
  readonly arrived: number;
}
/** Deliver inputs, then compute in each ideal round. Four slots are always available. */
export function feedStateAt(time: number, controls: Controls): FeedState {
  const f = frame(time, memoryNarration), t = f.time;
  const auto = controls.supply !== '1' && controls.supply !== '4';
  const supply = controls.supply === '4' || (auto && t >= 22) ? 4 : 1;
  const start = auto && t >= 22 ? 22 : 10, rounds = 8 / supply;
  const p = clamp((t - start) / 1.5, rounds), completed = Math.floor(p) * supply;
  const working = t < start || completed === 8 ? [] : Array.from({ length: supply }, (_, i) => completed + i);
  return { ...f, kind: 'memory', supply, round: Math.floor(p), rounds, progress: p % 1,
    working, arrived: completed + working.length, results: INPUT.map((n, i) => i < completed ? n + 1 : null),
    description: auto ? f.description : `${supply} ${supply === 1 ? 'input is' : 'inputs are'} supplied per ideal round. Four slots remain available; ${working.length} can work now. ${completed} results are ready.` };
}
export type Matrix = readonly [readonly [number, number], readonly [number, number]];
export const A: Matrix = [[1, 2], [3, 4]];
export const B: Matrix = [[2, 0], [1, 2]];
/** Exact mathematical model; operands are toy data, never real learned weights. */
export function multiply(a: Matrix, b: Matrix): Matrix {
  if ([...a.flat(), ...b.flat()].some(n => !Number.isFinite(n))) throw new Error('Nonfinite matrix operand');
  return [
    [a[0][0] * b[0][0] + a[0][1] * b[1][0], a[0][0] * b[0][1] + a[0][1] * b[1][1]],
    [a[1][0] * b[0][0] + a[1][1] * b[1][0], a[1][0] * b[0][1] + a[1][1] * b[1][1]],
  ];
}
export interface MatrixState extends FrameState {
  readonly kind: 'matrix';
  readonly a: Matrix;
  readonly b: Matrix;
  readonly result: Matrix;
  readonly row: number;
  readonly column: number;
  readonly left: readonly number[];
  readonly right: readonly number[];
  readonly products: readonly number[];
  readonly sum: number;
  readonly changed: boolean;
  readonly step: 'grids' | 'pair' | 'multiply' | 'sum' | 'outputs' | 'connect';
}
export function matrixStateAt(time: number, controls: Controls): MatrixState {
  const f = frame(time, matrixNarration), t = f.time, changed = controls.weight === 'changed';
  const b: Matrix = changed ? [[2, 1], [1, 2]] : B;
  const index = ['0', '1', '2', '3'].includes(controls.cell) ? Number(controls.cell) : 0;
  const row = Math.floor(index / 2), column = index % 2;
  const left = A[row], right = [b[0][column], b[1][column]], products = left.map((n, i) => n * right[i]);
  return { ...f, kind: 'matrix', a: A, b, result: multiply(A, b), row, column, left, right, products,
    sum: products.reduce((sum, n) => sum + n, 0), changed,
    step: t < 10 ? 'grids' : t < 22 ? 'pair' : t < 34 ? 'multiply' : t < 44 ? 'sum' : t < 58 ? 'outputs' : 'connect',
    description: controls.cell !== '0' || changed
      ? `Row ${row + 1}, column ${column + 1}: ${left[0]} × ${right[0]} + ${left[1]} × ${right[1]} = ${products[0]} + ${products[1]} = ${products[0] + products[1]}.${changed ? ' The changed weight affects output column 2.' : ''}` : f.description };
}
