// Canonical story: one source for the film script (script.yaml is generated from it), the interactive captions,
// the prediction, the transfer check and the local "dive deeper" intents. Scene and beat ids are stable.
// Each beat names the checkpoint (lesson/checkpoints.js) whose state both media show while the line is said.

export const EPISODE = {
  id: "ep01",
  question: "Why can a language model read the prompt together but must build its answer one token at a time?",
  takeaway:
    "The prompt's tokens are all known, so their positions go through each layer together; an answer token does not " +
    "exist until it is picked, and the next pick needs it processed first, so the answer grows one token per trip. " +
    "The KV cache only spares rebuilding earlier positions' keys and values.",
  taughtTerms: ["token", "position", "layer", "causal mask", "attention", "feed-forward network", "decoding rule",
    "key", "value", "query", "KV cache", "prefill", "decode"],
};

const q = (word) => `“${word}”`;

export const SCENES = [
  {
    id: "hook",
    title: "A prompt read at once, an answer written piece by piece",
    purpose: "Start from the stream the viewer has seen, ask the main question, and get a prediction before any mechanism.",
    beats: [
      { id: "hook_stream", checkpoint: "cp_prompt",
        narration: `Type ${q("The sky is")} into a chatbot, and the answer arrives a piece at a time: ${q("blue")}, then ${q("and")}, then more.`,
        visual: "Three blue chips “The”, “sky”, “is” fade in left of centre; gold chips “blue” and “and” appear to their right one after the other, then a grey ellipsis." },
      { id: "hook_question", checkpoint: "cp_prompt",
        narration: "The prompt you typed is read in one go. The answer is written one piece at a time. Why the difference?",
        visual: "A blue brace under the three prompt chips labelled “read together”; a gold brace under “blue” and “and” labelled “one at a time”." },
      { id: "hook_guess", checkpoint: "cp_prompt", pause: 2.5,
        narration: "Guess first. The chip running the model, the GPU, does thousands of calculations at once. Could it choose two answer pieces together?",
        visual: "The gold chips and the braces fade; two dashed empty slots marked “?” stand where they were, under the line “Both in one trip?”, through the pause." },
      { id: "hook_follow", checkpoint: "cp_prompt",
        narration: "Let's follow one request through the model.",
        visual: "The question and the empty slots fade; the three prompt chips glide to the bottom of the frame." },
    ],
  },
  {
    id: "known_positions",
    title: "Known positions go through each layer together",
    purpose: "Build tokens, positions and layers, with the causal look-back and the two jobs of a layer, so prefill of known positions looks inevitable.",
    beats: [
      { id: "kp_tokens", checkpoint: "cp_prompt",
        narration: "Text is cut into small pieces, called tokens. Here each word is one piece. We number their positions: one, two, three.",
        visual: "The three blue chips sit along the bottom with the numbers 1, 2, 3 beneath them; a small grey note at the bottom right reads “token pieces are illustrative”." },
      { id: "kp_numbers", checkpoint: "cp_prompt",
        narration: "Each token becomes a list of numbers. All three lists can be made at once, because all three tokens are known.",
        visual: "Above each chip, a small blue row of two squares (the list of numbers) appears; all three appear at the same moment." },
      { id: "kp_layers", checkpoint: "cp_prompt",
        narration: "A layer transforms these number lists. Its outputs become the next layer's inputs. We draw two layers; real models have many more.",
        visual: "On the right, show is input [0.60, 0.40] entering one transform and yielding [1.26, 1.16], its real layer-one result. Two rows on the left then locate repeated transformations as layer 1 and layer 2." },
      { id: "kp_lookback", checkpoint: "cp_lookback",
        narration: "Within a layer, is can read the input lists for The, sky and itself. Sky cannot read is. This no-looking-ahead rule is the causal mask.",
        visual: "Arrows rise from the three known INPUT lists into the is output of layer 1. A dashed red connection from is INPUT to sky OUTPUT is blocked. No arrows link freshly computed neighboring outputs." },
      { id: "kp_two_jobs", checkpoint: "cp_prefill",
        narration: "First, mix context from allowed inputs into each position. That operation is attention. Watch is change from its input to this new result.",
        visual: "A numeric inset follows is in layer 1: input [0.60, 0.40] → after the attention block [1.08, 0.72]. The feed-forward result stays hidden until kp_ffn. Values come from the shared computation." },
      { id: "kp_ffn", checkpoint: "cp_prefill",
        narration: "Next, rework each position's numbers independently. This second operation is a feed-forward network. Its completed result becomes that position's input to the next layer.",
        visual: "The numeric inset reveals after feed-forward block [1.26, 1.16]. The prior attention block [1.08, 0.72] stays visible; each block includes carrying its input forward, detailed in the model view." },
      { id: "kp_together", checkpoint: "cp_prefill", pause: 1.2,
        narration: "Layer one’s three input lists are known, so its positions run together. Once those outputs are ready, layer two processes them together.",
        visual: "All three layer-1 cells light yellow at the same moment and turn solid; then all three layer-2 cells do the same. The line “known → processed together” stays at the top through the pause." },
      { id: "kp_prefill_name", checkpoint: "cp_prefill", pause: 0.5,
        narration: "That prompt-processing pass is called prefill. Its last position supplies the first answer choice.",
        visual: "A blue label Prefill: process the known prompt appears above the completed prompt columns." },
    ],
  },
  {
    id: "first_pick",
    title: "The last position's scores pick the first answer token",
    purpose: "Show that only the last position's scores choose the next token, and that the picked token is not yet processed, which answers the guess.",
    beats: [
      { id: "fp_scores", checkpoint: "cp_pick_blue",
        narration: "The last prompt position, is, produces scores for possible next tokens. These numbers are computed by our small illustrative model, not measured from a real chatbot.",
        visual: "The processed grid from before. An arrow rises from the top “is” cell to a score list with bars: blue 3.00, clear 2.04, “.” 0.21, captioned “toy scores”." },
      { id: "fp_pick", checkpoint: "cp_pick_blue",
        narration: "Take the highest score: blue. This simplest way to choose is called greedy decoding. Real chatbots can use other selection rules.",
        visual: "The “blue” bar turns yellow; a gold chip “blue” appears next to the score list." },
      { id: "fp_not_processed", checkpoint: "cp_pick_blue",
        narration: `Look where ${q("blue")} is now. It has been picked, but no layer has processed it. Position four is still empty.`,
        visual: "A fourth column of dashed empty cells appears to the right with an empty input slot numbered 4; the gold “blue” chip waits above it, outside the stack, labelled “picked, not processed”." },
      { id: "fp_next_only", checkpoint: "cp_pick_blue",
        narration: "An ordinary causal model is trained to score the immediate next token from each position. It has no second-answer output here.",
        visual: "A table labels the slots scored by the three prompt positions: The → slot 2 (already known), sky → slot 3 (already known), is → slot 4 (next answer). These are target slots, not claims about what the toy predicts for earlier positions." },
      { id: "fp_settle", checkpoint: "cp_pick_blue",
        narration: `So the token after ${q("blue")} is scored by position four. But position four needs ${q("blue")} as its input, and ${q("blue")} only exists after this pick.`,
        visual: "The score list and label fade. A dashed fifth slot with “?” appears to the right; a grey arrow runs from the “blue” chip to it, labelled “needs position 4 first”." },
      { id: "fp_conclusion", checkpoint: "cp_pick_blue", pause: 1.2,
        narration: "One pass through every layer, followed by choosing a token, is one trip. In this ordinary model, it picks one new token.",
        visual: "The line “one trip → one new token” appears at the top and stays through the pause." },
    ],
  },
  {
    id: "feed_back",
    title: "The picked token goes back in and reuses saved results",
    purpose: "Feed the picked token back as the next input; show the numeric intermediate results kept by earlier positions; get the second token from position four.",
    beats: [
      { id: "fb_input", checkpoint: "cp_feed_blue",
        narration: `To be scored from, position four must be computed. So ${q("blue")} goes back in, as the input at position four.`,
        visual: "The gold “blue” chip travels along a curved arrow from the top down into the input slot at position 4." },
      { id: "fb_kv", checkpoint: "cp_feed_blue",
        narration: "Now reuse the prompt's work. Each layer made two extra lists from its inputs while processing each position. We saved those lists.",
        visual: "Six earlier cells gain two small unlabeled bars, showing the extra saved lists; these are separate intermediate state made from the layer inputs. A numeric spotlight for The/layer 1 shows [1.00, 0.50] and [0.80, 0.00]; names appear only during fb_value." },
      { id: "fb_value", checkpoint: "cp_feed_blue",
        narration: "Keys are compared to decide the mix. Values are the numbers being mixed. This pair is called a key and value, or K and V.",
        visual: "The saved numeric key and value remain visible; their labels are emphasized one at a time. No semantic word-feature interpretation is claimed for their coordinates." },
      { id: "fb_own", checkpoint: "cp_process_blue",
        narration: "Layer one processes blue and makes its own key and value. That is fresh computation for the new input.",
        visual: "The numeric spotlight fades. The blue cell in layer 1 changes from empty to a newly made K V pair; earlier cells keep their teal saved pairs." },
      { id: "fb_query", checkpoint: "cp_process_blue",
        narration: "Blue also makes a query: numbers to compare with keys. Those comparisons set mixing weights, used to combine the values, including blue's own.",
        visual: "Show blue’s actual query [-0.15, 0.90] as the comparison input. Look-back connections join blue to all four allowed positions. A numeric line shows the actual layer-1 mixing weights: The 0.20, sky 0.31, is 0.24, blue 0.25; values are mixed with those weights." },
      { id: "fb_reads", checkpoint: "cp_process_blue",
        narration: "The old keys and values are inputs to that calculation. They save repeated computation, but they still have to be read.",
        visual: "The three previous layer-1 K V pairs are highlighted as reused. Blue remains marked new; the look-back connections stay visible." },
      { id: "fb_still_valid", checkpoint: "cp_process_blue", pause: 1,
        narration: "Why are those saved results still valid? Earlier positions cannot look ahead. Adding blue therefore cannot change what they computed.",
        visual: "The look-back arrows fade. A crossed information-flow edge rises from the later blue INPUT toward the earlier is OUTPUT; it is forbidden. This repeats the direction used in kp_lookback and shows the causal rule, with the caption later tokens cannot change earlier results." },
      { id: "fb_ffn", checkpoint: "cp_process_blue",
        narration: "After attention, the feed-forward network transforms blue's result. This becomes blue's input to layer two.",
        visual: "A numeric readout shows blue after its layer-1 attention block [-0.45, 1.40], then after its feed-forward block [-0.45, 2.00]. An upward arrow carries that fresh output into layer 2." },
      { id: "fb_pick_and", checkpoint: "cp_pick_and",
        narration: "Layer two repeats both operations using its own saved lists. Blue's final result produces next-token scores. The highest score selects and.",
        visual: "The arrows fade; the layer-2 cell above “blue” lights and gains “K” and “V”. A score list appears: and 2.30, “.” 2.06, clear 1.81; “and” turns yellow and a gold chip “and” appears." },
      { id: "fb_loop", checkpoint: "cp_pick_and", pause: 1.2,
        narration: "These repeating one-token passes are decoding. Each new choice needs the previous chosen token as its input.",
        visual: "The score list fades; the line “pick → feed back → process → pick” appears at the top and stays through the pause." },
    ],
  },
  {
    id: "cache",
    title: "The KV cache keeps earlier keys and values",
    purpose: "Name the KV cache, show exactly what it saved on the step for “blue”, and what it is not.",
    beats: [
      { id: "kv_name", checkpoint: "cp_cache",
        narration: "Keeping these keys and values is called the KV cache. Each layer saves one pair per processed position.",
        visual: "The grid with four processed columns, all with “K” and “V” tags; a teal bracket at the right of each layer row, labelled “layer 1 cache” and “layer 2 cache”. The gold “and” chip waits at the top right." },
      { id: "kv_saves", checkpoint: "cp_cache",
        narration: "For blue, we made one new pair in each of two layers. Six earlier pairs were reused. These counts are pairs, not individual numbers or execution time.",
        visual: "The two cells above “blue” flash yellow with the count “made: 2”; the six earlier cells flash teal with the count “read from cache: 6”." },
      { id: "kv_still_reads", checkpoint: "cp_cache",
        narration: "The new position still uses all the allowed earlier results, plus its own. Caching saves rebuilding them, not reading them.",
        visual: "The grey query arrows from the layer-1 “blue” cell to the earlier cells and itself reappear." },
      { id: "kv_not", checkpoint: "cp_cache", pause: 1,
        narration: "These saved pairs are working state for this request. The model's calculation rules stay the same with caching on and off.",
        visual: "The arrows fade. At the top, “stored answers” and “the model” appear struck through in grey, and “old keys and values” in teal." },
      { id: "kv_last", checkpoint: "cp_cache",
        narration: `${q("and")}, just picked, has no entry yet. It gets one only after it's fed back and processed.`,
        visual: "A fifth column of dashed empty cells appears under the gold “and” chip, labelled “no entry yet”." },
    ],
  },
  {
    id: "close",
    title: "Known tokens go together; picked tokens go one at a time",
    purpose: "State the punchline, then pose the cache-off transfer case with a pause before revealing it, and end on a reframe.",
    beats: [
      { id: "cl_known", checkpoint: "cp_close",
        narration: "So here's the real reason. The prompt's tokens are all known, so their positions go through each layer together.",
        visual: "The three prompt columns flash together; the label “known: together” appears above them." },
      { id: "cl_unknown", checkpoint: "cp_close", pause: 1.2,
        narration: "An answer token doesn't exist until it's picked, and the next pick needs it processed first. So the answer comes one token at a time.",
        visual: "Column 4 flashes, then the gold “and” above column 5; the label “picked: one at a time” appears above them and stays through the pause." },
      { id: "cl_transfer_ask", checkpoint: "cp_transfer", pause: 3,
        narration: `A new case. The prompt is processed, then the cache is switched off before ${q("blue")} goes in. What must be made again? And must the answer change?`,
        visual: "Rewind to before blue is processed: hide the and choice, return blue to a waiting output chip, clear its two layer cells and show its empty input slot. Then clear the six prompt K/V pairs; show cache off and question marks. No second choice is visible before the reveal." },
      { id: "cl_transfer_reveal", checkpoint: "cp_transfer", interactive: "reveal",
        narration: "Rebuild the three prompt positions, plus blue, in both layers: eight pairs instead of two. The same toy calculation still gives the same scores and token.",
        visual: "Feed blue into its slot; rebuild the six old prompt pairs and make blue’s two new pairs. All eight become valid; only then show the and choice and made: 8 instead of 2, pick: and, unchanged." },
      { id: "cl_reframe", checkpoint: "cp_close", pause: 1.5,
        narration: "An ordinary model can compute many things at once. Its next choice still waits for the previous chosen token.",
        visual: "Everything fades except the five chips “The sky is blue and” in one row, with the closing sentence above them." },
    ],
  },
];

export const PREDICTION = {
  id: "predict_one_trip",
  prompt: "A GPU does thousands of calculations at once. Could it pick “blue” and “and” together, in one trip through the model?",
  options: [
    { id: "yes", label: "Yes, both at once" },
    { id: "no", label: "No, one per trip" },
    { id: "unsure", label: "Not sure yet" },
  ],
  correct: "no",
  revealAtCheckpoint: "cp_pick_blue",
  explanation:
    "No. The scores for the token after “blue” come from position four, and position four exists only after “blue” is picked and fed back. One ordinary trip picks one new token.",
};

export const TRANSFER = {
  id: "transfer_six_token_prompt",
  prompt:
    "A different request has SIX prompt tokens. Its first answer token is picked; then the cache is turned off. To choose its second answer token, which work returns? Must the exact toy’s answer change?",
  answer: "The six old positions must be rebuilt, along with the new input position, in every layer. With two layers, that is 14 new K/V pairs rather than 2. The same exact computation and decoding rule give the same scores and token. The cache changes repeated work, not the deterministic rule.",
  rubric: [
    { score: 2, text: "Names both: the earlier positions' keys and values are rebuilt in every layer, and the deterministic toy still picks the same token (same numbers, same rule)." },
    { score: 1, text: "Names only one of the two parts." },
    { score: 0, text: "Says the cache stores answers or weights, or that the GPU itself must now work one position at a time, or gives neither part." },
  ],
  revealBeat: "cl_transfer_reveal",
};

// Local "dive deeper" intents. Matching is plain keyword lookup; unknown text is handed back to the host conversation.
export const INTENTS = [
  { panel: "attention", label: "Attention, worked with numbers",
    aliases: ["attention", "softmax", "query", "queries", "key", "keys", "value", "values", "mask", "causal", "dot product", "weights", "math", "formula", "numbers"] },
  { panel: "model", label: "What a layer does",
    aliases: ["layer", "layers", "ffn", "mlp", "feed-forward", "feed forward", "explain the model", "model", "transformer", "residual", "vector", "embedding"] },
  { panel: "insight", label: "Requests side by side (batching)",
    aliases: ["gpu", "batch", "batching", "parallel", "lanes", "lane", "insight", "show the insight", "throughput", "many requests", "speed", "fast", "slow", "bottleneck"] },
  { panel: "cache", label: "Cache on and off",
    aliases: ["cache", "kv cache", "kv", "recompute", "recomputed", "reuse", "turn off", "cache off"] },
  { panel: "transfer", label: "Check your understanding",
    aliases: ["quiz", "test", "check", "transfer", "exercise"] },
];

export function matchIntent(text) {
  const t = ` ${String(text).toLowerCase().replace(/[^a-z0-9\- ]+/g, " ")} `;
  let best = null;
  for (const intent of INTENTS) {
    for (const alias of intent.aliases) {
      if (t.includes(` ${alias} `) && (!best || alias.length > best.alias.length)) best = { ...intent, alias };
    }
  }
  if (!best && /^(?:please )?(?:(?:dive|go|dig) deeper|tell me more|more details?)(?: please)?$/.test(t.trim())) {
    return {panel: "model", label: "Explain the model", alias: "dive deeper"};
  }
  return best;
}
