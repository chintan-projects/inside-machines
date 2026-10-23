import { useEffect, useState } from 'react';
import type { ReactElement } from 'react';
import { api, errorMessage } from './api';
import { previewChange, type PublicPreviewState } from './public-preview';

export function OwnerPublicPreview({lessonId}:{readonly lessonId:string}):ReactElement {
  const [state,setState]=useState<PublicPreviewState|null>(null),[attempt,setAttempt]=useState(0);
  const [loading,setLoading]=useState(true),[busy,setBusy]=useState(false),[error,setError]=useState(''),[notice,setNotice]=useState('');
  const endpoint=`/owner/lessons/${encodeURIComponent(lessonId)}/public-preview`;
  useEffect(()=>{
    let active=true,request=0;
    const refresh=():void=>{
      const current=++request;setLoading(true);
      void api<PublicPreviewState>(endpoint).then(value=>{
        if(active&&current===request){setState(value);setError('');}
      }).catch(reason=>{if(active&&current===request)setError(errorMessage(reason));})
        .finally(()=>{if(active&&current===request)setLoading(false);});
    };
    refresh();window.addEventListener('inside:learning-path-changed',refresh);
    window.addEventListener('inside:learning-review-changed',refresh);
    return()=>{active=false;window.removeEventListener('inside:learning-path-changed',refresh);window.removeEventListener('inside:learning-review-changed',refresh);};
  },[endpoint,attempt]);
  async function change(enabled:boolean):Promise<void> {
    if(!state||state.lesson_id!==lessonId)return;
    const body=previewChange(state,enabled);if(!body)return;
    setBusy(true);setError('');setNotice('');
    try {
      await api(endpoint,body,'PUT');
      setState(await api<PublicPreviewState>(endpoint));
      setNotice(enabled?'This exact lesson and path are shared as a public review draft.':'Public preview permission removed.');
      window.dispatchEvent(new Event('inside:public-preview-changed'));
    } catch(reason){setError(errorMessage(reason));}
    finally{setBusy(false);}
  }
  return <section className="owner-public-preview"><h3>Share a public review draft</h3>
    <p>Let anyone explore this exact lesson and its attached path. Public preview keeps the review-draft label and is separate from quality approval and library activation.</p>
    {loading&&<p role="status">Checking the current preview permission…</p>}
    {state?.notice&&<p className="muted">{state.notice}</p>}
    {state?.enabled&&<p role="status">Public preview is on for this exact lesson and path.</p>}
    {state?.preview?.enabled&&!state.enabled&&<p className="notice">The earlier preview permission no longer matches the current artifact. You can remove it or share the current valid candidate.</p>}
    {state?.issue&&<p className="notice">{state.issue}</p>}
    {error&&<p role="alert" className="error">{error}</p>}{notice&&<p role="status">{notice}</p>}
    <div className="preview-actions"><button disabled={busy||loading||!state?.candidate||state.enabled} onClick={()=>void change(true)}>Make this review draft public</button>
      {state?.preview?.enabled&&<button disabled={busy||loading} onClick={()=>void change(false)}>Remove public preview</button>}
      <button disabled={busy||loading} onClick={()=>setAttempt(value=>value+1)}>Refresh preview status</button></div>
  </section>;
}
