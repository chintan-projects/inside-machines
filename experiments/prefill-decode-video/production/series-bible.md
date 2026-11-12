# Prefill versus Decode: series bible

## Audience and tone

Curious adult beginner (product leader). Calm, plain causal language, second person, no jargon before the thing it
names is on screen. Theo (blackboard) presenter: black canvas, quiet transitions, build up rather than replace.
Everything numeric is illustrative and labelled so.

## Concept colours   (fixed for the whole series; new concepts take unused colours)

| Concept | Colour | Hex |
|---|---|---|
| Prompt tokens (known input) | BLUE_C | #58C4DD |
| Generated / sampled output token | GOLD_C | #F0AC5F |
| Token currently being processed ("look here") | YELLOW outline | #FFFF00 |
| Saved key + value (KV cache cell) | TEAL | #5CD0B3 |
| Not allowed / future / blocked | RED_C | #FC6255 |
| Model layers and structure | GREY_B outline | #BBBBBB |
| GPU memory (reading) | PURPLE_C | #9A72AC |

Shape reinforces colour: prompt and generated tokens are rounded chips with their text; a saved key+value is a filled
square cell; an empty (not yet processed) cell is a dashed outline; the currently processed token gets a yellow box.

## Recurring devices

- The main-question line, small and faint at the top: "Why is the prompt read together, but the answer written one
  token at a time?"
- The grid: token positions are columns, layers are rows (3 shown, labelled "layer 1–3"; real models have many).
  Inputs sit under the grid, sampled tokens above it.
- The toy request: prompt "The sky is" → "blue" → "and" → "clear" → "." → end. Illustrative only.

## Terms and names   (translations used everywhere: subtitles, labels, narration)

| Original | Used in this series |
|---|---|
| KV cache | KV cache ("saved keys and values"); spoken "K V cache" |
| prefill | prefill |
| decode | decode step |
| causal mask | causal mask (screen label); spoken "can only look back" |
| memory-bound | "limited by memory reads" |

On-screen type: `Text` in the scene_kit video font (Noto Sans) for every label; no LaTeX formulas in this episode.

## Episode format   (cover, opening, closing)

Cover: the grid with a gold token arcing from the top back into the input row. Opening: a concrete hook within five
seconds (an answer streaming). Closing: one-sentence reframe, then the end credits page with the three sources.
