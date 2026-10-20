import { useId } from 'react';
import type { ReactElement } from 'react';
import outside from '../../public/figures/ac-outside.svg?raw';
import inside from '../../public/figures/ac-inside.svg?raw';
declare const __AC_SCENE_HASH__:string;
export const acSceneHash=__AC_SCENE_HASH__;

export function Cutaway({context='outside',focus,onSelect}:{readonly context?:'outside'|'inside'|'none';readonly focus?:string;readonly onSelect?:(id:string)=>void}):ReactElement {
  const id=useId().replaceAll(':','');
  // Only these two bundled, author-controlled vector sources can reach this sink.
  // Model/user data never becomes markup. Namespace definitions across catalog figures.
  const frames:Record<string,string>={evaporator:'90 90 480 460',compressor:'535 170 500 460',condenser:'535 100 500 530',expansion:'90 320 700 310'};
  let source=(context==='inside'?inside:outside).replaceAll('id="ac-',`id="${id}-ac-`).replaceAll('url(#ac-',`url(#${id}-ac-`);
  if(focus&&frames[focus])source=source.replace('viewBox="90 90 950 540"',`viewBox="${frames[focus]}"`).replace('<svg ',`<svg data-focus="${focus}" `);
  return <div className={`ce-context ${onSelect?'interactive':''}`} onClick={onSelect?e=>{const node=e.target instanceof Element?e.target.closest('[data-core]'):null;const target=node?.getAttribute('data-core');if(target&&frames[target])onSelect(target);}:undefined} dangerouslySetInnerHTML={{__html:source}}/>;
}
