# First live generation benchmark — October 19, 2026

One observed OpenAI run, not a provider comparison or a representative average.
All requests ran on the personal, protected Vercel deployment using the configured
$50 app-AI ceiling. No API credential appears in this report.

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
- Generated artifact copied alone into local review storage, with no production
  users/chats/analytics copied. Chrome video metadata/captions passed; 375px layout
  showed no page overflow. Real-phone and human release review remain outstanding.

## Implications

The first reusable lesson cost less than a dollar in this observation, while its
multi-minute generation time remains a significant experience constraint. Reuse
avoids another AI generation charge; serving artifacts still consumes hosting and
storage. Measure more machines, failures and latency before extrapolating cost or
choosing a cheaper model. Claude and open-model comparisons have not been run.
