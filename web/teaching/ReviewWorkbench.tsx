import { useEffect, useState } from 'react';
import type { FormEvent, ReactElement } from 'react';
import { api, errorMessage } from '../api';
import type { CatalogEntry, RequestResult } from '../contracts';
import { useRef } from 'react';

const gateNames=['engineering','technical','craft','learning','release'] as const;
type Gate=typeof gateNames[number];
interface ReviewState {lesson_id:string;spec_sha256:string;video_sha256:string;bundle_sha256:string;bundle_issues:string[];spec_version:number;gates:Record<Gate,boolean>;can_release:boolean;ready:boolean;records:{gate:Gate;reviewer:string;decision:string;evidence:string;at:number}[];recording_note:string}
interface Score {baseline:string;causal:string;transfer:string;retention:string}
export function ReviewWorkbench({reserve}:{readonly reserve:number}):ReactElement {
  const [lessons,setLessons]=useState<CatalogEntry[]>([]),[selected,setSelected]=useState(''),[state,setState]=useState<ReviewState|null>(null),[error,setError]=useState(''),[busy,setBusy]=useState(false);
  const [gate,setGate]=useState<Gate>('technical'),[reviewer,setReviewer]=useState(''),[evidence,setEvidence]=useState(''),[decision,setDecision]=useState<'pass'|'needs-work'>('needs-work'),[independent,setIndependent]=useState(false),[realDevice,setRealDevice]=useState(false),[device,setDevice]=useState('');
  const [scores,setScores]=useState<Score[]>(()=>Array.from({length:5},()=>({baseline:'',causal:'',transfer:'',retention:''})));
  const operations=useRef<Record<string,string>>({});
  const [retryAvailable,setRetryAvailable]=useState(false);
  async function revise(newAttempt=false):Promise<void> {
    if(!selected)return;
    if(newAttempt||!operations.current[selected])operations.current[selected]=crypto.randomUUID();
    setBusy(true);setError('');setRetryAvailable(false);
    try {
      const result=await api<RequestResult>(`/owner/lessons/${encodeURIComponent(selected)}/revise`,{operation:operations.current[selected]});
      if(result.kind==='job'&&result.job_id)window.location.hash=`/job/${result.job_id}`;
      else if(result.kind==='lesson'&&result.lesson_id)window.location.hash=`/lesson/${result.lesson_id}`;
      else setError(result.message||'The revised draft could not be started.');
    }catch(e){setError(errorMessage(e));setRetryAvailable(true);}finally{setBusy(false);}
  }
  useEffect(()=>{void api<CatalogEntry[]>('/lessons').then(items=>{setLessons(items);setSelected(items.find(i=>i.preview.version===2)?.id||'');}).catch(e=>setError(errorMessage(e)));},[]);
  useEffect(()=>{
    if(!selected)return;
    let active=true;
    const refresh=():void=>{
      void api<ReviewState>(`/owner/lessons/${encodeURIComponent(selected)}/reviews`).then(s=>{if(active){setState(s);setError('');}}).catch(e=>{if(active)setError(errorMessage(e));});
    };
    refresh();window.addEventListener('inside:learning-path-changed',refresh);
    return ()=>{active=false;window.removeEventListener('inside:learning-path-changed',refresh);};
  },[selected]);
  async function submit(event:FormEvent):Promise<void> {
    event.preventDefault();
    if(!state||state.lesson_id!==selected)return;
    if(gate==='learning'&&scores.some(row=>[row.baseline,row.causal,row.transfer].some(value=>value===''))){setError('Record all observed scores, including the initial baseline. Do not guess missing results.');return;}
    setBusy(true);setError('');
    try{
      const updated=await api<ReviewState>(`/owner/lessons/${encodeURIComponent(selected)}/reviews`,{spec_sha256:state.spec_sha256,video_sha256:state.video_sha256,bundle_sha256:state.bundle_sha256,gate,reviewer,method:'human',decision,evidence,independent,real_device:realDevice,device,scores:gate==='learning'?scores.map((row,i)=>({participant:`anon-${i+1}`,baseline:Number(row.baseline),causal:Number(row.causal),transfer:Number(row.transfer),retention:row.retention===''?null:Number(row.retention)})):[]});
      setState(updated);setEvidence('');window.dispatchEvent(new Event('inside:learning-review-changed'));
    }catch(e){setError(errorMessage(e));}finally{setBusy(false);}
  }
  return <section className="review-workbench"><h2>Lesson quality workbench</h2><p>Record evidence for one exact lesson and video revision. Tests, technical review, actual-phone craft and beginner understanding are separate gates.</p>
    <label>Lesson<select value={selected} onChange={e=>{setSelected(e.target.value);setState(null);setRetryAvailable(false);}}>{lessons.map(l=><option value={l.id} key={l.id}>{l.title}</option>)}</select></label>
    {error&&<p role="alert" className="error">{error}</p>}
    {state&&state.lesson_id===selected&&<><p><strong>{state.ready?'Owner-recorded release requirements passed':'Quality review remains open'}</strong></p>{state.bundle_sha256&&<p className="muted">Reviews bind to this complete learning path, including its core and branches.</p>}{state.bundle_issues.map(issue=><p className="error" key={issue}>{issue}</p>)}<ul>{gateNames.map(name=><li key={name}>{state.gates[name]?'✓':'○'} {name}</li>)}</ul><p className="muted">{state.recording_note}</p>
      {state.spec_version===3 ? <p>Native artwork revisions use the local production workflow and enter as separately reviewed drafts. Paid schematic revision cannot preserve this artwork.</p> :
        <details><summary>Create the next teaching iteration</summary><p>This creates a new draft using the configured provider and reserves up to ${reserve.toFixed(2)} from the existing AI budget. The old lesson and its private conversations remain available. The author uses any available automated editorial critique to guide this iteration. New drafts require fresh quality evidence.</p><button disabled={busy} onClick={()=>void revise()}>Generate revised teaching draft</button>{retryAvailable&&error&&<button disabled={busy} onClick={()=>void revise(true)}>Start another attempt using budget</button>}</details>}
      <details><summary>Record a review or learning session</summary><form onSubmit={e=>void submit(e)}>
        <label>Review type<select value={gate} onChange={e=>setGate(e.target.value as Gate)}>{gateNames.map(name=><option key={name}>{name}</option>)}</select></label>
        <label>Human reviewer<input required minLength={2} maxLength={100} value={reviewer} onChange={e=>setReviewer(e.target.value)}/></label>
        <label>Decision<select value={decision} onChange={e=>setDecision(e.target.value as 'pass'|'needs-work')}><option value="needs-work">Needs work / incomplete evidence</option><option value="pass">Pass based on observed evidence</option></select></label>
        <label>Evidence and review scope<textarea required minLength={20} maxLength={1200} value={evidence} onChange={e=>setEvidence(e.target.value)} placeholder="Reference the checked artifacts, source review, device walk or anonymized test session. Do not enter private learner answers."/></label>
        {gate==='technical'&&<label><input type="checkbox" checked={independent} onChange={e=>setIndependent(e.target.checked)}/>Independent technical reviewer checked claim support and model limits</label>}
        {gate==='craft'&&<><label><input type="checkbox" checked={realDevice} onChange={e=>setRealDevice(e.target.checked)}/>Walked the lesson on an actual phone</label><label>Device/browser and accessibility checks<input maxLength={120} value={device} onChange={e=>setDevice(e.target.value)}/></label></>}
        {gate==='learning'&&<><p>0: wrong/misconception. 1: correct direction without cause. 2: correct causal reasoning. Baseline 2 means the learner already knew the explanation and does not count toward the five-beginner learning gate.</p><div className="table-scroll"><table><thead><tr><th>Anonymous learner</th><th>Baseline</th><th>Teach-back</th><th>Transfer</th><th>Next-day transfer (optional)</th></tr></thead><tbody>{scores.map((row,i)=><tr key={i}><td>{i+1}</td>{(['baseline','causal','transfer','retention'] as const).map(field=><td key={field}><select aria-label={`Learner ${i+1} ${field}`} required={field!=='retention'} value={row[field]} onChange={e=>setScores(scores.map((r,j)=>j===i?{...r,[field]:e.target.value}:r))}><option value="">Unmeasured</option>{[0,1,2].map(score=><option key={score}>{score}</option>)}</select></td>)}</tr>)}</tbody></table></div><button type="button" disabled={scores.length>=30} onClick={()=>setScores([...scores,{baseline:'',causal:'',transfer:'',retention:''}])}>Add another learner</button></>}
        {gate==='release'&&!state.can_release&&<p>Release requires the other four gates first. A fresh revision requires fresh artifact-bound evidence.</p>}
        <button disabled={busy||(gate==='release'&&decision==='pass'&&!state.can_release)}>{busy?'Recording…':'Record review'}</button>
      </form></details>
      <details><summary>Review history ({state.records.length})</summary>{state.records.map((r,i)=><div key={i}><strong>{r.gate} · {r.decision} · {r.reviewer}</strong><p>{r.evidence}</p></div>)}</details>
    </>}
  </section>;
}
