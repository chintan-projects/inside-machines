# Visual explanation cost scenarios

Calculated October 19, 2026. Reproduce with `node scripts/cost-model.mjs`. This script makes no provider calls. Workloads are illustrative, not measured product performance.

## Provider rates

USD per million short-context tokens at standard rates, using uncached input. Rates: [official OpenAI pricing](https://developers.openai.com/api/docs/pricing). These examples compare spend, not suitability or quality.

| Model | Input | Output |
| --- | --- | --- |
| gpt-6-luna | $0.10 | $0.50 |
| gpt-6.1-sol | $2.00 | $10.00 |
| gpt-6-astra | $10.00 | $50.00 |

## Inference scenarios

Input/output counts are assumed total billable tokens across all requests in one attempt. Each individual request is assumed to stay within its model's short-context band. Output includes any charged reasoning tokens. All stages and tool results must fit these totals; otherwise the estimate is low. Attempts multiply the whole workload. Separate tool charges, cache writes, and long-context charges are excluded.

| Task | Input / output per attempt | Attempts | gpt-6-luna | gpt-6.1-sol | gpt-6-astra |
| --- | --- | --- | --- | --- | --- |
| Bounded follow-up on an existing lesson | 4,000 / 600 | 1 | $0.0007 | $0.0140 | $0.0700 |
| New artifact, moderate assumed workload | 20,000 / 8,000 | 3 | $0.0180 | $0.36 | $1.80 |
| New artifact, heavy assumed workload | 150,000 / 40,000 | 3 | $0.11 | $2.10 | $10.50 |

## Illustrative monthly contribution

Ten follow-ups use gpt-6.1-sol: $0.14. Assumed video playback is 30 delivered minutes: $0.03 using the [Stream rate](https://developers.cloudflare.com/stream/pricing/). Assumed allocated infrastructure is $0.25 per active subscriber. Base variable cost is $0.42. A moderate custom build adds $2.30 and a heavy one $11.00, each including an assumed $0.50 of rendering/worker overhead. These overhead allocations are placeholders.

15% assumes approved Small Business Program eligibility; 30% is a fee sensitivity case, not a universal storefront rule. [Apple program](https://developer.apple.com/app-store/small-business-program/). Prices are hypothetical experiments.

| Price | Fee case | Monthly use | Net after fee | Variable cost | Contribution | Contribution / net |
| --- | --- | --- | --- | --- | --- | --- |
| $4.99 | 15% | Library + 10 follow-ups | $4.24 | $0.42 | $3.82 | 90.1% |
| $4.99 | 15% | Above + 1 moderate custom build | $4.24 | $2.72 | $1.52 | 35.9% |
| $4.99 | 15% | Above + 3 moderate custom builds | $4.24 | $7.32 | -$3.08 | -72.6% |
| $4.99 | 15% | Above + 1 heavy custom build | $4.24 | $11.42 | -$7.18 | -169.2% |
| $9.99 | 15% | Library + 10 follow-ups | $8.49 | $0.42 | $8.07 | 95.1% |
| $9.99 | 15% | Above + 1 moderate custom build | $8.49 | $2.72 | $5.77 | 68.0% |
| $9.99 | 15% | Above + 3 moderate custom builds | $8.49 | $7.32 | $1.17 | 13.8% |
| $9.99 | 15% | Above + 1 heavy custom build | $8.49 | $11.42 | -$2.93 | -34.5% |
| $4.99 | 30% | Library + 10 follow-ups | $3.49 | $0.42 | $3.07 | 88.0% |
| $4.99 | 30% | Above + 1 moderate custom build | $3.49 | $2.72 | $0.77 | 22.1% |
| $4.99 | 30% | Above + 3 moderate custom builds | $3.49 | $7.32 | -$3.83 | -109.6% |
| $4.99 | 30% | Above + 1 heavy custom build | $3.49 | $11.42 | -$7.93 | -226.9% |
| $9.99 | 30% | Library + 10 follow-ups | $6.99 | $0.42 | $6.57 | 94.0% |
| $9.99 | 30% | Above + 1 moderate custom build | $6.99 | $2.72 | $4.27 | 61.1% |
| $9.99 | 30% | Above + 3 moderate custom builds | $6.99 | $7.32 | -$0.33 | -4.7% |
| $9.99 | 30% | Above + 1 heavy custom build | $6.99 | $11.42 | -$4.43 | -63.3% |

Excludes content authoring and human review, fixed costs, taxes, refunds, support, payment adjustments, acquisition, failed paid jobs, narration, and generative video. Contribution is not gross profit or a business forecast. Bundled/offline rendering does not incur video-streaming delivery charges.

## Reuse and budget examples

A moderate $2.30 artifact reused for 1,000 valid views allocates $0.0023 per view in assumed machine production cost; review and delivery are additional. A genuinely private personalized artifact must not be shared to gain this reuse.

For one personal user, 50 assumed gpt-6.1-sol follow-ups cost $0.70 in inference. Three moderate novel builds add $6.90. This says little about manual research, review time, or true end-to-end generation cost. A budget ceiling is a product control, not a guarantee supplied by the provider dashboard.
