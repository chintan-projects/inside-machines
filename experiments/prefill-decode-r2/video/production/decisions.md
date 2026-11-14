# Decisions
- 2026-11-13: Episode script is generated from `lesson/story.js` by `node build.mjs`; edit the story, not script.yaml, so the interactive captions and film narration stay identical.
- 2026-11-13: Film uses two drawn layers; narration says real models have many more. The toy model in `lesson/mechanism.js` also has exactly two layers, so counts on screen (6 prefill entries, 2 made / 6 read, 8 rebuilt) are computed, not typed.
- 2026-11-13: [Superseded below] "forward pass" is said as "trip through the model" for beginners; "prefill"/"decode" are not named in the film (only in the interactive depth).
- 2026-11-13: [Superseded below] The causal-mask "no looking ahead" arrow is drawn in layer 2 so it does not cross the look-back arrows in layer 1 (state field `arrows.blocked.layer`).
- 2026-11-13: [Assessment revised below] The film reveals the cache-off transfer answer after a 3 s pause (Theo guess-beat pattern). Consequence: human transfer checks must be taken before `cl_transfer_reveal` (pause the film there) or with the interactive's hidden-answer check first. The interactive never shows that beat until "Show the answer" is pressed.
- 2026-11-13: No timing ratio between prompt and answer steps anywhere (the original video's 10× claim is dropped, C5/C7).
- 2026-11-13: Background music off (unchanged from the owner's plan); ElevenLabs eleven_v4, voice EXAVITQu4vr4xnSDxMaL, $1 budget unchanged.

## Final production and departures from the proposed plan

- The proposed plan estimated 250 seconds. The delivered film is 379.2 seconds: 800 words across 38 beats. Added prerequisite links, a separate feed-forward beat and slower actual speech expanded it. This is a review risk for a curiosity-first product, not an accepted improvement in learning.
- Prefill and decoding are now named in the core. A concrete query vector and its computed mixing weights appear in the film; the full dot-product/softmax and feed-forward arithmetic remain optional interactive depth. This supersedes the earlier plan to keep all query numbers out of the film.
- Input-to-output arrows show that one position does not depend on its neighbor's newly computed output within the same layer. Feedback tokens follow the outside return path. The cache-off worked case rewinds blue, hides and, then rebuilds six old plus two new pairs before selecting and.
- Counts are K/V pairs, one per position per layer. They are not scalar counts, memory reads, GPU cores or timing ratios.
- The film's cache-off worked example uses the original three prompt tokens. The separate optional assessment uses SIX prompt tokens, so viewers must transfer the rule rather than repeat the film's answer. Teach-back and transfer both precede their scoring guides; anonymous export excludes written answers.
- Eight genuine automated reads retain beginner confusion in known_positions, first_pick, feed_back and cache. Each reviewer could state the central dependency, but that is not human acceptance. Produce a concrete review draft; do not activate it or expand the catalog on these results.
- Frozen source reviews are split into review/audience/round-XX.json. Build seeds Studio's required review file only when absent, preserving later local review rounds. The public source contains no private authoring sessions or narration cache.
