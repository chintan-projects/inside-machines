/** Trusted physical artwork; poses, causal rules and labels remain lesson data. */
import { useId } from 'react';
import type { ReactElement } from 'react';
import type { LessonSpec } from '../contracts';
import fan from '../../public/figures/vacuum-fan.svg?raw';
import nozzle from '../../public/figures/vacuum-nozzle.svg?raw';
import bag from '../../public/figures/vacuum-bag.svg?raw';
import context from '../../public/figures/vacuum-context.svg?raw';
declare const __VACUUM_ART_HASH__:string;
export const vacuumArtHash=__VACUUM_ART_HASH__;
interface ArtworkSet {readonly revisions:readonly string[];readonly scenes:readonly string[];readonly context:string}
const sets:Readonly<Record<string,ArtworkSet>>={[vacuumArtHash]:{revisions:['bagged-vacuum-ce-2','bagged-vacuum-ce-3','bagged-vacuum-ce-4','bagged-vacuum-ce-5'],scenes:[fan,nozzle,bag],context}};
export function hasSectionArtwork(spec:LessonSpec):boolean {
 const set=sets[spec.teaching?.renderer_fingerprint||''];
 return !!set&&set.revisions.includes(spec.canonical)&&set.scenes.length===spec.stages.length;
}
interface Artwork {readonly markup:string;readonly replaced:ReadonlySet<string>}
export function sectionArtwork(spec:LessonSpec,index:number,namespace:string):Artwork|undefined {
  if(!hasSectionArtwork(spec))return undefined;
  const set=sets[spec.teaching?.renderer_fingerprint||''];
  const source=index===-1?set.context:set.scenes[index];
  if(!source)return undefined;
  const replaced=new Set((source.match(/data-replaces="([^"]*)"/)?.[1]||'').split(/\s+/).filter(Boolean));
  const markup=source.slice(source.indexOf('>')+1,source.lastIndexOf('</svg>'))
    .replaceAll(/id="([^"]+)"/g,`id="${namespace}-$1"`).replaceAll(/url\(#([^)]+)\)/g,`url(#${namespace}-$1)`);
  return {markup,replaced};
}
export function SectionContext({spec}:{readonly spec:LessonSpec}):ReactElement {
  const id=useId().replaceAll(':','');
  const art=sectionArtwork(spec,-1,id);
  if(!art)return <p>This earlier drawing is preserved in the original video.</p>;
  return <div className="ce-context"><svg viewBox="0 0 900 540" role="img" aria-label="Whole system: nozzle and hose lead to the porous bag, then the fan and outlet." dangerouslySetInnerHTML={{__html:art.markup}}/></div>;
}
