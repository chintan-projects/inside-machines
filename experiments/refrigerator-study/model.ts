/** Qualitative refrigeration rules and a declared energy example, never an appliance simulator. */
import type { Controls, FrameState, NarrationPlan } from '../visual-studio/contracts.ts';
import { cueAt } from '../visual-studio/narration.ts';
import { refrigeratorCore, refrigeratorEnergy, refrigeratorPhase } from './narration.ts';
const bounded = (n: number, end: number): number => Math.max(0, Math.min(end, Number.isFinite(n) ? n : 0));
function frame(time: number, plan: NarrationPlan): FrameState {
  const t = bounded(time, plan.duration), cue = cueAt(plan, t);
  return { time: t, beatId: plan.id + '-' + cue.start, description: cue.text };
}
export interface ArtPose {
  readonly focus: 'whole' | 'inside' | 'compressor' | 'outside' | 'restrictor';
  readonly running: boolean;
  readonly progress: number;
  readonly piston: number;
  readonly intakeOpen: boolean;
  readonly outletOpen: boolean;
}
export interface CycleState extends FrameState, ArtPose {
  readonly kind: 'cycle';
  readonly view: 'overview' | 'evaporator' | 'compressor' | 'condenser' | 'capillary';
  readonly crankX: number;
  readonly crankY: number;
  readonly pistonPinY: number;
}
/** Intake enlarges the chamber; closed compression shrinks it; discharge follows. */
export function compressorPose(progress: number, running: boolean): Pick<CycleState,
  'piston' | 'intakeOpen' | 'outletOpen' | 'crankX' | 'crankY' | 'pistonPinY'> {
  const p = running ? bounded(progress, 1) : .25, theta = p * 2 * Math.PI;
  const crankX = 360 + 50 * Math.sin(theta), crankY = 460 - 50 * Math.cos(theta);
  const height = 50 * Math.cos(theta) + Math.sqrt(150 ** 2 - (50 * Math.sin(theta)) ** 2);
  return { piston: bounded((height - 100) / 100, 1), crankX, crankY, pistonPinY: 460 - height,
    intakeOpen: running && p > 0 && p < .48, outletOpen: running && p > .8 && p < 1 };
}
export function cycleStateAt(time: number, controls: Controls): CycleState {
  const f = frame(time, refrigeratorCore), t = f.time, running = controls.power !== 'off';
  const focus = t < 10 ? 'whole' : t < 34 ? 'inside' : t < 49 ? 'compressor' : t < 63 ? 'outside' : t < 77 ? 'restrictor' : 'whole';
  const progress = running ? (t % 3) / 3 : 0;
  return { ...f, kind: 'cycle', focus, running, progress, ...compressorPose(progress, running),
    view: focus === 'inside' ? 'evaporator' : focus === 'compressor' ? 'compressor' :
      focus === 'outside' ? 'condenser' : focus === 'restrictor' ? 'capillary' : 'overview',
    description: running ? f.description : 'The compressor is stopped. Sustained pumping stops; a real cold coil may still absorb heat briefly. This view omits that transient.' };
}
export interface EnergyBalance {
  readonly removed: number;
  readonly work: number;
  readonly released: number;
  /** Only same-reservoir comparison defines this net; closed-cabinet heat leakage is omitted. */
  readonly sameRoomNet: number | null;
}
/** 3+1=4 illustrative energy units, with no time scale or claimed coefficient of performance. */
export function energyBalance(open: boolean, running = true): EnergyBalance {
  const removed = running ? 3 : 0, work = running ? 1 : 0;
  return { removed, work, released: removed + work, sameRoomNet: open ? work : null };
}
export interface EnergyState extends FrameState {
  readonly kind: 'energy';
  readonly open: boolean;
  readonly showNumbers: boolean;
  readonly balance: EnergyBalance;
}
export function energyStateAt(time: number, controls: Controls): EnergyState {
  const f = frame(time, refrigeratorEnergy);
  const open = controls.door === 'open' || (controls.door !== 'closed' && f.time >= 24);
  return { ...f, kind: 'energy', open, showNumbers: f.time >= 10, balance: energyBalance(open),
    description: controls.door === 'closed' || controls.door === 'open'
      ? open ? 'Both sides exchange heat with the same room: 4 released minus 3 removed leaves 1 added. These are illustrative energy units.'
        : 'The cabinet loses 3 illustrative units while the warm side releases 4 into the room; 1 unit of work supplies the difference. Passive heat leaks are omitted.'
      : f.description };
}
export interface PhaseState extends FrameState {
  readonly kind: 'phase';
  readonly pressure: 'lower' | 'higher';
  readonly canBoil: boolean;
  readonly canAbsorbHeat: true;
}
/** Chosen fluid temperature is at the lower-P boiling point, below the higher-P one. No EOS/transient. */
export function phaseStateAt(time: number, controls: Controls): PhaseState {
  const f = frame(time, refrigeratorPhase);
  const pressure = controls.pressure === 'higher' || (controls.pressure !== 'lower' && f.time >= 24) ? 'higher' : 'lower';
  return { ...f, kind: 'phase', pressure, canBoil: pressure === 'lower', canAbsorbHeat: true,
    description: controls.pressure === 'lower' || controls.pressure === 'higher'
      ? pressure === 'lower' ? 'At the chosen cold temperature and lower pressure, liquid can boil while absorbing heat from warmer surroundings.'
        : 'At the same chosen cold temperature and higher pressure, this fluid stays liquid. It can still absorb heat and warm without boiling.'
      : f.description };
}
