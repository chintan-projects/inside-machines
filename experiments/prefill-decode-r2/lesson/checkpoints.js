// Checkpoint states shared by both media. Built only from runRequest() results, never hand-typed.
// Cell states: empty | processed | kv (processed, K/V shown) | new (K/V made this trip) | reused | rebuilt.
import { runRequest, PROMPT, LAYER_COUNT, round } from "./mechanism.js";

export const CHECKPOINT_IDS = ["cp_prompt", "cp_lookback", "cp_prefill", "cp_pick_blue", "cp_feed_blue",
  "cp_process_blue", "cp_pick_and", "cp_cache", "cp_close", "cp_transfer"];

const top = (scores, n = 3) =>
  [...scores.list].sort((a, b) => b.score - a.score).slice(0, n).map((s) => ({ token: s.token, score: round(s.score) }));

export function buildCheckpoint(id, { cache = true } = {}) {
  if (!CHECKPOINT_IDS.includes(id)) throw new Error(`unknown checkpoint ${id}`);
  // cp_transfer is the cache-off case by definition.
  const run = runRequest({ cache: id === "cp_transfer" ? false : cache });
  const [prefill, decode] = run.passes;
  const [first, second] = run.picks;
  const columns = PROMPT.map((token, i) => ({ token, role: "prompt", slot: "input", number: i + 1 }));
  const fill = (states) => Array.from({ length: LAYER_COUNT }, () => [...states]);
  let cells = fill(["empty", "empty", "empty"]);
  let arrows = null;
  let scores = null;
  let counts = null;
  const index = CHECKPOINT_IDS.indexOf(id);

  if (id === "cp_lookback") arrows = { layer: 0, from: 2, reads: [0, 1, 2], blocked: { layer: 1, from: 1, to: 2 } };
  if (id === "cp_prefill") {
    cells = fill(["new", "new", "new"]);
    counts = { made: prefill.computed, reused: prefill.reused };
  }
  if (index >= CHECKPOINT_IDS.indexOf("cp_pick_blue")) cells = fill(["kv", "kv", "kv"]);
  if (id === "cp_pick_blue") {
    scores = { column: 2, list: top(prefill.scores), pick: first };
    columns.push({ token: first, role: "answer", slot: "picked", number: 4 });
    cells.forEach((row) => row.push("empty"));
  }
  if (index >= CHECKPOINT_IDS.indexOf("cp_feed_blue")) {
    columns.push({ token: first, role: "answer", slot: "input", number: 4 });
    cells.forEach((row) => row.push(id === "cp_feed_blue" ? "empty" : "kv"));
  }
  if (["cp_process_blue", "cp_cache", "cp_transfer"].includes(id)) {
    const old = run.cache ? "reused" : "rebuilt";
    cells = Array.from({ length: LAYER_COUNT }, () => [old, old, old, "new"]);
    arrows = { layer: 0, from: 3, reads: [0, 1, 2, 3], blocked: null };
    counts = { made: decode.computed, reused: decode.reused };
  }
  if (index >= CHECKPOINT_IDS.indexOf("cp_pick_and")) {
    columns.push({ token: second, role: "answer", slot: "picked", number: 5 });
    cells.forEach((row) => row.push("empty"));
  }
  if (id === "cp_pick_and") scores = { column: 3, list: top(decode.scores), pick: second };

  return {
    id,
    cache: run.cache,
    columns,
    cells,
    arrows,
    scores,
    counts,
    picks: run.picks,
    selections: run.selections,
    decodePasses: run.decodePasses,
  };
}

/** Everything the film needs, for both cache settings. Written to video/production/shared/lesson_states.json. */
export function exportStates() {
  const on = runRequest({ cache: true });
  const off = runRequest({ cache: false });
  const states = {};
  for (const id of CHECKPOINT_IDS) {
    states[id] = { cache_on: buildCheckpoint(id, { cache: true }), cache_off: buildCheckpoint(id, { cache: false }) };
  }
  return {
    generated_by: "lesson/checkpoints.js exportStates()",
    prompt_inputs: PROMPT.map(token=>runRequest({prompt:[token],answerTokens:1}).passes[0].trace.layers[0].input),
    layer_example: on.passes[0].trace.layers[0],
    decode_example: on.passes[1].trace.layers[0],
    numeric_example: {token: "The", layer: 1, ...on.passes[0].kvLayer0[0]},
    layer_count: LAYER_COUNT,
    picks: on.picks,
    work: {
      prefill_made: on.passes[0].computed,
      decode_made_cache_on: on.passes[1].computed,
      decode_reused_cache_on: on.passes[1].reused,
      decode_made_cache_off: off.passes[1].computed,
    },
    states,
  };
}
