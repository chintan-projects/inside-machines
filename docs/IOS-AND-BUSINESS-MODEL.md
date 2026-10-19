# iOS delivery and business model

Planning date: October 19, 2026. Recommendation: build the learning experience so that playback works without AI. Start personally, test a small library, and introduce paid services only after demand and real production cost are known.

## Does iOS require a frontier model API key

No. Distribution platform, inference location, and who pays are separate decisions.

| Experience | Runtime model requirement | Who supplies credentials |
| --- | --- | --- |
| Watch bundled videos | None | Nobody |
| Run bundled interactive scenes and reviewed scenarios | None | Nobody |
| Search a small catalog and use authored questions | None; local text matching is sufficient | Nobody |
| Ask a fresh natural-language question | A model may help; it need not be a frontier model | On-device access, or the developer's backend credentials for a hosted provider |
| Identify an appliance or read an uploaded manual | OCR, matching, and evidence extraction; model choice depends on evaluated accuracy | Device APIs and/or developer-operated backend |
| Create an entirely new machine explanation | Authoring plus verification and rendering; a capable model can help | Developer production pipeline; generated output can then be replayed without inference |
| Expert personal tool with BYOK | Whatever provider the owner chooses | The owner; not required for ordinary consumers |

When using OpenAI's hosted API, keep its standard key on the server. Customers use an app account or purchase entitlement, not the developer's secret. [Official OpenAI authentication guidance](https://developers.openai.com/api/reference/overview).

Apple's [Foundation Models framework](https://developer.apple.com/foundation-models-framework/) offers on-device inference on supported configurations. Availability must be checked at runtime and the catalog must remain usable when the model is unavailable. This is a candidate for catalog routing and bounded language tasks, not evidence that it can generate mechanically correct scenes.

Apple also documents access to [Private Cloud Compute](https://developer.apple.com/private-cloud-compute/) with no cloud API cost for developers enrolled in the Small Business Program, below its first-time-download threshold, and holding the required entitlement. Availability follows Apple Intelligence availability; loss of eligibility requires a migration. Verify account access, supported OS/device/region, permitted use, and workload performance before selecting it. It does not supply an arbitrary code-rendering worker or eliminate content review.

These options make “frontier API or no app” a false choice. They do not make unlimited generation free or reliable.

## Recommended delivery architecture

Retain a portable lesson format: versioned scene assets, timeline, deterministic model, accessible descriptions, curated questions, and citations. The same lesson package should support interactive playback and a recorded video derived from it.

For iOS, evaluate a SwiftUI shell with bundled, reviewed web scenes in a constrained WKWebView. Native navigation, downloads, accessibility, purchases, and optional device intelligence stay in the shell. This is a reuse proposal, not an assertion that the current prototype is ready to submit. A fully native renderer is an option if real-device performance or accessibility makes the web renderer unsuitable.

An App Store release needs useful native behavior and a satisfactory app experience; Apple's minimum-functionality guideline addresses repackaged websites. Review this together with digital purchase requirements for the intended storefront. [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/).

## Personal and commercial paths

| Path | Start with | Cost exposure | When to choose it |
| --- | --- | --- | --- |
| Personal offline library | Three reviewed lessons; authored answers; no billing | Content creation and optional distribution costs; no runtime inference | Recommended now while deciding whether this is a business |
| Personal AI assistant | Same library plus one private backend or local inference | Metered questions and manual extraction, governed by a monthly cap | When actual questions exceed the authored answers |
| Free public catalog | Up to ten reviewed lessons after learning validation | Asset delivery, updates, support; production cost amortized across users | When sharing the content is itself the goal |
| Paid content packs | A finite, named collection with offline access | Mostly authoring and support; low repeat-playback cost | Best first monetization test for occasional use |
| Subscription | Continuing releases and a clearly capped hosted service | Recurring inference, support, and content production | Only if observed return use supports a recurring promise |
| Credits for custom work | Quote one understandable deliverable before starting | Variable job and retry costs | After quality, cost distribution, and failure recovery are measured |

Do not require customers to understand provider tokens. A customer buys a content pack, a number of answered questions, or a defined custom explanation. Internally, tokens, tool calls, CPU time, retries, and review minutes remain cost meters.

Do not sell a lifetime unlimited cloud service to finance ongoing inference. A one-time pack can explicitly include the purchased lessons and their corrections while excluding future custom generation.

## Is ten free videos a good starting offer

Ten is a possible release collection, not the first validation milestone. Start with three mechanisms and determine whether users learn better or return. The closest direct alternative already has 15 public lessons. [Market research](MARKET-RESEARCH.md) explains why a ten-video catalog is unlikely to be differentiated by quantity.

Keep free lessons fully usable: pausing, revisiting, offline playback where offered, and corrections should not consume credits. Place paid value around a new collection or a genuinely additional service. A free question should not unexpectedly become an expensive build.

Test a **$9.99 one-time themed pack** only as an experimental offer, with a clearly named collection. It is not an established price or a claim of willingness to pay. Compare it with remaining free. Delay a recurring plan until users exhibit a recurring job; possible $4.99 and $9.99 monthly price points in the calculator are sensitivity inputs, not launch commitments.

## What actually costs money

Playback, chat, manual extraction, and new-artifact creation should have separate budgets. [Reproducible cost scenarios](COST-TABLES.md) use checked provider rates and explicitly assumed workloads. They demonstrate sensitivity; no live generation benchmark has yet established these workloads.

In the illustrative model, a bounded follow-up using gpt-6.1-sol costs $0.014 in inference. Fifty such questions would cost $0.70. A new artifact using three assumed frontier attempts costs $1.80 in inference under the moderate workload and $10.50 under the heavy workload. Rendering, narration, tool use, and human review can add more. These are different tasks and should never share an unlimited allowance.

With illustrative monthly variable cost of $0.42 for ten follow-ups plus light delivery/hosting, a $4.99 plan under a 15% fee case retains $3.82 before fixed costs and other exclusions. Add three moderate $2.30 custom builds and it loses $3.08. This is why a low subscription price cannot safely include arbitrary generation. The table also tests 30% as fee sensitivity. Apple's [Small Business Program](https://developer.apple.com/app-store/small-business-program/) documents 15% for eligible enrolled developers; actual storefront proceeds, tax, and agreements must be used in production.

For optional video delivery, [Cloudflare Stream](https://developers.cloudflare.com/stream/pricing/) lists $1 per 1,000 delivered minutes and storage sold in $5 increments for 1,000 minutes. Ten three-minute videos watched once by 1,000 people imply 30,000 delivered minutes, or $30 in delivery, plus the applicable storage purchase and other charges. Offline repeated playback is a different case. Small static scene packages can instead use object hosting; [R2](https://developers.cloudflare.com/r2/pricing/) lists storage/operation pricing, a free tier, and no internet egress charge. Neither is a quote for the complete app.

Human review needs its own equation: accepted lessons × review hours per lesson × hourly opportunity cost. A cheap model bill does not make content production cheap. Count failed jobs in the cost per accepted artifact.

## Controls required before hosted generation

- Separate free playback from paid computation. Cache reviewed generic artifacts and curated answers.
- Route supported questions to existing content before considering generation. Bound chat history and retrieve relevant evidence rather than repeatedly sending entire manuals.
- Reserve a maximum job budget atomically before dispatch; cap tool calls, attempts, concurrency, and output. Account for actual usage against the reservation.
- Enforce a global monthly ceiling and a per-user ceiling in the application's own ledger. Stop accepting new work before the reserve is exhausted; provider spend alerts alone are insufficient.
- For a personal pilot, use a proposed $20/month ceiling, a $1/day soft warning, and a $2 maximum reservation for an ordinary question. Keep novel builds off by default. These are suggested settings, not spending authorization.
- Quote custom work in user-facing units, return reserved credits on failure, and reuse an idempotency key so reconnects cannot duplicate a charge.
- Price only after observing median and tail cost per accepted output, including failures. A low average with an uncontrolled tail is not enough.

If iOS credits are sold, Apple states that credits bought through in-app purchase may not expire. Use a purchase ledger and relevant restoration mechanisms; do not copy a web vendor's expiring-credit policy. Subscription entitlements and separately purchased credits need separate product definitions. Check current regional terms before submission. [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/).

## Recommended decision

Build the next version for personal use and learning validation. Give it three strong lessons, portable offline playback, curated questions, and a source-aware follow-up experiment behind a hard budget. Earn a reason for users to choose it before expanding to ten. If there is commercial demand, test a finite content pack first. Keep arbitrary custom generation as a separate, explicitly quoted product until its quality and economics are known.
