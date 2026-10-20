import { useRef } from 'react';
import type { ReactElement } from 'react';
import type { LessonSpec } from '../contracts';
import { Graphic } from './Graphic';
interface Props {readonly spec:LessonSpec;readonly seconds:number;readonly scenario?:string;readonly still:boolean;readonly progress:number}
export function Detail({spec,seconds,scenario,still,progress}:Props):ReactElement {
  const dialog=useRef<HTMLDialogElement>(null);
  const graphic=<Graphic spec={spec} seconds={seconds} scenario={scenario} still={still}/>;
  return <figure className="ce-detail">{graphic}<figcaption>{progress<.01?'Before the change':progress>.99?'After the change':'Follow what changes'}</figcaption>
    <button className="ce-enlarge" onClick={()=>dialog.current?.showModal()}>Enlarge diagram</button>
    <dialog ref={dialog} className="ce-diagram-dialog" aria-label="Enlarged causal diagram"><header><h2>Inspect the change</h2><button onClick={()=>dialog.current?.close()}>Close</button></header><p>Scroll across to inspect the labels and mechanism.</p><div tabIndex={0} role="region" aria-label="Pan enlarged diagram">{graphic}</div></dialog>
  </figure>;
}
