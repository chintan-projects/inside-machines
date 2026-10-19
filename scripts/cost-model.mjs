// Planning calculator. Rates checked 2026-10-19; workloads are assumptions.
// No API calls. Run: node scripts/cost-model.mjs
import { writeFileSync, mkdirSync } from 'node:fs';
import assert from 'node:assert/strict';
const rates={ 'gpt-6-luna':{input:.1,output:.5}, 'gpt-6.1-sol':{input:2,output:10}, 'gpt-6-astra':{input:10,output:50} };
const cost=(model,input,output)=> (rates[model].input*input+rates[model].output*output)/1e6;
const workloads=[
  {name:'Bounded follow-up on an existing lesson',input:4000,output:600,attempts:1},
  {name:'New artifact, moderate assumed workload',input:20000,output:8000,attempts:3},
  {name:'New artifact, heavy assumed workload',input:150000,output:40000,attempts:3}
];
const models=Object.keys(rates);
const mdTable=(headers,rows)=>['| '+headers.join(' | ')+' |','| '+headers.map(()=> '---').join(' | ')+' |',...rows.map(r=>'| '+r.join(' | ')+' |')].join('\n');
const usd=n=>(n<0?'-$':'$')+Math.abs(n).toFixed(Math.abs(n)<.1?4:2);
const usageRows=workloads.map(w=>[w.name,`${w.input.toLocaleString()} / ${w.output.toLocaleString()}`,w.attempts,...models.map(m=>usd(cost(m,w.input,w.output)*w.attempts))]);
const followup=cost('gpt-6.1-sol',4000,600);
const moderate=cost('gpt-6-astra',20000,8000)*3+.5;
const heavy=cost('gpt-6-astra',150000,40000)*3+.5;
// Stream playback scenario, allocated infrastructure, and render cost are assumptions.
const base=followup*10+.03+.25;
const scenarios=[['Library + 10 follow-ups',base],['Above + 1 moderate custom build',base+moderate],['Above + 3 moderate custom builds',base+moderate*3],['Above + 1 heavy custom build',base+heavy]];
const contributionRows=[];
for(const fee of [.15,.30])for(const price of [4.99,9.99])for(const [name,cogs] of scenarios){
  const net=price*(1-fee), contribution=net-cogs;
  contributionRows.push([usd(price),`${fee*100}%`,name,usd(net),usd(cogs),usd(contribution),`${(contribution/net*100).toFixed(1)}%`]);
}
assert(Math.abs(followup-.014)<1e-10);
assert(Math.abs(moderate-2.3)<1e-10);
assert(Math.abs(heavy-11)<1e-10);
mkdirSync('docs',{recursive:true});
writeFileSync('docs/COST-TABLES.md',`# Visual explanation cost scenarios\n\nCalculated October 19, 2026. Reproduce with \`node scripts/cost-model.mjs\`. This script makes no provider calls. Workloads are illustrative, not measured product performance.\n\n## Provider rates\n\nUSD per million short-context tokens at standard rates, using uncached input. Rates: [official OpenAI pricing](https://developers.openai.com/api/docs/pricing). These examples compare spend, not suitability or quality.\n\n${mdTable(['Model','Input','Output'],models.map(m=>[m,usd(rates[m].input),usd(rates[m].output)]))}\n\n## Inference scenarios\n\nInput/output counts are assumed total billable tokens across all requests in one attempt. Each individual request is assumed to stay within its model's short-context band. Output includes any charged reasoning tokens. All stages and tool results must fit these totals; otherwise the estimate is low. Attempts multiply the whole workload. Separate tool charges, cache writes, and long-context charges are excluded.\n\n${mdTable(['Task','Input / output per attempt','Attempts',...models],usageRows)}\n\n## Illustrative monthly contribution\n\nTen follow-ups use gpt-6.1-sol: ${usd(followup*10)}. Assumed video playback is 30 delivered minutes: $0.03 using the [Stream rate](https://developers.cloudflare.com/stream/pricing/). Assumed allocated infrastructure is $0.25 per active subscriber. Base variable cost is ${usd(base)}. A moderate custom build adds ${usd(moderate)} and a heavy one ${usd(heavy)}, each including an assumed $0.50 of rendering/worker overhead. These overhead allocations are placeholders.\n\n15% assumes approved Small Business Program eligibility; 30% is a fee sensitivity case, not a universal storefront rule. [Apple program](https://developer.apple.com/app-store/small-business-program/). Prices are hypothetical experiments.\n\n${mdTable(['Price','Fee case','Monthly use','Net after fee','Variable cost','Contribution','Contribution / net'],contributionRows)}\n\nExcludes content authoring and human review, fixed costs, taxes, refunds, support, payment adjustments, acquisition, failed paid jobs, narration, and generative video. Contribution is not gross profit or a business forecast. Bundled/offline rendering does not incur video-streaming delivery charges.\n\n## Reuse and budget examples\n\nA moderate ${usd(moderate)} artifact reused for 1,000 valid views allocates $0.0023 per view in assumed machine production cost; review and delivery are additional. A genuinely private personalized artifact must not be shared to gain this reuse.\n\nFor one personal user, 50 assumed gpt-6.1-sol follow-ups cost ${usd(followup*50)} in inference. Three moderate novel builds add ${usd(moderate*3)}. This says little about manual research, review time, or true end-to-end generation cost. A budget ceiling is a product control, not a guarantee supplied by the provider dashboard.\n`);
console.log(`Wrote docs/COST-TABLES.md. Follow-up ${usd(followup)}; moderate build ${usd(moderate)}; heavy build ${usd(heavy)}.`);
