// Teaching model, not a manufacturer's cycle or a hydraulic simulation.
// Seconds represent a condensed lesson. Volumes and RPM are illustrative.
export const DURATION = 72;
export const STAGES = [
  { start: 0, end: 8, name: 'Fill', title: 'Let a little water in.', text: 'An inlet valve opens. Water passes through the detergent drawer into the outer tub. The clothes do not need to be completely submerged.', part: 'inlet', why: 'The outer tub holds water. The perforated inner drum holds the clothes.' },
  { start: 8, end: 30, name: 'Tumble', title: 'Lift. Drop. Repeat.', text: 'The motor turns the drum slowly, reversing direction. Lifters carry the clothes up; gravity drops them through the wash water. Detergent and movement loosen dirt.', part: 'drum', why: 'Slow rotation lets clothes fall. Spinning too fast would pin them to the wall.' },
  { start: 30, end: 38, name: 'Drain', title: 'Give dirty water a way out.', text: 'The drain pump moves used water from the bottom of the outer tub into the drain hose. The drum stays in place while the water leaves.', part: 'pump', why: 'Water moves through holes in the inner drum into the watertight outer tub.' },
  { start: 38, end: 58, name: 'Rinse', title: 'Fresh water takes the soap away.', text: 'The valve admits clean water, the drum tumbles the clothes, and the pump drains again. This simplified lesson shows one rinse; real cycles may repeat it.', part: 'inlet', why: 'Rinsing replaces soapy water with clean water, then carries the diluted detergent away.' },
  { start: 58, end: 72, name: 'Spin', title: 'The water leaves. The clothes stay.', text: 'The motor accelerates the drum. The wall keeps the clothes moving in a circle. Water passes through the perforations into the outer tub and is pumped away.', part: 'drum', why: 'The drum supplies the inward force for circular motion. Water that escapes a hole continues into the outer tub.' }
];
const clamp = (n, a, b) => Math.max(a, Math.min(b, n));
const ease = n => n * n * (3 - 2 * n);
export function sample(input) {
  const t = clamp(Number.isFinite(input) ? input : 0, 0, DURATION);
  const index = STAGES.findIndex(s => t < s.end);
  const stageIndex = index < 0 ? 4 : index;
  let water = 0, rpm = 0, inlet = false, pump = false;
  if (t < 8) { water = 12 * t / 8; inlet = true; }
  else if (t < 30) { water = 12; rpm = 48 * Math.sin((t - 8) * Math.PI / 5); }
  else if (t < 38) { water = 12 * (38 - t) / 8; pump = true; }
  else if (t < 43) { water = 12 * (t - 38) / 5; inlet = true; }
  else if (t < 53) { water = 12; rpm = 48 * Math.sin((t - 43) * Math.PI / 5); }
  else if (t < 58) { water = 12 * (58 - t) / 5; pump = true; }
  else if (t < 72) { rpm = 1000 * ease(clamp((t - 58) / 6, 0, 1)) * ease(clamp((72 - t) / 3, 0, 1)); pump = true; }
  // Integrated RPM gives physical angle; drawing labels its 4× / 60× slowdown.
  // Integrate deterministically so scrubbing gives exactly the same pose as playback.
  let integral = 0;
  if (t > 8) { const d = Math.min(t, 30) - 8; integral += 48 * 5 / Math.PI * (1 - Math.cos(d * Math.PI / 5)); }
  if (t > 43) { const d = Math.min(t, 53) - 43; integral += 48 * 5 / Math.PI * (1 - Math.cos(d * Math.PI / 5)); }
  const tumbleIntegral = integral;
  let spinIntegral = 0;
  if (t > 58) {
    const d = t - 58;
    if (d <= 6) { const x = d / 6; spinIntegral = 6000 * (x ** 3 - x ** 4 / 2); }
    else if (d <= 11) spinIntegral = 3000 + 1000 * (d - 6);
    else { const x = (d - 11) / 3; spinIntegral = 8000 + 3000 * (x - x ** 3 + x ** 4 / 2); }
    integral += spinIntegral;
  }
  const displayAngle = tumbleIntegral * Math.PI / 120 + spinIntegral * Math.PI / 1800;
  const tumbleAtSpin = 48 * 5 / Math.PI * (1 - Math.cos(22 * Math.PI / 5));
  const spinStartAngle = tumbleAtSpin * Math.PI / 120;
  const laundryAngle = t < 58 ? 65 * Math.sin(displayAngle) :
    65 * Math.sin(spinStartAngle) + (displayAngle - spinStartAngle) * 180 / Math.PI;
  return { t, stageIndex, water: Math.max(0, water), rpm, inlet, pump,
    doorLocked: t < DURATION, complete: t === DURATION,
    physicalAngle: integral * Math.PI / 30,
    displayAngle, laundryAngle,
    rotationScale: stageIndex === 4 ? 60 : 4,
    stage: STAGES[stageIndex] };
}
