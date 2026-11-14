# Recover understanding before adding detail

A curious learner needs a next action when the thread is lost. Make the player
aware of the current concept, example, operation and return point. Start from
the current representation, not from another long explanation.

## Reusable help behavior

- “I’m lost” or “more simply” opens an authored repair for the current beat.
- A named concept opens its corresponding repair; ambiguous or unknown questions
  offer two or three clear paths rather than a fabricated answer.
- “Dive deeper” asks which relationship to unpack. It must not dump every formula.
- A repair shows one concrete input → operation → changed output, with one
  optional diagnostic choice and specific feedback. Incorrect attempts change the
  explanation, not the learner’s access to it.
- Preserve the exact chapter, beat and experiment state. Return resumes there.
  Restart clears the attempt, help, question and media state.
- Keep answers ephemeral unless storage is explicitly requested. State whether
  help selects prepared material or uses a real connected AI; do not imply live
  generation from keyword matching.

Use topic data (concept IDs, aliases, repair routes, worked examples) with a shared
controller. The r3 reference in `experiments/prefill-decode-r2/r3/` includes a pure
controller tested with both inference and refrigerator metadata. Domain calculations
remain separate. A controller’s reuse does not approve another topic’s teaching.

## A confusion finding is work to do

Before paid narration or a ready-for-review handoff, obtain a fresh automated read
of the actual core. Ask for causal teach-back and a new situation before hints or
the answer rubric. Review implementation and visuals too, not only the prose.

Unresolved **lost** or **wrong** findings about a dependency in the scoped core
block handoff. Do not mark them “kept” because three rounds ran, the central
headline was repeated correctly, or a difficult prerequisite can be hidden under
“optional.” Change the representation or order, then get a fresh read. A clear,
explicit scope boundary (for example, no measured speed claim) is not confusion.
Depth needs its own coherent causal path; it cannot be a holding area for missing
core relationships.

New helper video projects declare `teaching_gate: review/core-readiness.json` in
`explanation.json`. The Studio wrapper checks this record **before reading a
speech credential** for `narrate` and before `deliver`:

```json
{
  "schema_version": 1,
  "episode": "ep01",
  "script_sha256": "<SHA-256 of the actual script.yaml bytes>",
  "review_kind": "fresh_automated_reader",
  "reviewer_id": "<actual independent review run>",
  "causal_teachback": "pass",
  "novel_transfer": "pass",
  "findings": []
}
```

Populate this from genuine review evidence, never the author’s imagined reader.
Findings use `kind`, `scope` (`core` or `depth`) and `status`; core `lost`/`wrong`
must be `fixed`. A changed script invalidates the digest. This is an integrity
and workflow guard over recorded evidence, not a semantic grader or proof that
the reader was human. Existing projects without this opt-in retain Studio’s
native checks; do not silently rewrite their manifests. Direct Studio use remains
possible, but it must follow the same teaching policy.

Keep technical truth, code tests, visual checks, automated comprehension and human
acceptance separate. Passing the automated floor makes a human review worthwhile;
it does not replace one or authorize public publication.
