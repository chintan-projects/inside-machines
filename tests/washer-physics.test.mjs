import test from 'node:test';
import assert from 'node:assert/strict';
import { spinContact } from '../web/washer-physics.mjs';

test('fabric contact changes at the vertical-circle force-balance threshold', () => {
  assert.equal(spinContact(45).contact, false);
  assert.equal(spinContact(90).contact, true);
  const threshold = spinContact(0).criticalRpm;
  assert.equal(spinContact(threshold - .001).contact, false);
  assert.equal(spinContact(threshold + .001).contact, true);
  assert.equal(spinContact(0).normalPerKg, 0);
});
test('doubling speed needs four times the circular acceleration and radius changes the threshold', () => {
  assert.equal(spinContact(80).acceleration / spinContact(40).acceleration, 4);
  assert.ok(spinContact(60, .5).criticalRpm < spinContact(60, .25).criticalRpm);
  for (const value of [NaN, Infinity, -1]) assert.throws(() => spinContact(value), RangeError);
  assert.throws(() => spinContact(50, 0), RangeError);
});
