import { useEffect, useState } from 'react';
import type { ReactElement } from 'react';
import { api, errorMessage } from './api';
export interface TopicRequest { id:string;question:string;status:'requested'|'planned'|'working'|'available'|'declined';lesson_id:string|null;updated_at:number }
interface Update {id:string;title:string;question:string;lesson_id:string|null;available:boolean;read:boolean;at:number}
export function Requests({online,guest=false}:{readonly online:boolean;readonly guest?:boolean}):ReactElement {
  const [requests,setRequests]=useState<TopicRequest[]>([]),[updates,setUpdates]=useState<Update[]>([]);
  const [error,setError]=useState(''),[loading,setLoading]=useState(true),[refresh,setRefresh]=useState(0);
  useEffect(()=>{
    if(!online)return;
    let active=true;
    void Promise.all([api<TopicRequest[]>('/requests'),api<Update[]>('/notifications')]).then(([r,u])=>{
      if(active){setRequests(r);setUpdates(u);setError('');setLoading(false);}
    }).catch(e=>{if(active){setError(errorMessage(e));setLoading(false);}});
    return()=>{active=false;};
  },[online,refresh]);
  if(!online)return <section><h1>Your requests and updates</h1><p>Reconnect to check progress. Saved explanations still work offline.</p></section>;
  return <section className="request-inbox"><h1>Your requests and updates</h1>
    <p>Requests help us choose what to explain next. They never spend your AI credits.</p>
    {guest&&<p className="muted">Your requests and updates are saved for this browser. Return here to check them.</p>}
    <button disabled={loading} onClick={()=>{setLoading(true);setError('');setRefresh(value=>value+1);}}>Refresh updates</button>
    {error&&<p role="alert" className="error">{error}</p>}{loading&&<p role="status">Checking your updates…</p>}
    <h2>Updates</h2>{!loading&&!error&&!updates.length&&<p className="muted">We’ll post an update here when an explanation you requested is released.</p>}
    {updates.map(update=><article key={update.id} className="request-item"><strong>{update.title}{!update.read?' · New':''}</strong>
      <p>{update.question}</p>{update.available&&update.lesson_id?<a href={`#/lesson/${update.lesson_id}`} onClick={()=>{
        void api(`/notifications/${update.id}/read`,{}).catch(e=>setError(errorMessage(e)));
      }}>Open explanation</a>:<p>This explanation is being reviewed again. Your request is still saved.</p>}</article>)}
    <h2>What you requested</h2>{!loading&&!error&&!requests.length&&<p className="muted">No requests yet. Ask about a system from the library page.</p>}
    {requests.map(request=><article className="request-item" key={request.id}><strong>{request.question}</strong>
      <p>{({requested:'Request received',planned:'Planned',working:'Being prepared',available:'Available',declined:'Not currently planned'})[request.status]}</p>
      {request.status==='available'&&request.lesson_id&&<a href={`#/lesson/${request.lesson_id}`}>Open explanation</a>}
    </article>)}
  </section>;
}
