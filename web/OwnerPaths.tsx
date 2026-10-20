import { useEffect, useState } from 'react';
import type { ReactElement } from 'react';
import { api, errorMessage } from './api';
import type { CatalogEntry } from './contracts';
import type { LearningPath } from './studio/path-contract';
import { parsePath } from './studio/path-contract';
import { OwnerDepthDraft } from './OwnerDepthDraft';

interface PathRecord {bundle_sha256:string;path_sha256:string;path:LearningPath;created_at:number}
interface History {root_lesson_id:string;current_bundle_sha256:string;records:PathRecord[]}
interface Attached {bundle_sha256:string;review_required:boolean;reused:boolean}

export function OwnerPaths({reserve}:{readonly reserve:number}):ReactElement {
  const [lessons,setLessons]=useState<CatalogEntry[]>([]),[selected,setSelected]=useState('');
  const [history,setHistory]=useState<History|null>(null),[source,setSource]=useState('');
  const [busy,setBusy]=useState(false),[error,setError]=useState(''),[notice,setNotice]=useState('');
  const [allowDrafts,setAllowDrafts]=useState(false);
  const [depthBusy,setDepthBusy]=useState(false);
  useEffect(()=>{
    let active=true;
    void api<CatalogEntry[]>('/lessons').then(rows=>{if(active)setLessons(rows.filter(row=>row.preview.version===2));})
      .catch(reason=>{if(active)setError(errorMessage(reason));});
    return()=>{active=false;};
  },[]);
  useEffect(()=>{
    if(!selected)return;
    let active=true;
    void Promise.all([
      api<History>(`/owner/lessons/${encodeURIComponent(selected)}/learning-paths`),
      api<{path:LearningPath}>(`/learning-paths/${encodeURIComponent(selected)}`),
    ]).then(([saved,bundle])=>{if(active){setHistory(saved);setSource(JSON.stringify(bundle.path,null,2));}})
      .catch(reason=>{if(active)setError(errorMessage(reason));});
    return()=>{active=false;};
  },[selected]);
  async function attach():Promise<void> {
    if(!history||history.root_lesson_id!==selected)return;
    setBusy(true);setError('');setNotice('');
    try {
      const parsed:unknown=JSON.parse(source);
      const path=parsePath(parsed,lessons.map(row=>row.id));
      const result=await api<Attached>(`/owner/lessons/${encodeURIComponent(selected)}/learning-paths`,{
        path,expected_bundle_sha256:history.current_bundle_sha256,allow_review_drafts:allowDrafts,
      });
      setHistory(await api<History>(`/owner/lessons/${encodeURIComponent(selected)}/learning-paths`));
      setLessons(rows=>rows.map(row=>row.id===selected?{...row,review_needed:result.review_required}:row));
      window.dispatchEvent(new Event('inside:learning-path-changed'));
      setNotice(result.review_required?'Path saved. The complete bundle now needs fresh quality reviews before release.':'This exact path is already reviewed and released.');
    }catch(reason){setError(errorMessage(reason));}finally{setBusy(false);}
  }
  return <section aria-labelledby="learning-path-editor"><h2 id="learning-path-editor">Compose a learning path</h2>
    <p>Connect an existing core to existing insight or model lessons. This uses no AI credits.
      Each node keeps its own explanation, media and questions. A changed path requires fresh review of the complete bundle.</p>
    <details><summary>Owner path editor</summary>
      <label>Core revision<select value={selected} onChange={event=>{setHistory(null);setSource('');setError('');setNotice('');setAllowDrafts(false);setSelected(event.target.value);}} disabled={busy||depthBusy}>
        <option value="">Choose a core lesson</option>{lessons.map(lesson=><option key={lesson.id} value={lesson.id}>{lesson.title} · {lesson.id}</option>)}
      </select></label>
      {error&&<p role="alert" className="error">{error}</p>}{notice&&<p role="status">{notice}</p>}
      {selected&&!history&&!error&&<p role="status">Loading the current path and its immutable history…</p>}
      {history&&<><p>The first node must reference {selected}. Add at most seven distinct existing leaf revisions;
        roles are core, insight and model. Keep prerequisite and next-node references acyclic.</p>
        <p><a href={`#/lesson/${selected}`}>Preview the current learning path</a></p>
        <label>Learning-path JSON<textarea rows={18} maxLength={40000} spellCheck={false} value={source} onChange={event=>setSource(event.target.value)} disabled={busy}/></label>
        <label><input type="checkbox" checked={allowDrafts} onChange={event=>setAllowDrafts(event.target.checked)} disabled={busy}/>Allow structurally valid review drafts with completed media</label>
        <p className="muted">Draft composition lets you review the whole experience. Publication stays held until every branch and the complete bundle pass their separate quality gates.</p>
        <button disabled={busy||depthBusy||!source} onClick={()=>void attach()}>{busy?'Validating and saving…':allowDrafts?'Attach review draft':'Attach path and begin bundle review'}</button>
        <p className="muted">A short core alone is still valid. Composing existing lessons does not author content or approve its quality. Use the separate owner build below when a branch is missing.</p>
        <details><summary>Available immutable lesson IDs</summary><ul>{lessons.map(lesson=><li key={lesson.id}>{lesson.id} · {lesson.review_needed?'review pending':'released'}</li>)}</ul></details>
        <details><summary>Preserved path history ({history.records.length})</summary>{history.records.map(record=><p key={record.bundle_sha256}>
          <button disabled={busy} onClick={()=>setSource(JSON.stringify(record.path,null,2))}>Load {new Date(record.created_at*1000).toLocaleString()}</button>
          <small>{record.bundle_sha256===history.current_bundle_sha256?'Current path · ':''}{record.bundle_sha256.slice(0,12)} · loading a record does not attach it</small>
        </p>)}</details>
      </>}
      <OwnerDepthDraft rootId={selected} rootTitle={lessons.find(lesson=>lesson.id===selected)?.title??selected} reserve={reserve} onBusy={setDepthBusy}/>
    </details>
  </section>;
}
