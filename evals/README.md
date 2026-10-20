# Concept explanation evaluations

`concept-cases.json` fixes the same questions, required relationships, misconception,
transfer task and critical failures for any provider. It includes different machine
families, ambiguous AC and unsupported exact-machine requests. It is an evaluation
set, not measured evidence that one provider is better.

Use the product pipeline and existing task routes/budget for candidate generation;
do not call providers outside the shared gateway or create a second spending ledger.
Only OpenAI is currently configured; another adapter needs its own contract tests,
capabilities, rates and reservations before these cases can establish comparability.

Export a private packet from the configured database, without making paid calls:

```sh
.venv/bin/python -m backend.evaluation packet --lesson air-conditioner-ce-1 --case ac --output .data/evals/ac.json
.venv/bin/python -m backend.evaluation compare .data/evals/ac.json --output .data/evals/comparison.json
```

Packets contain immutable spec/video hashes, structural findings, whitelisted usage
receipts from the actual job ledger, and initially empty human ratings. They exclude
user records, private chats, raw prompts and paid-call outputs. Authored lessons
have no provider receipt; cost/model remain unreported, not fabricated as measured.
Speech estimates and uncertain billing are separate from recorded token usage.

Have a person review the artifacts without seeing the provider label, then fill
`ratings`: factual, causal, visual, simplicity and transfer, each 0 (fails), 1
(partial) or 2 (meets the declared rubric), plus reviewer and critical-error flag.
Use `must_explain` and `critical_errors` in the case rather than visual polish as a
proxy for truth. Preserve the original packet and save a separately rated copy.
Comparison requires the same case and keeps missing ratings unmeasured. Include
failures and abstentions in the run log; don't compare only successful generations.

This reviewer rubric does not replace the five-beginner teach-back/transfer test
or next-day retention check. Record those in the owner workbench for the exact
lesson/video hashes. The workbench requires independent human technical evidence,
actual-phone craft evidence and eligible beginner scores before a release decision.
It records owner assertions and cannot authenticate reviewer expertise itself.
