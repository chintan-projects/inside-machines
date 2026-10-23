import { useEffect, useRef, useState } from 'react';
import type { FormEvent, ReactElement } from 'react';
import { ApiError, api, errorMessage } from './api';
import type { RequestResult } from './contracts';
import { DepthAttempts, depthIntentKey } from './depth-attempts';
import type { DepthIntent } from './depth-attempts';

interface Props {
  readonly rootId:string;
  readonly rootTitle:string;
  readonly reserve:number;
  readonly onBusy:(value:boolean)=>void;
}
interface Failure {readonly intent:string;readonly message:string;readonly canStartNew:boolean}
interface Notice {readonly intent:string;readonly message:string}

export function OwnerDepthDraft({rootId,rootTitle,reserve,onBusy}:Props):ReactElement|null {
  const [question,setQuestion]=useState(''),[role,setRole]=useState<DepthIntent['role']>('insight');
  const [busy,setBusy]=useState(false),[failure,setFailure]=useState<Failure|null>(null),[notice,setNotice]=useState<Notice|null>(null);
  const [attempts]=useState(()=>new DepthAttempts());
  const inFlight=useRef(false),mounted=useRef(true);
  const intent:DepthIntent={rootId,role,question:question.trim()};
  const failureHere=failure?.intent===depthIntentKey(intent)?failure:null;
  const noticeHere=notice?.intent===depthIntentKey(intent)?notice:null;
  useEffect(()=>{mounted.current=true;return()=>{mounted.current=false;};},[]);

  async function build(explicitNewAttempt=false):Promise<void> {
    if(inFlight.current||!rootId)return;
    if(intent.question.length<8||intent.question.length>180)return;
    inFlight.current=true;setBusy(true);onBusy(true);setFailure(null);setNotice(null);
    const operation=attempts.operation(intent,explicitNewAttempt);
    try {
      const result=await api<RequestResult>(`/owner/lessons/${encodeURIComponent(rootId)}/depth-drafts`,{
        question:intent.question,role:intent.role,operation,
      });
      if(!mounted.current)return;
      if(result.kind==='job'&&result.job_id)window.location.hash=`/job/${result.job_id}`;
      else if(result.kind==='lesson'&&result.lesson_id)window.location.hash=`/lesson/${result.lesson_id}`;
      else setNotice({intent:depthIntentKey(intent),message:result.message??'The draft was not started. Check the owner budget and provider configuration.'});
    }catch(reason){
      if(mounted.current)setFailure({intent:depthIntentKey(intent),message:errorMessage(reason),
        canStartNew:reason instanceof ApiError&&reason.status===409});
    }finally{
      inFlight.current=false;onBusy(false);if(mounted.current)setBusy(false);
    }
  }
  function submit(event:FormEvent):void {event.preventDefault();void build();}
  if(!rootId)return null;
  return <section aria-labelledby="owner-depth-draft"><h3 id="owner-depth-draft">Build a missing explanation</h3>
    <p>Ask one concrete follow-up to {rootTitle}. The owner pipeline keeps this core’s example and scope.
      The result is a separate review draft; it is never attached or released automatically.</p>
    <form onSubmit={submit}>
      <label>Question to explain<input required minLength={8} maxLength={180} value={question} disabled={busy}
        onChange={event=>{setQuestion(event.target.value);setNotice(null);}} placeholder="Why does this mechanism change the output?"/></label>
      <label>Depth<select value={role} disabled={busy} onChange={event=>{setRole(event.target.value as DepthIntent['role']);setNotice(null);}}>
        <option value="insight">Insight · explain a hidden relationship</option><option value="model">Model · unpack the reasoning</option>
      </select></label>
      <p className="muted">Building reserves ${reserve.toFixed(2)} from the existing owner budget. Replaying or composing existing lessons uses no AI credits.</p>
      {failureHere&&<><p role="alert" className="error">{failureHere.message}</p>
        <p className="muted">Continuing reuses this same operation. A lost response may already have created a job; check Owner generation jobs before starting another funded attempt.</p></>}
      {noticeHere&&<p role="status">{noticeHere.message}</p>}
      <button disabled={busy||intent.question.length<8}>{busy?'Submitting owner draft…':failureHere?'Continue same attempt':`Build depth draft · reserve $${reserve.toFixed(2)}`}</button>
      {failureHere?.canStartNew&&<button type="button" disabled={busy} onClick={()=>void build(true)}>Start a new funded attempt · reserve ${reserve.toFixed(2)}</button>}
    </form>
    <p className="muted">After the job completes, review its actual lesson revision and add that ID to the path JSON above.</p>
  </section>;
}
