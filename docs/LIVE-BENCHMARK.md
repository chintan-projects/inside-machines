# First live generation benchmark — October 19, 2026

One observed OpenAI run, not a provider comparison or a representative average.
All requests ran on the personal, protected Vercel deployment using the configured
$50 app-AI ceiling. No API credential appears in this report.

Historical identity correction: earlier receipt `models` fields retained the
configured/requested alias, not the API's resolved identity. Read those names below
as requested models. Reported token counts remain intact. New receipts retain the
API-returned identity and explicitly flag missing identities (including speech).
No historical row has been edited to pretend that information was observed.

## Successful new-machine run

- Question: How does a household vacuum cleaner work?
- Text: `gpt-6.1-sol`, configured low reasoning; speech: `gpt-4o-mini-tts`.
- Output: 35 safe geometric parts, five causal stages, four sources, interactive
  cutaway, included follow-ups and an actual 66.02-second H.264/AAC video.
- Time from admission to publication: **375.91 seconds (6m16s)**.
- Authoring: **14,538 input / 7,234 output tokens**, two search calls,
  **$0.121416** calculated from reported usage and configured rates.
- Review: **7,888 input / 7,325 output tokens**, **$0.089026**.
- Five speech calls: **$0.024154 estimated**, using the configured narration rate;
  this endpoint did not return the text-token usage contract.
- Combined: **22,426 input / 14,559 output tokens**, **$0.234596 including estimated
  speech**. This is calculated application cost, not invoice reconciliation.

The total excludes Vercel compute, Blob traffic/storage, database charges, fresh
follow-up chats and earlier failed attempts. Source count and automated editorial
acceptance do not establish factual correctness; human review remains required.

## Failed attempts and budget accounting

The first attempt returned HTTP 400 with unsupported URI schema format. The
second exceeded the original 100-second provider deadline. Each retains its $0.65
allowance as **uncertain billing**, for $1.30 total. These are conservative budget
charges, not claims that OpenAI actually billed those amounts.

The corrected attempt completed with configured low reasoning, a 210-second
provider deadline and a gateway deadline within its 240-second worker lease.
No implicit paid retries or model fallbacks were enabled.

After the successful lesson and two live follow-up chats, the ledger showed
**$1.545924 charged/reserved conservatively**, **$0 active reservations** and
**$48.454076 remaining**. Later use will change those values.

## Hosted checks

- Invite sign-in, four-lesson catalog, private MP4 byte-range delivery.
- Real durable queue delivery through authoring, review, all five speech phases,
  rendering and atomic publication.
- Two members reused the generated artifact without a new generation job.
- Private chat isolation, owner-route isolation and logout/session revocation.
- Fresh live answers on both an authored starter and the generated lesson.
- Hosted versioned service worker, shell manifest and PWA manifest.
- Hosted Chrome download, forced network-offline full reload, and actual downloaded
  video playback passed: 66.02 seconds, captions present, playback advancing, no
  media error. Network override was restored afterward.
- Generated artifact copied alone into local review storage, with no production
  users/chats/analytics copied. Chrome video metadata/captions passed; 375px layout
  showed no page overflow. Real-phone and human release review remain outstanding.

## Implications

The first reusable lesson cost less than a dollar in this observation, while its
multi-minute generation time remains a significant experience constraint. Reuse
avoids another AI generation charge; serving artifacts still consumes hosting and
storage. Measure more machines, failures and latency before extrapolating cost or
choosing a cheaper model. Claude and open-model comparisons have not been run.

## CE-1 protected review deployment — October 19, 2026

Implementation commit `c7c031e` is Ready in the personal
`chintan-4466s-projects/inside-machines-alpha` project. The protected stable URL
serves the new AC/washer/cooker teaching drafts. Private Blob media bytes verified
against SHA-256 before atomic import. A repeat import reports zero inserted,
three existing. Old lesson specs, chats, feedback, users, sessions, jobs, ledger,
spending and reservations compare unchanged across publication; only discovery
moves to the three new immutable IDs. No human review records were inserted.

Observed on deployed Chrome: the new causal AC player, keyboard slider to the
compressed state, native private MP4 playback at readyState 4 with 100.51-second
duration and one captions track; saved lesson survives full offline reload and
plays narration from a local Blob at the selected checkpoint. 375-pixel phone
capture is `shots/ce-1-hosted-phone.jpg` (ignored). Network/viewport overrides
were restored. This is browser evidence, not actual-phone or human craft acceptance.

A single owner-initiated, $2-reserved revision of the existing vacuum lesson tests
the new production CE-1 generation pipeline. Baseline ledger before that request:
$1.545924 spent/retained, $0 reserved, $50 ceiling. It failed after 211 seconds with ModelUnavailableError and no usable provider
receipt. The ledger retained $0.65 for uncertain billing and released the rest;
nothing was published and no paid call was retried automatically. A private failure
packet preserves this run in the evaluation denominator. ADR 0002 splits evidence
retrieval from authoring before the next explicit evaluation. No provider-comparison or learning result is
inferred from successful infrastructure or a model editorial pass.


The first split run completed its research request in 27 seconds: actual model
`gpt-6.1-sol`, 21,844 input tokens, 914 output tokens and two search calls;
$0.072828 recorded at configured rates, billing marked known by the receipt. It
published nothing because local packet validation failed on text limits and an
out-of-range positional source reference. The next contract uses exact source URLs
and a larger internal evidence-summary limit while preserving every lesson/craft
gate. Invalid saved data is not guessed into a successful checkpoint. Owner-only
diagnostics expose field paths/error types without raw outputs or private input.

The next split run validated research and completed the CE-1 author draft. Review
then exhausted 10,000 output tokens while returning a full replacement lesson:
research 22,205 input / 1,032 output ($0.094730), author 4,550 / 8,239 ($0.091490),
review 11,163 / 10,000 ($0.122326). Total $0.308546; all three receipts identify
`gpt-6.1-sol`, none have unknown billing. The failed job published nothing and
remains in the evaluation denominator. The application ledger afterward was
$2.577297846 spent/retained, $0 reserved, against the unchanged $50 ceiling.

The research receipt's four `search_calls` are observed web-tool output items,
not a verified count of billable searches. Earlier receipts also used that counting
rule. Future receipts inspect search/open/find action types and explicitly mark
missing action metadata as estimated; no historical amounts have been reduced.
New review uses a concise verdict bound to the full draft hash rather than copying
the entire scene. Its hosted evaluation remains pending.

The older adapter did not retain the provider's incomplete reason. The review
output-cap diagnosis is inferred from its exact 10,000-token receipt and unusable
result. Future receipts retain allowlisted response status/incomplete reason,
without raw provider bodies. Browser inspection separately rejected the saved
draft's unlabeled, context-free insets; that drawing cannot be recovered under
the tightened CE-04/05/07 floor. A fresh explicit operation may reuse its validated
evidence while authoring the detail views again. See the vacuum worksheet.

The next explicit operation reused validated evidence and completed a new drawing
(4,686 input / 7,307 output tokens, $0.082442; provider status completed). The
structural gate rejected two overlong labels outside the inset canvas before
review/speech/video. The application ledger became $2.659739846, $0 reserved.
Nothing was published. Authoring now specifies short separate labels and bounded
text placement, without padding spaces or sentence-length flow chains. The
clipping gate remains unchanged; this failed run is exported for evaluation.

The next author response conclusively returned `incomplete` with
`incomplete_reason=max_output_tokens`: 4,772 input / 10,000 output, $0.109544.
The API returned model identity `gpt-6.1-sol`; identity is observed, billing is not
marked uncertain. Nothing published; ledger $2.769283846, $0 reserved. Compact
authoring transport now removes repeated keys/empty arrays while preserving the
exact expanded lesson contract and all quality gates. The next explicit operation
will test it; no successful runtime or learning result is inferred from unit tests.

Compact authoring completed in 138.8 seconds: 4,775 input / 6,649 output tokens,
$0.076040, API-returned model `gpt-6.1-sol`, status completed. Initial DTO expansion
rejected omitted unused paint channels. The compiler now defines these channels
and zero-box polygon bounds explicitly; expanded data passes unchanged structural
gates. Browser inspection separately found a closed drawn outlet, so the teaching
policy was strengthened and invalidates that drawing for recovery. Ledger after
the run: $2.845323846 spent/retained, $0 reserved, unchanged $50 ceiling.

The AC has an agent engineering record scoped to code a753bf7, artifact hashes,
local viewport checks and hosted desktop/375/media/offline checks. A second
append-only record clarifies local versus hosted widths. Technical, actual-phone,
beginner learning and owner release gates remain false; no human score was added.

The open-passage policy run completed authoring (4,929 input / 6,748 output,
$0.077338) and concise review (8,151 / 266, $0.018962). Both API responses completed
with model identity `gpt-6.1-sol`; the verdict hash matched the draft. Review rejected
the lesson for unlabeled markers/ports, pickup markers starting inside the inlet,
and narration that did not explain enlarged material/bypass motion. Total
$0.096300, no publication; ledger $2.941623846, $0 reserved.

A new explicit revision can now use that critique and the rejected scene as input
to fresh authoring, with the same source/quality/editorial gates and all previous
failures retained. Owner diagnostics expose bounded critique. Private chats and
learner reasoning are excluded. Runtime acceptance of this loop is pending.


The critique-guided full revision resolved those four findings. Authoring used
14,152 input / 9,700 output tokens ($0.125304); fresh review used 8,864 / 420
($0.021928). Both completed with returned model `gpt-6.1-sol`, and the verdict
hash matched. Review identified one remaining solid/air collision: a horizontal
air marker crosses the drawn motor/shaft in two insets. Total $0.147232; no
publication. Ledger $3.088855846, $0 reserved, unchanged $50 ceiling.

Explicit revisions now support typed, source-hash-bound scene patches. Untouched
geometry and narration remain intact; the complete resulting lesson receives all
source/quality gates and a fresh full editorial review. No automatic paid retry.
Evaluation separates incremental cost, reused evidence/draft receipts and prior
critique inputs; failed attempts remain in the denominator. Runtime success of
the patch loop is pending, and no human ratings have been entered.


### Completed live typed revision (19 October 2026)

The first typed repair cleared the motor/air collision, but fresh review found
bag/motor label overlap in the bypass and bag/fan label overlap. It failed closed:
author 12,820 / 628 tokens, $0.031920; review 8,883 / 445, $0.022216. No publication.
Agent-rendered seated/bypass views independently reproduced both label failures.

The next explicit typed repair completed in 86.8 seconds, producing immutable
`household-vacuum-cleaner-ce-6b5e6fa1d2`. Author used 12,808 input / 507 output
($0.030686); fresh full review used 8,917 / 303 ($0.020864). Both responses returned
`gpt-6.1-sol`; exact-draft review accepted. Three `gpt-4o-mini-tts` speech receipts
add $0.018307692 estimated from configured duration rates. Incremental total:
$0.069857692. Video is 51.03 seconds, and hosted playback reached readyState 4
with one caption track and advancing time. All three structural gates passed.

This is a repair result, not a one-shot machine cost: reused evidence is $0.094730
and its paid critique ancestors add $0.297668. Their disjoint recipe total is
$0.462255692. Earlier unrelated/failed attempts remain in the evaluation denominator.
The complete application ledger is $3.212849538 spent/retained, $0 reserved,
unchanged $50 ceiling; historical uncertain allowances remain included.

Hosted Chrome exercised prediction, three causal chunks, before/after, nozzle
entry, seated/bypass comparison, transfer reasoning, keyboard enlarge/Escape and
375-pixel containment. A repeat generic lookup reached the new immutable lesson,
with unchanged job count and spend. Hash comparison confirms the parent's original
spec/video, private conversations and all pre-existing ledger rows are unchanged.
Private evaluation packets retain receipts and unmeasured human ratings. One
completed generated case is not broad factual, visual or reliability acceptance.

Deployment ownership correction: a separate agent confirmed the source Hobby
workspace is personal-named but its owning identity uses the work email. The
Gmail requester is another account. This does not make it Liquid AI's organization,
but it does fail the requested account separation. Project/Neon/Blob migration is
pending authenticated destination verification; see DEPLOYMENT-OWNERSHIP.md.
No further push/deployment is intended until that destination is resolved.
