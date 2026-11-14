// Pure, deterministic mechanism rules shared by the interactive and the film.
// No DOM, no randomness, no network. Every number shown in either medium comes from here.
//
// Toy model (declared, illustrative): 2 layers, 2-number vectors, one attention head per layer,
// a ReLU feed-forward block per layer, greedy decoding over a 5-token vocabulary.
// It is NOT a real model; it exists so that "cache on" and "cache off" can be computed and compared.

export const PROMPT = ["The", "sky", "is"];
export const LAYER_COUNT = 2;
export const ANSWER_TOKEN_COUNT = 2; // blue, and

const EMBEDDINGS = {
  The: [1.0, 0.0],
  sky: [0.0, 1.0],
  is: [0.6, 0.4],
  blue: [-0.6, 0.9],
  clear: [0.4, 0.8],
  dark: [-0.2, -0.6],
  and: [0.9, -0.5],
  ".": [0.1, -0.9],
};

// Per-layer weights (2x2 matrices, row-major) — declared toy values.
const LAYERS = [
  {
    query: [[1.0, 0.5], [0.0, 1.0]],
    key: [[1.0, 0.0], [0.5, 1.0]],
    value: [[0.8, 0.0], [0.0, 0.8]],
    ffnIn: [[1.0, -1.0], [0.5, 1.0]],
    ffnOut: [[0.5, 0.0], [-0.5, 0.5]],
  },
  {
    query: [[0.5, 1.0], [1.0, 0.0]],
    key: [[1.0, 0.5], [0.0, 1.0]],
    value: [[0.0, 0.8], [0.8, 0.0]],
    ffnIn: [[0.5, 0.5], [-1.0, 1.0]],
    ffnOut: [[0.0, -0.5], [0.5, 0.0]],
  },
];

// Scoring direction per vocabulary token (declared toy values).
export const VOCABULARY = ["blue", "clear", "dark", "and", "."];
const UNEMBED = {
  blue: [0.6, 0.5],
  clear: [0.2, 0.5],
  dark: [-0.3, 0.2],
  and: [-0.5, 0.25],
  ".": [-0.3, 0.3],
};

const matVec = (m, v) => m.map((row) => row[0] * v[0] + row[1] * v[1]);
const add = (a, b) => a.map((x, i) => x + b[i]);
const dot = (a, b) => a.reduce((s, x, i) => s + x * b[i], 0);
const relu = (v) => v.map((x) => Math.max(0, x));
export const round = (x, digits = 2) => Math.round(x * 10 ** digits) / 10 ** digits;

/** Scaled dot-product attention with an explicit allow-list (C6). Pure. */
export function attend(query, keys, values, allowed) {
  if (!Array.isArray(query) || !query.length || query.some(x => !Number.isFinite(x))
    || !Array.isArray(keys) || !keys.length || keys.length !== values.length || keys.length !== allowed.length
    || keys.some(k => !Array.isArray(k) || k.length !== query.length || k.some(x => !Number.isFinite(x)))
    || values.some(v => !Array.isArray(v) || !v.length || v.length !== values[0].length || v.some(x => !Number.isFinite(x)))) {
    throw new RangeError("Attention needs finite matching vectors and an explicit mask.");
  }
  const scale = Math.sqrt(query.length);
  const scores = keys.map((k, i) => (allowed[i] ? dot(query, k) / scale : -Infinity));
  if (scores.some((score,i) => allowed[i] && !Number.isFinite(score))) throw new RangeError("Unmasked attention score is not finite.");
  const finite = scores.filter((s) => Number.isFinite(s));
  if (finite.length === 0) {
    return { valid: false, reason: "no_allowed_positions", scores, weights: scores.map(() => 0), output: null };
  }
  const max = Math.max(...finite);
  const exps = scores.map((s) => (Number.isFinite(s) ? Math.exp(s - max) : 0));
  const total = exps.reduce((a, b) => a + b, 0);
  const weights = exps.map((e) => e / total);
  const output = values.reduce((acc, v, i) => add(acc, v.map((x) => x * weights[i])), values[0].map(() => 0));
  return { valid: true, scores, weights, output };
}

/** The causal rule: a query at `position` may read keys at itself and earlier. */
export const causalAllowed = (position, count) => Array.from({ length: count }, (_, i) => i <= position);

/** Key and value of one position at one layer, from that position's input to the layer. */
function keyValue(layer, input) {
  return { key: matVec(LAYERS[layer].key, input), value: matVec(LAYERS[layer].value, input) };
}

/** One position through one layer, given the K/V of every allowed position at this layer (its own included). */
function layerStep(layer, input, kvs) {
  const weights = LAYERS[layer];
  const query = matVec(weights.query, input);
  const attention = attend(query, kvs.map((kv) => kv.key), kvs.map((kv) => kv.value), kvs.map(() => true));
  const mixed = add(input, attention.output);
  const hidden = matVec(weights.ffnIn, mixed);
  const activated = relu(hidden);
  const delta = matVec(weights.ffnOut, activated);
  const reworked = add(mixed, delta);
  const feedForward = {input: mixed, matrixIn: weights.ffnIn, hidden, activated, matrixOut: weights.ffnOut, delta, output: reworked};
  return { query, attention, mixed, feedForward, output: reworked };
}

/** Vocabulary scores from a final-layer vector; greedy rule picks the highest (ties: earlier vocabulary entry). */
export function scoreVocabulary(vector) {
  const list = VOCABULARY.map((token) => ({ token, score: dot(UNEMBED[token], vector) }));
  const pick = list.reduce((best, item) => (item.score > best.score ? item : best)).token;
  return { list, pick };
}

/**
 * Run the whole toy request: prefill of the prompt, then decode passes until ANSWER_TOKEN_COUNT tokens are picked.
 * `cache: true` reuses earlier positions' K/V; `cache: false` recomputes them from scratch on every decode pass.
 * Returns picks, per-pass work counts and the per-layer vectors needed by the depth views.
 */
export function runRequest({ cache = true, prompt = PROMPT, answerTokens = ANSWER_TOKEN_COUNT } = {}) {
  if (!Array.isArray(prompt) || !prompt.length || prompt.some(token => !Object.hasOwn(EMBEDDINGS,token))) {
    throw new RangeError("Use a nonempty prompt of known toy tokens.");
  }
  if (!Number.isSafeInteger(answerTokens) || answerTokens < 1 || answerTokens > 1000) {
    throw new RangeError("Answer choices must be an integer from 1 to 1000.");
  }
  const tokens = [...prompt];
  const passes = [];
  let store = Array.from({ length: LAYER_COUNT }, () => []); // store[layer][position] = {key, value}
  let lastTrace = null;
  const picks = [];

  const processPositions = (positions, label) => {
    const computed = Array.from({ length: LAYER_COUNT }, () => []);
    const reused = Array.from({ length: LAYER_COUNT }, () => []);
    if (!cache && label === "decode") {
      // Cache off: throw the stored K/V away and rebuild every earlier position as well.
      store = Array.from({ length: LAYER_COUNT }, () => []);
      positions = tokens.map((_, i) => i);
    }
    let inputs = positions.map((p) => EMBEDDINGS[tokens[p]]);
    const traces = positions.map(() => []);
    for (let layer = 0; layer < LAYER_COUNT; layer += 1) {
      // All listed positions derive their own K/V at this layer before any of them attends (same-layer rule).
      positions.forEach((p, i) => {
        store[layer][p] = keyValue(layer, inputs[i]);
        computed[layer].push(p);
      });
      const outputs = positions.map((p, i) => {
        const allowed = causalAllowed(p, tokens.length);
        const kvs = store[layer].filter((_, j) => allowed[j]);
        allowed.forEach((ok, j) => {
          if (ok && !positions.includes(j) && !reused[layer].includes(j)) reused[layer].push(j);
        });
        const step = layerStep(layer, inputs[i], kvs);
        traces[i].push({ layer, input: inputs[i], key: store[layer][p].key, value: store[layer][p].value, ...step });
        return step.output;
      });
      inputs = outputs;
    }
    const last = inputs[inputs.length - 1];
    const scores = scoreVocabulary(last);
    lastTrace = { position: positions[positions.length - 1], layers: traces[traces.length - 1], scores };
    passes.push({
      label,
      trace: lastTrace,
      positions: [...positions],
      newPosition: tokens.length - 1,
      computed: computed.reduce((s, l) => s + l.length, 0),
      reused: reused.reduce((s, l) => s + l.length, 0),
      computedByLayer: computed,
      reusedByLayer: reused,
      scores,
      kvLayer0: store[0].map((kv) => ({ key: [...kv.key], value: [...kv.value] })),
    });
    return scores.pick;
  };

  let pick = processPositions(tokens.map((_, i) => i), "prefill");
  picks.push(pick);
  while (picks.length < answerTokens) {
    tokens.push(pick); // the picked token becomes the next input only now
    pick = processPositions([tokens.length - 1], "decode");
    picks.push(pick);
  }
  return { cache, tokens, picks, passes, lastTrace, selections: picks.length, decodePasses: passes.length - 1 };
}

/**
 * Logical work for the batching view (C5, C7). Counts positions handled per pass; it says nothing about time,
 * GPU cores or which part limits speed on real hardware.
 */
export function laneWork({ requests = 1, promptLength = 3, answerTokens = 2 } = {}) {
  if ([requests,promptLength,answerTokens].some(n => !Number.isSafeInteger(n) || n < 1 || n > 1000)) {
    throw new RangeError("Logical counts must be positive integers up to 1000.");
  }
  const passes = [{ kind: "prefill", positions: requests * promptLength, perRequest: promptLength }];
  for (let i = 1; i < answerTokens; i += 1) passes.push({ kind: "decode", positions: requests, perRequest: 1 });
  return {
    passes,
    selections: requests * answerTokens,
    decodePasses: answerTokens - 1,
    firstPickFromPrefill: true,
  };
}

/** Layer-1 query, key and value of a token (layer 1's input is the token's own list of numbers). */
export function layerOneProjection(token) {
  const input = EMBEDDINGS[token];
  return { query: matVec(LAYERS[0].query, input), ...keyValue(0, input) };
}
