/** Visual projection of existing causal state. No second cooling or piston model. */
import type { CycleState } from '../model.ts';
import type { Point } from './geometry.ts';
export { cycleStateAt, energyStateAt, phaseStateAt, energyBalance, compressorPose } from '../model.ts';
export function mechanismPoints(state:CycleState):{crank:Point;piston:Point} {
  return {crank:[state.crankX-360,0,460-state.crankY],piston:[0,0,460-state.pistonPinY]};
}
