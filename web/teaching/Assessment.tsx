import { useState } from 'react';
import type { ReactElement } from 'react';
import type { Assessment as Task } from './contracts';

export function Prediction({task,onContinue}:{readonly task:Task;readonly onContinue:(choice:number|null)=>void}):ReactElement {
  const [choice,setChoice]=useState<number|null>(null);
  return <section className="ce-prediction" aria-label="Make a prediction">
    <span className="ce-overline">Before we look inside</span><h2>{task.prompt}</h2>
    <p>Take a guess. We’ll build an explanation you can use to test it.</p>
    <div className="ce-choice-list" role="group" aria-label="Your prediction">{task.choices.map((option,i)=><button key={option} aria-pressed={choice===i} onClick={()=>setChoice(i)}>{option}</button>)}</div>
    <p className="ce-private-note">Your selected answer stays on this screen.</p>
    <button className="ce-primary" onClick={()=>onContinue(choice)}>{choice===null?'Show me how it works':'Test my prediction'}</button>
  </section>;
}
export function Transfer({task,teachBack,reasoning,onReveal}:{readonly task:Task;readonly teachBack:string;readonly reasoning:readonly string[];readonly onReveal?:()=>void}):ReactElement {
  const [choice,setChoice]=useState<number|null>(null),[revealed,setRevealed]=useState(false),[answer,setAnswer]=useState('');
  return <section className="ce-transfer" aria-label="Try a new situation">
    <span className="ce-overline">Make the idea yours</span><h2>{task.prompt}</h2>
    <div className="ce-choice-list" role="group" aria-label="Transfer prediction">{task.choices.map((option,i)=><button key={option} aria-pressed={choice===i} onClick={()=>{setChoice(i);setRevealed(false);}}>{option}</button>)}</div>
    <label className="ce-answer-label">Why do you think that?<textarea maxLength={1000} value={answer} onChange={e=>setAnswer(e.target.value)} placeholder="Explain it in your own words (optional)"/></label>
    <p className="ce-private-note">Only on this screen. This answer isn’t stored or sent to AI.</p>
    <button className="ce-primary" onClick={()=>{if(!revealed)onReveal?.();setRevealed(!revealed);}} aria-expanded={revealed}>{revealed?'Hide the explanation':choice===null?'Show the explanation':'Compare my reasoning'}</button>
    {revealed && <div className="ce-reveal" role="status"><h3>{choice===null?'Follow the cause':choice===task.correct?'That prediction fits. Here is why.':'Let’s trace what changes.'}</h3><p>{task.explanation}</p><h4>Check your explanation</h4><ul>{task.reasoning.map(r=><li key={r}>{r}</li>)}</ul><p>Getting the direction right is a start. Being able to explain these causes is the useful part.</p></div>}
    <details className="ce-teachback"><summary>Explain the whole system to someone</summary><p>{teachBack}</p><p>Try saying it without the technical names, then check for these ideas:</p><ul>{reasoning.map(r=><li key={r}>{r}</li>)}</ul></details>
  </section>;
}
