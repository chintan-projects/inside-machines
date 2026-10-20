import { useEffect, useState } from 'react';
import type { ReactElement } from 'react';
import { api, errorMessage } from './api';
import type { OwnerReport } from './contracts';
import { ReviewWorkbench } from './teaching/ReviewWorkbench';

const money = (n: number): string => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 3 }).format(n);
export function OwnerView(): ReactElement {
  const [report, setReport] = useState<OwnerReport | null>(null), [error, setError] = useState('');
  useEffect(() => { void api<OwnerReport>('/owner/report').then(setReport).catch(error => setError(errorMessage(error))); }, []);
  if (error) return <p role="alert" className="error">{error}</p>;
  if (!report) return <p role="status">Loading the alpha report…</p>;
  const hits = report.events.filter(e => e.kind === 'catalog_hit').length;
  const requests = report.events.filter(e => ['catalog_hit', 'generation_requested', 'requested_topic', 'joined_job'].includes(e.kind));
  const positive = report.feedback.filter(f => f.value === 'up').length;
  return <section className="owner"><p className="eyebrow">Owner only · Budget totals & 7-day activity</p><h1>What curiosity is teaching us</h1>
    <p className="muted">Demand and feedback are learning signals. A thumbs-up does not verify a lesson’s facts.</p>
    <div className="metrics">{[['AI cost ledger', money(report.spent_usd)], ['Reserved', money(report.reserved_usd)], ['Available budget', money(report.remaining_usd)], ['Library reuse', `${hits} / ${requests.length}`]].map(([label, value]) => <div key={label}><span>{label}</span><strong>{value}</strong></div>)}</div>
    <p className="notice">Generation is {report.generation_enabled ? 'connected' : 'disabled until the provider key and spending ceiling are configured'}. Costs use configured rates; speech and unclassified web-tool charges are estimates. Historical web-tool fees remain conservative. Interrupted requests with unknown billing retain their allowance until reconciliation.</p>
    <div className="report-grid"><section><h2>What people asked</h2>{requests.length ? <div className="report-list">{requests.slice().reverse().map((e, i) => <div key={i}><strong>{e.question || e.canonical}</strong><span>{e.kind.replaceAll('_', ' ')} · {new Date(e.at * 1000).toLocaleDateString()}</span></div>)}</div> : <p className="muted">Requests will appear here as your family explores.</p>}</section>
      <section><h2>Did it help?</h2><p>{positive} positive · {report.feedback.length - positive} negative</p>{report.feedback.map(f => <blockquote key={`${f.user_id}:${f.lesson_id}`}><strong>{f.value === 'up' ? 'Helpful' : 'Needs work'} · {f.lesson_id}{typeof f.stage === 'number' ? ` · step ${f.stage+1}` : ''}</strong><p>{f.reason || 'No written feedback'}</p></blockquote>)}</section></div>
    <h2>Generation jobs</h2>{!report.jobs.length ? <p className="muted">No generation jobs yet. New requests will appear here once AI generation is enabled.</p> : <div className="table-scroll"><table><thead><tr><th>Machine</th><th>Status</th><th>Step</th><th>Issue</th></tr></thead><tbody>{report.jobs.map(job => <tr key={job.id}><td>{job.canonical}</td><td>{job.status}</td><td>{job.phase}</td><td>{job.error || '—'}{job.failure_type&&<small>{job.failed_phase} · {job.failure_type}</small>}{[...(job.quality_issues||[]),...(job.validation_issues||[])].length>0&&<details><summary>Bounded diagnostics</summary><ul>{[...(job.quality_issues||[]),...(job.validation_issues||[])].map((issue,i)=><li key={i}>{issue}</li>)}</ul></details>}</td></tr>)}</tbody></table></div>}
    <details><summary>Token and cost ledger ({report.ledger.length} operations)</summary><div className="table-scroll"><table><thead><tr><th>Operation</th><th>Input tokens</th><th>Output tokens</th><th>Recorded cost</th></tr></thead><tbody>{report.ledger.map(row => <tr key={row.operation}><td>{row.operation}{row.response_status&&<small>{row.response_status}{row.incomplete_reason?` · ${row.incomplete_reason.replaceAll('_',' ')}`:''}</small>}</td><td>{row.input_tokens}</td><td>{row.output_tokens}</td><td>{money(row.charged_usd)}{row.uncertain ? ' · billing unknown' : row.speech_estimated||row.search_estimated ? ' · estimate' : ''}</td></tr>)}</tbody></table></div></details>
    <ReviewWorkbench reserve={report.generation_reserve_usd}/>
  </section>;
}
