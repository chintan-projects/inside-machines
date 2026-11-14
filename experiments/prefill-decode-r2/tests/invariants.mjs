// node tests/invariants.mjs — mechanism, agreement and content checks. Exits non-zero on the first failure.
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { runRequest, attend, causalAllowed, laneWork, round, LAYER_COUNT } from "../lesson/mechanism.js";
import { buildCheckpoint, CHECKPOINT_IDS, exportStates } from "../lesson/checkpoints.js";
import { SCENES, PREDICTION, TRANSFER, INTENTS, matchIntent } from "../lesson/story.js";

const on = runRequest({ cache: true });
const off = runRequest({ cache: false });
let n = 0;
const ok = (name, fn) => { fn(); n += 1; console.log(`ok ${n} ${name}`); };

ok("running example picks blue then and", () => assert.deepEqual(on.picks, ["blue", "and"]));
ok("cache off picks the same tokens with identical scores (exact toy rules)", () => {
  assert.deepEqual(off.picks, on.picks);
  on.passes.forEach((p, i) => assert.deepEqual(off.passes[i].scores, p.scores));
});
ok("prefill makes K/V for every prompt position in every layer, reusing nothing", () => {
  assert.equal(on.passes[0].computed, 3 * LAYER_COUNT); assert.equal(on.passes[0].reused, 0);
});
ok("decode with cache makes only the new position's K/V and reads the old ones", () => {
  assert.equal(on.passes[1].computed, LAYER_COUNT); assert.equal(on.passes[1].reused, 3 * LAYER_COUNT);
});
ok("decode without cache rebuilds every earlier position's K/V", () => {
  assert.equal(off.passes[1].computed, 4 * LAYER_COUNT); assert.equal(off.passes[1].reused, 0);
});
ok("N picks = 1 from prefill + N-1 decode trips (C7)", () => {
  assert.equal(on.selections, 2); assert.equal(on.decodePasses, 1);
  const w = laneWork({ requests: 3, promptLength: 5, answerTokens: 4 });
  assert.equal(w.decodePasses, 3); assert.equal(w.selections, 12); assert.equal(w.passes[0].positions, 15);
  assert.ok(w.passes.slice(1).every((p) => p.positions === 3));
});
ok("attention weights sum to 1 and the causal mask gives later positions zero weight", () => {
  const keys = [[1, 0], [0, 1], [1, 1], [-1, 1]], values = [[1, 2], [3, 4], [5, 6], [7, 8]];
  const r = attend([0.5, 1], keys, values, causalAllowed(1, 4));
  assert.equal(round(r.weights.reduce((a, b) => a + b, 0), 9), 1);
  assert.equal(r.weights[2], 0); assert.equal(r.weights[3], 0);
  // hand-checked: scores 0.5/√2 and 1/√2 → weights 0.4125, 0.5875 (1/(1+e^0.3536)); output = 0.4125*[1,2] + 0.5875*[3,4]
  assert.equal(round(r.weights[0], 4), 0.4125);
  assert.deepEqual(r.output.map((x) => round(x, 3)), [2.175, 3.175]);
});
ok("the picked token has no K/V until it is processed", () => {
  const s = buildCheckpoint("cp_pick_blue");
  assert.equal(s.columns[3].slot, "picked");
  assert.ok(s.cells.every((row) => row[3] === "empty"));
  const and = buildCheckpoint("cp_cache");
  assert.equal(and.columns[4].slot, "picked");
  assert.ok(and.cells.every((row) => row[4] === "empty"));
});
ok("cache toggle changes only reused/rebuilt state, never the picks", () => {
  for (const id of CHECKPOINT_IDS) {
    const a = buildCheckpoint(id, { cache: true }), b = buildCheckpoint(id, { cache: false });
    assert.deepEqual(a.picks, b.picks);
    assert.deepEqual(a.columns, b.columns);
  }
  assert.equal(buildCheckpoint("cp_cache", { cache: true }).cells[0][0], "reused");
  assert.equal(buildCheckpoint("cp_cache", { cache: false }).cells[0][0], "rebuilt");
});

const beats = SCENES.flatMap((s) => s.beats);
const words = (t) => t.split(/\s+/).filter(Boolean).length;
ok("six scenes, unique ids, every beat on a known checkpoint, at most 32 words per beat", () => {
  assert.equal(SCENES.length, 6);
  const ids = [...SCENES.map((s) => s.id), ...beats.map((b) => b.id)];
  assert.equal(new Set(ids).size, ids.length);
  ids.forEach((id) => assert.match(id, /^[a-z][a-z0-9_]*$/));
  beats.forEach((b) => { assert.ok(CHECKPOINT_IDS.includes(b.checkpoint), b.id); assert.ok(words(b.narration) <= 32, b.id); });
});
ok("core narration stays below 800 words after audience fixes", () => {
  const total = beats.reduce((s, b) => s + words(b.narration), 0);
  console.log(`   narration words: ${total}`);
  assert.ok(total >= 500 && total <= 800, String(total));
});
ok("numbers written in the film visuals equal the computed toy numbers", () => {
  const states = exportStates();
  const fmtList = (cp) => states.states[cp].cache_on.scores.list.map((s) => s.score.toFixed(2));
  const visual = (id) => beats.find((b) => b.id === id).visual;
  fmtList("cp_pick_blue").forEach((v) => assert.ok(visual("fp_scores").includes(v), v));
  fmtList("cp_pick_and").forEach((v) => assert.ok(visual("fb_pick_and").includes(v), v));
  assert.ok(visual("kv_saves").includes(`made: ${states.work.decode_made_cache_on}`));
  assert.ok(visual("kv_saves").includes(`read from cache: ${states.work.decode_reused_cache_on}`));
  assert.ok(visual("cl_transfer_reveal").includes(`made: ${states.work.decode_made_cache_off} instead of ${states.work.decode_made_cache_on}`));
});
ok("prediction and transfer are tied to real checkpoints and beats", () => {
  assert.ok(CHECKPOINT_IDS.includes(PREDICTION.revealAtCheckpoint));
  assert.ok(beats.some((b) => b.id === TRANSFER.revealBeat && b.interactive === "reveal"));
  assert.deepEqual(TRANSFER.rubric.map((r) => r.score), [2, 1, 0]);
});
ok("known intents route to panels; unknown text is not matched", () => {
  assert.equal(matchIntent("show me the attention math").panel, "attention");
  assert.equal(matchIntent("What does the MLP do?").panel, "model");
  assert.equal(matchIntent("how does batching on a GPU work").panel, "insight");
  assert.equal(matchIntent("what if I turn the KV cache off").panel, "cache");
  assert.equal(matchIntent("who invented the transistor"), null);
  const panels = new Set(INTENTS.map((i) => i.panel));
  ["attention", "model", "insight", "cache", "transfer"].forEach((p) => assert.ok(panels.has(p)));
});
ok("built HTML is self-contained and current", () => {
  const html = readFileSync(new URL("../interactive/index.html", import.meta.url), "utf8");
  assert.ok(!/src=["']https?:/i.test(html), "remote media or script");
  assert.ok(!/\bfetch\(|XMLHttpRequest|WebSocket|localStorage|sessionStorage|indexedDB/.test(html), "network or storage API");
  SCENES.flatMap((s) => s.beats).forEach((b) => assert.ok(html.includes(`id: "${b.id}"`), `stale build: ${b.id}`));
});
ok("generated script.yaml matches the story", () => {
  const y = readFileSync(new URL("../video/production/episodes/ep01/script.yaml", import.meta.url), "utf8");
  beats.forEach((b) => assert.ok(y.includes(JSON.stringify(b.narration)), b.id));
});
ok("all masked attention is explicitly invalid; unequal key/value dimensions remain valid", () => {
  assert.equal(attend([1,0],[[1,0]],[[1,2,3]],[false]).valid,false);
  assert.deepEqual(attend([1,0],[[1,0]],[[1,2,3]],[true]).output,[1,2,3]);
  assert.throws(()=>attend([1e308,1e308],[[1e308,1e308]],[[1,2]],[true]),RangeError);
});
ok("six-token assessment is distinct from the narrated worked case",()=>{
  const prompt=["The","sky","is","The","sky","is"];
  assert.equal(runRequest({prompt,cache:false}).passes[1].computed,14);
  assert.equal(runRequest({prompt,cache:true}).passes[1].computed,2);
  assert.match(TRANSFER.prompt,/SIX/);
  assert.ok(!beats.some(b=>b.narration.includes("six prompt")));
});
ok("literal dive deeper routes to a prepared model view",()=>assert.equal(matchIntent("dive deeper").panel,"model"));
console.log(`all ${n} invariants hold`);
