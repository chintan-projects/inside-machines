import test from "node:test";
import assert from "node:assert/strict";
import { playingMediaTime } from "../web/lessonTimeline.ts";

test("late canceled-load events cannot rewind a manually selected chapter", () => {
  let selectedTime = 32.54;
  const events = [
    { paused: false, readyState: 0, currentTime: 0 },
    { paused: false, readyState: 1, currentTime: 0 },
    { paused: true, readyState: 4, currentTime: 0 },
  ];
  for (const event of events) selectedTime = playingMediaTime(event) ?? selectedTime;
  assert.equal(selectedTime, 32.54);
  selectedTime = playingMediaTime({ paused: false, readyState: 4, currentTime: 33.2 }) ?? selectedTime;
  assert.equal(selectedTime, 33.2);
});

test("valid startup is accepted while corrupt times cannot poison progress", () => {
  assert.equal(playingMediaTime({ paused: false, readyState: 2, currentTime: 0 }), 0);
  for (const currentTime of [NaN, Infinity, -1])
    assert.equal(playingMediaTime({ paused: false, readyState: 4, currentTime }), null);
});
