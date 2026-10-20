# ADR 0002: checkpoint evidence before scene authoring

Status: implemented for a protected evaluation; runtime acceptance remains separate.
Date: 2026-10-19. Complements [ADR 0001](0001-concept-explanation.md).

## Problem and evidence

The first live CE-1 vacuum revision combined web research and a large typed visual
artifact in one call. It exceeded the existing 210-second provider deadline.
The job failed, published nothing and retained $0.65 for unknown billing. This is
not a measured zero-cost failure or a successful CE-1 generation benchmark.

## Decision

Separate the work into durable research → author → review → voice → video phases.
Research has its own registry task, small typed evidence schema and 2,500-token
limit. The existing OpenAI adapter retrieves primary-source evidence. Authoring
and review consume that checkpoint, perform no new search and cannot introduce
source URLs outside it or reorder its source table. Facts refer to exact source
URLs; the author receives explicit zero-based source-table indices. Source presence is not source entailment or expert approval.
Each phase retains its own existing paid-operation receipt, lease and checkpoint.

Research reserves $0.30, author/review $0.65 each and up to seven speech phases
$0.05 each: $1.95 fits the existing $2 admission reservation. Validate these bounds
and model-specific rates at startup. The $50 total ceiling is unchanged. There is
no automatic paid retry, provider fallback or invented completed output. A failed
attempt remains in the ledger and evaluation denominator. Unknown billing remains
retained until reconciled using provider evidence.

This extends application task routing; it does not change the shared gateway's
ModelBackend protocol or duplicate its services. All adapters are trusted startup
registrations. Another research route must declare retrieval support. A lesson
source ledger remains a draft until its separate human technical review.

## Migration and verification

New jobs carry `pipeline_version=evidence-first-1`. Old terminal job progress keeps
its combined research/build meaning. An already-paid pre-split author output is
resumed without a new research call. Interrupted unknown calls still fail closed.
Lesson spec/video identities, member history and the existing v1 reader remain
unchanged. No paid phase was redeployed while the first attempt was in flight.

Contract tests cover research routing/limits, malformed evidence stopping authoring,
source-boundary enforcement, paid-output migration and full real-MP4 publication.
Evaluation packets can export terminal failed jobs without prompts, private outputs
or fake artifacts. A new explicit production operation must demonstrate the split
path; engineering tests alone do not establish runtime reliability or teaching quality.


A completed paid evidence output may be reused only by a fresh explicit owner
operation for the same member, question and immutable parent within seven days,
after full validation under the current contract. Unknown billing, invalid source
references or an editorial response cannot qualify. Original failed records remain
unchanged. Reused evidence receipts appear separately in evaluation packets so
incremental cost is not confused with prior evidence cost.

The first split evaluation completed research in 27 seconds ($0.072828 recorded;
21,844 input / 914 output tokens, two search calls) but failed local validation:
several summaries exceeded an unnecessarily narrow 240-character internal limit,
and a numeric source reference was out of range. Internal research summaries now
allow 600 characters; all lesson/craft layout gates remain unchanged. Research
facts now use exact source URLs, validated against the packet's source list, to
avoid positional ambiguity. The invalid saved packet is retained, not repaired by
guessing. Further production validation remains required.

## Review verdict protocol

The next split run completed evidence and an 8,239-output-token visual draft, but
the full-lesson review exhausted its 10,000-token output limit. The known receipts
total $0.308546; nothing was published. New jobs use `review_protocol=verdict-1`:
the reviewer inspects the complete draft but returns only accept/reject, actionable
notes and the exact draft SHA-256. It cannot rewrite geometry or silently repair
content. A rejection or mismatched hash stops publication. The same structural
floor runs after review and before publication. Historical full-review checkpoints
retain their parser. This changes the output protocol, not the editorial criteria.

A fresh, explicit owner revision may reuse the valid evidence and authored draft
after a billed review transport/incomplete-output failure. The parent hash, question,
member and seven-day scope must match; research/author/review receipts must be known,
and current schema/source/quality checks must pass. Editorial rejections cannot
qualify. Preserve the original failed operation, draft hash and receipts; bind the
new verdict to the new revision identity. Evaluation packets separate reused research,
reused authoring and incremental spending. No automatic paid retry is introduced.

Future OpenAI receipts distinguish search actions from page-open/find actions.
Missing or unknown action metadata retains a conservatively estimated search fee.
Historical receipts remain unchanged: their `search_calls` counted observed web-tool
items, which may include page opens. They are application estimates, not invoice
reconciliation. See [official action accounting](https://developers.openai.com/api/docs/guides/tools-web-search#output-and-citations).

A local browser review then found the completed draft used unlabeled tiny overlays
in panels that render independently from the machine. CE-04/05/07 therefore block
its reuse under the current quality floor. Each panel now requires its own label;
author/editor instructions require a large working mechanism and physical
surroundings. Current gates are reapplied before every recovery. Valid evidence
from a known billed review failure may be reused separately; its drawing is not
automatically accepted. Engineering success remains distinct from craft review.

## Compact authoring transport

The subsequent full-format author response returned `incomplete/max_output_tokens`
at 10,000 tokens ($0.109544; provider-returned identity `gpt-6.1-sol`). New jobs
carry `author_protocol=compact-1`. A provider-neutral DTO groups coordinates and
paint, omits mandatory empty static-motion arrays and groups pose numbers with an
explicit fixed ordering. The server expands the data into the unchanged full
AuthorLessonSpec before all source, geometry and learning gates. No geometry,
labels, layers, paths, evidence, limits or causal state are inferred or removed.
Existing paid full-format checkpoints retain their parser. The public lesson/API,
version, renderer and media meanings are unchanged.

A round-trip regression preserves the exact draft hash and validates schema refs.
Malformed coordinates/paint, unsupported fields and invalid expanded pose bounds
remain errors. The serializer refuses to discard legacy motion. The failed
vacuum checkpoint serializes to 24,469 compact bytes versus 26,080 full bytes at
equal minification; token/latency improvement needs the next live run and must not
be inferred from byte savings. The $2 reservation and $50 ceiling are unchanged.
