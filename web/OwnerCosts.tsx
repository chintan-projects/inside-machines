import { useEffect, useState } from 'react';
import type { ReactElement } from 'react';
import { api, errorMessage } from './api';
import './owner-costs.css';

interface CostTotals {
  recorded_usd:number; receipt_based_usd:number; estimated_usd:number; uncertain_usd:number;
  input_tokens:number; output_tokens:number; operations:number;
}
interface RevisionCost {
  lesson_id:string; archived:boolean; released:boolean; narration:string;
  production_mode:string; declared_paid_calls:number|null; build:CostTotals;
}
interface SystemCost {
  system_id:string; title:string; category:string; build:CostTotals; chat:CostTotals;
  revisions:RevisionCost[]; jobs:number; active_reserved_usd:number;
  owner_draft_reservation_usd:number; expected_generation_usd:null;
  optional_hosted_speech_estimate_usd:number|null; speech_script_words:number|null;
  speech_estimate_lesson_id:string|null; speech_estimate_basis:'active-lesson'|'authored-source'|'unmeasured';
}
interface CostReport {
  systems:SystemCost[]; attributed:CostTotals; unallocated:CostTotals; ledger_total:CostTotals;
  stored_spent_usd:number; spent_ledger_difference_usd:number; stored_reserved_usd:number;
  unallocated_reserved_usd:number; budget_usd:number; generation_reserve_usd:number;
  speech_rate_usd_per_minute:number; assumptions:string[];
}
const money=(value:number):string=>new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',minimumFractionDigits:2,maximumFractionDigits:4}).format(value);
const tokens=(value:number):string=>new Intl.NumberFormat('en-US').format(value);

function RecordedCost({cost}:{readonly cost:CostTotals}):ReactElement {
  return <><strong>{money(cost.recorded_usd)}</strong>
    {cost.estimated_usd>0&&<small>{money(cost.estimated_usd)} estimated</small>}
    {cost.uncertain_usd>0&&<small>{money(cost.uncertain_usd)} billing unknown</small>}</>;
}

export function OwnerCosts():ReactElement {
  const [report,setReport]=useState<CostReport|null>(null),[error,setError]=useState('');
  useEffect(()=>{
    let active=true;
    void api<CostReport>('/owner/costs').then(result=>{if(active)setReport(result);})
      .catch(reason=>{if(active)setError(errorMessage(reason));});
    return()=>{active=false;};
  },[]);
  return <section aria-labelledby="scope-cost-heading">
    <h2 id="scope-cost-heading">The cost of each explanation</h2>
    {error&&<p role="alert" className="error">{error}</p>}
    {!report&&!error&&<p role="status">Reconciling system costs with the shared ledger…</p>}
    {report&&<>
      <p>A customer request costs no AI credits. Each owner draft reserves {money(report.generation_reserve_usd)} before starting.
        That is an allowance, not a price estimate. Revisions and live chat use additional allowances.</p>
      <p className="muted">These {report.systems.length} scopes share the same production framework. Missing receipts mean unmeasured cost.
        Local authoring and computer speech can have no paid API calls; design, hosting, storage and human review still take resources.</p>
      <p className="muted">Scroll across the comparison to see tokens, revisions and voice estimates.</p>
      <div className="table-scroll" tabIndex={0} role="region" aria-label="Scrollable system cost comparison"><table className="cost-table"><caption>Build receipts include failed jobs and preserved revisions. Chat is shown separately.</caption>
        <thead><tr><th scope="col">System</th><th scope="col">Build ledger</th><th scope="col">Input / output tokens</th><th scope="col">Prepared revisions</th><th scope="col">Optional hosted voice</th></tr></thead>
        <tbody>{report.systems.map(row=><tr key={row.system_id}>
          <th scope="row">{row.title}<small>{row.category}</small></th>
          <td>{row.build.operations?<RecordedCost cost={row.build}/>:<span>No paid receipts</span>}
            {row.chat.operations>0&&<small>Chat: {money(row.chat.recorded_usd)} · {row.chat.operations} operations</small>}
            {row.active_reserved_usd>0&&<small>{money(row.active_reserved_usd)} still reserved</small>}
          </td>
          <td>{row.build.operations?`${tokens(row.build.input_tokens)} / ${tokens(row.build.output_tokens)}`:'—'}</td>
          <td>{!row.revisions.length?'Not prepared':<details><summary>{row.revisions.length} preserved</summary>
            {row.revisions.map(revision=><p key={revision.lesson_id}><a href={`#/lesson/${revision.lesson_id}`}>{revision.lesson_id}</a><small>
              {revision.archived?'Historical':revision.released?'Released':'Draft · review required'}
              {revision.production_mode==='local-authored'&&revision.declared_paid_calls===0?' · local work: 0 declared paid calls':''}
              {revision.production_mode==='unmeasured'?' · production cost unmeasured':''}
            </small><small>{revision.narration}</small></p>)}
          </details>}</td>
          <td>{row.optional_hosted_speech_estimate_usd===null?'Unmeasured':<>≈ {money(row.optional_hosted_speech_estimate_usd)}
            <small>Speech API estimate · 130 words/min</small><small>{row.speech_script_words} words · {row.speech_estimate_basis==='active-lesson'?'current served revision':'complete authored source'}</small></>}</td>
        </tr>)}</tbody>
      </table></div>
      <p>Attributed to these scopes: <strong>{money(report.attributed.recorded_usd)}</strong>.
        Other or unmatched app operations: <strong>{money(report.unallocated.recorded_usd)}</strong>.
        Entire app ledger: <strong>{money(report.ledger_total.recorded_usd)}</strong>.</p>
      {Math.abs(report.spent_ledger_difference_usd)>0.000001&&<p className="notice">The stored spending total differs from operation receipts by {money(report.spent_ledger_difference_usd)}. Reconcile this difference before treating the ledger as complete.</p>}
      {report.unallocated_reserved_usd>0&&<p className="notice">{money(report.unallocated_reserved_usd)} remains reserved outside attributed system jobs.</p>}
      <details><summary>How to read these numbers</summary><ul>{report.assumptions.map(assumption=><li key={assumption}>{assumption}</li>)}</ul></details>
    </>}
  </section>;
}
