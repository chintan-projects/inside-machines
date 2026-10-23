import { useEffect, useRef, useState } from 'react';
import type { ReactElement } from 'react';
import { ApiError, api, errorMessage } from './api';
import { OwnerAttempts } from './owner-attempts';
import type { CatalogEntry, RequestResult } from './contracts';
import type { TopicRequest } from './Requests';
interface QueueItem extends TopicRequest {requesters:number;note:string;job_id?:string}
export function OwnerRequests({reserve}:{readonly reserve:number}):ReactElement {
  const [items,setItems]=useState<QueueItem[]>([]),[lessons,setLessons]=useState<CatalogEntry[]>([]);
  const [error,setError]=useState(''),[busy,setBusy]=useState('');
  const [attempts]=useState(()=>new OwnerAttempts());
  const [failure,setFailure]=useState<{id:string;canStartNew:boolean}|null>(null);
  const inFlight=useRef(false);
  useEffect(()=>{
    let active=true;
    void Promise.all([api<QueueItem[]>('/owner/requests'),api<CatalogEntry[]>('/lessons')]).then(([q,l])=>{
      if(active){setItems(q);setLessons(l);}
    }).catch(e=>{if(active)setError(errorMessage(e));});
    return()=>{active=false;};
  },[]);
  async function update(item:QueueItem):Promise<void> {
    setBusy(item.id);setError('');
    try {await api(`/owner/requests/${item.id}`,{status:item.status,lesson_id:item.lesson_id,note:item.note},'PATCH');}
    catch(e){setError(errorMessage(e));}finally{setBusy('');}
  }
  async function build(item:QueueItem,explicitNewAttempt=false):Promise<void> {
    if(inFlight.current)return;
    inFlight.current=true;setBusy(item.id);setError('');setFailure(null);
    const operation=attempts.operation(item.id,explicitNewAttempt);
    try {
      const result=await api<RequestResult>(`/owner/requests/${item.id}/build`,{operation});
      if(result.kind==='job'&&result.job_id)window.location.hash=`/job/${result.job_id}`;
      else if(result.kind==='lesson'&&result.lesson_id)window.location.hash=`/lesson/${result.lesson_id}`;
      else setError(result.message??'The draft could not be started.');
    }catch(e){
      setError(errorMessage(e));
      setFailure({id:item.id,canStartNew:e instanceof ApiError&&e.status===409});
    }finally{inFlight.current=false;setBusy('');}
  }
  function edit(id:string,change:Partial<QueueItem>):void {setItems(old=>old.map(item=>item.id===id?{...item,...change}:item));}
  return <section className="owner-requests"><h2>Requested explanations</h2>
    <p>Collect interest first. Building is a separate owner action that reserves up to ${reserve.toFixed(2)}. Availability requires the lesson’s release checks.</p>
    {error&&<p role="alert" className="error">{error}</p>}{!items.length&&<p className="muted">New topic requests will appear here. No generation starts automatically.</p>}
    {items.map(item=><article key={item.id} className="request-item"><h3>{item.question}</h3><p>{item.requesters} interested {item.requesters===1?'person':'people'}</p>
      <div className="request-fields"><label>Status<select value={item.status} onChange={e=>edit(item.id,{status:e.target.value as QueueItem['status']})}>
        <option value="requested">Received</option><option value="planned">Planned</option><option value="working">Preparing</option><option value="available">Available after release</option><option value="declined">Not planned</option></select></label>
      <label>Explanation to deliver<select value={item.lesson_id??''} onChange={e=>edit(item.id,{lesson_id:e.target.value||null})}><option value="">Choose a revision</option>{lessons.map(l=><option key={l.id} value={l.id}>{l.title}</option>)}</select></label>
      <label>Private production note<input value={item.note} maxLength={600} onChange={e=>edit(item.id,{note:e.target.value})}/></label></div>
      <button disabled={!!busy} onClick={()=>void update(item)}>{busy===item.id?'Working…':'Save request status'}</button>{' '}
      <button disabled={!!busy} onClick={()=>void build(item)}>{failure?.id===item.id?'Continue same attempt':`Build owner draft · reserve ≤ $${reserve.toFixed(2)}`}</button>
      {failure?.id===item.id&&<p className="muted">A lost response may already have started a build. Continuing keeps the same operation; check build progress before funding another attempt.</p>}
      {failure?.id===item.id&&failure.canStartNew&&<button disabled={!!busy} onClick={()=>void build(item,true)}>Start a new funded attempt · reserve ${reserve.toFixed(2)}</button>}
      {item.job_id&&<a href={`#/job/${item.job_id}`}>View build progress</a>}
    </article>)}
  </section>;
}
