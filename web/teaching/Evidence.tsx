import type { ReactElement } from 'react';
import type { LessonSpec } from '../contracts';
import type { Beat } from './contracts';

export function Evidence({spec,beat}:{readonly spec:LessonSpec;readonly beat:Beat}):ReactElement {
  const teaching=spec.teaching;
  if(!teaching) return <></>;
  return <details className="ce-evidence"><summary>Evidence, assumptions &amp; details</summary>
    <h3>What this step says</h3><p>{spec.stages[beat.stage].explanation}</p><p><strong>Why:</strong> {spec.stages[beat.stage].cause}</p>
    <h3>Claims and sources</h3><ul>{teaching.claims.filter(c=>beat.claims.includes(c.id)).map(c=><li key={c.id}><p>{c.statement}</p><a href={spec.sources[c.source].url} target="_blank" rel="noreferrer">{spec.sources[c.source].title}</a><p className="ce-source-locator">{c.locator} · {c.scope==='inference'?'Application of the source’s principle':c.scope==='documented-model'?'Documented model detail':'Generic principle'}</p><p>{c.limitation}</p></li>)}</ul>
    <h3>What is simplified</h3><ul>{spec.assumptions.map(a=><li key={a}>{a}</li>)}</ul>
    <p>This is a teaching draft. Source links and automated checks do not establish independent technical review. The voice is computer-generated.</p>
  </details>;
}
