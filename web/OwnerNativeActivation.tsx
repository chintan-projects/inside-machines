import { useEffect, useState, type ReactElement } from 'react';
import { api, errorMessage } from './api';
import type { CatalogEntry } from './contracts';

interface Release {lesson_id:string;spec_sha256:string;video_sha256:string;bundle_sha256:string;ready:boolean}
interface Activated {lesson_id:string;replaced_ids:string[];reused:boolean}

/** Adoption is explicit and artifact-bound, after the separate human release decision. */
export function OwnerNativeActivation({lesson,candidates}:{readonly lesson:CatalogEntry;readonly candidates:readonly CatalogEntry[]}):ReactElement {
  const [state,setState]=useState<Release|null>(null),[previous,setPrevious]=useState('');
  const [error,setError]=useState(''),[notice,setNotice]=useState(''),[busy,setBusy]=useState(false),[attempt,setAttempt]=useState(0);
  useEffect(()=>{
    let active=true;
    const refresh=():void=>{
      void api<Release>(`/owner/lessons/${encodeURIComponent(lesson.id)}/reviews`)
        .then(value=>{if(active){setState(value);setError('');}}).catch(reason=>{if(active)setError(errorMessage(reason));});
    };
    refresh();window.addEventListener('inside:learning-review-changed',refresh);
    return()=>{active=false;window.removeEventListener('inside:learning-review-changed',refresh);};
  },[lesson.id,attempt]);
  async function activate():Promise<void> {
    if(!state?.ready||state.lesson_id!==lesson.id||!previous)return;
    setBusy(true);setError('');setNotice('');
    try {
      const result=await api<Activated>(`/owner/lessons/${encodeURIComponent(lesson.id)}/activate`,{
        spec_sha256:state.spec_sha256,video_sha256:state.video_sha256,bundle_sha256:state.bundle_sha256,expected_old_ids:[previous],
      });
      setNotice(`${result.reused?'Already active':'Activated'}: ${lesson.title}. Earlier media and conversations are preserved.`);
      window.dispatchEvent(new Event('inside:library-activated'));
    }catch(reason){setError(errorMessage(reason));}finally{setBusy(false);}
  }
  const eligible=candidates.filter(item=>item.id!==lesson.id&&!item.depth_parent);
  const old=eligible.find(item=>item.id===previous);
  return <section><h3>Use this reviewed artwork in the library</h3>
    <p>Importing and composing a draft do not replace the current explanation. Activate this exact revision after its complete path passes release review.</p>
    {state&&!state.ready&&<p>Activation is held. Complete the engineering, technical, craft, learning and release reviews first.</p>}
    <label>Explanation to replace<select value={previous} disabled={busy} onChange={event=>{setPrevious(event.target.value);setNotice('');}}>
      <option value="">Choose the current explanation</option>{eligible.map(item=><option key={item.id} value={item.id}>{item.title} · {item.id}</option>)}
    </select></label>
    {old&&<p><strong>{old.title}</strong> ({old.id}) will lead to <strong>{lesson.title}</strong> ({lesson.id}). Earlier media and private conversations stay with their original revision.</p>}
    {error&&<p role="alert" className="error">{error}</p>}{notice&&<p role="status">{notice}</p>}
    <button disabled={busy||!state?.ready||!old} onClick={()=>void activate()}>{busy?'Activating…':'Replace selected explanation'}</button>
    <button disabled={busy} onClick={()=>setAttempt(value=>value+1)}>Refresh release status</button>
  </section>;
}
