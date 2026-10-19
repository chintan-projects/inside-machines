import { test } from 'node:test';
import assert from 'node:assert/strict';
import { sample, DURATION } from '../src/model.mjs';
test('cycle has bounded water, finite poses, interlocks, and no high-speed spin in standing water', () => {
  for (let t = 0; t <= DURATION; t += 0.025) {
    const s = sample(t);
    assert(s.water >= 0 && s.water <= 12.00001);
    assert(Number.isFinite(s.displayAngle));
    if (Math.abs(s.rpm) > 100) { assert.equal(s.water, 0); assert(s.pump); assert(s.doorLocked); }
    if (s.inlet) assert(!s.pump);
  }
});
test('drain completes before rinse and spin, and the completed machine stops', () => {
  assert.equal(sample(38).water, 0);
  assert.equal(sample(58).water, 0);
  assert.equal(sample(72).rpm, 0);
  assert.equal(sample(72).doorLocked, false);
  assert.equal(sample(72).complete, true);
});
test('scrubbing is deterministic, input clamps, and angle remains continuous at every boundary', () => {
  assert.deepEqual(sample(65), sample(65));
  assert.equal(sample(-1).t, 0);
  assert.equal(sample(999).t, 72);
  assert.equal(sample(NaN).t, 0);
  for (const t of [8, 30, 38, 43, 53, 58, 64, 69, 72]) {
    assert(Math.abs(sample(t - 1e-5).displayAngle - sample(t + 1e-5).displayAngle) < 0.001);
    assert(Math.abs(sample(t - 1e-5).laundryAngle - sample(t + 1e-5).laundryAngle) < 0.02);
  }
});
