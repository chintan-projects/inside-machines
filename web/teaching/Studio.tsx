import { useRef, useState } from 'react';
import type { ReactElement } from 'react';
import { Headphones, Pause, RotateCcw, ArrowLeft, Play } from 'lucide-react';
import type { Answer, LegacyLesson as Lesson, Member } from '../contracts';
import type { TeachingSpec } from './contracts';
import { ChatPanel, FeedbackPanel } from '../LessonDiscussion';
import { LessonSaveButton, useLessonAssets } from '../useLessonAssets';
import { Scene } from '../Scene';
import { playingMediaTime } from '../lessonTimeline';
import { useMedia } from '../ac/useGuide';
import { usePlayer } from './usePlayer';
import { scenarioFor } from './state';
import { Cutaway, acSceneHash } from './Context';
import { Detail } from './Detail';
import { hasSectionArtwork } from './Sections';
import { Prediction, Transfer } from './Assessment';
import { Evidence } from './Evidence';
import { api, errorMessage } from '../api';
import './studio.css';

interface Props { readonly lesson:Lesson;readonly member:Member;readonly online:boolean }
export function TeachingStudio(props:Props):ReactElement {
  const teaching=props.lesson.spec.teaching;
  if(!teaching || !props.lesson.spec.graphics?.length) return <p role="alert" className="error">This lesson’s teaching data is incomplete. Reconnect and reopen it.</p>;
  if(teaching.renderer==='ac-cutaway-v2'&&teaching.renderer_fingerprint!==acSceneHash)return <EarlierRevision {...props}/>;
  if(teaching.renderer==='authored-sections-v1'&&!hasSectionArtwork(props.lesson.spec))return <EarlierRevision {...props}/>;
  return <Studio {...props} teaching={teaching}/>;
}
function EarlierRevision({lesson,member,online}:Props):ReactElement {
  const assets=useLessonAssets(lesson,member,online);
  return <article className="ce-studio"><h1>{lesson.spec.question}</h1><p>This earlier explanation is preserved in its video and text.</p><video controls playsInline preload="metadata" src={assets.videoUrl}><track kind="captions" src={assets.captionUrl} srcLang="en" label="English captions"/></video>{lesson.spec.stages.map(s=><section key={s.title}><h2>{s.title}</h2><p>{s.explanation}</p></section>)}</article>;
}
function Studio({lesson,member,online,teaching}:{readonly teaching:TeachingSpec}&Props):ReactElement {
  const audio=useRef<HTMLAudioElement>(null),video=useRef<HTMLVideoElement>(null),transfer=useRef<HTMLElement>(null);
  const reduced=useMedia('(prefers-reduced-motion:reduce)'), player=usePlayer(lesson,member,audio,reduced);
  const assets=useLessonAssets(lesson,member,online);
  const [begun,setBegun]=useState(player.seconds>0),[scenarioId,setScenario]=useState<string|undefined>(),[attempt,setAttempt]=useState(0);
  const [consent,setConsent]=useState(false),[countError,setCountError]=useState(''),[prediction,setPrediction]=useState<number|null>(null);
  const {spec}=lesson, {beat,progress}=player, stage=spec.stages[beat.stage],last=beat.stage===spec.stages.length-1;
  const scenario=scenarioFor(spec,beat,scenarioId), options=teaching.scenarios.filter(s=>s.beat===beat.id);
  const showContext=(context:'outside'|'inside'|'none'='outside'):ReactElement=>teaching.renderer==='ac-cutaway-v2'?<Cutaway context={context} onSelect={begun?inspect:undefined}/>:<Scene spec={spec} seconds={player.seconds} selected={stage.focus}/>;
  function jump(index:number):void {
    video.current?.pause();setScenario(undefined);player.jump(index);
    requestAnimationFrame(()=>document.querySelector('.ce-workspace')?.scrollIntoView({behavior:reduced?'instant':'smooth',block:'start'}));
  }
  function inspect(id:string):void {
    const index=spec.stages.findIndex(s=>s.focus===id);
    if(index>=0)jump(index);
  }
  function show(answer:Answer):void {
    setBegun(true);
    if(answer.stage!==null)jump(answer.stage);else if(answer.part)inspect(answer.part);
    document.querySelector('.ce-workspace')?.scrollIntoView({behavior:reduced?'instant':'smooth',block:'start'});
  }
  function reset():void {jump(0);setBegun(false);setAttempt(attempt+1);setPrediction(null);requestAnimationFrame(()=>window.scrollTo({top:0,behavior:reduced?'instant':'smooth'}));}
  function count(kind:'prediction_skipped'|'prediction_attempted'|'change_replayed'|'transfer_revealed'|'confusing_beat'):void {
    if(!consent||!online)return;
    void api(`/lessons/${encodeURIComponent(lesson.id)}/learning-event`,{kind,beat:beat.id,consent:true}).catch(e=>setCountError(errorMessage(e)));
  }
  async function listen():Promise<void> {video.current?.pause();await player.listen();}
  function primary():void {
    video.current?.pause();
    if(player.moving)player.scrub(1);
    else if(progress<.99)player.change();
    else if(!last)jump(beat.stage+1);
    else transfer.current?.scrollIntoView({behavior:reduced?'instant':'smooth',block:'start'});
  }
  return <article className="ce-studio">
    <header className="ce-heading"><div><p>{spec.family}</p><h1>{spec.question}</h1><span className="ce-review-status">{lesson.review_needed?'Teaching draft · review in progress':'Reviewed generic explanation'}</span></div><LessonSaveButton online={online} saved={assets.saved} saving={assets.saving} save={assets.save}/></header>
    {lesson.superseded_by&&<p className="ce-revision-note">This earlier draft is preserved with your conversation. <a href={`#/lesson/${lesson.superseded_by}`}>Open the revised explanation</a></p>}
    {(player.error||assets.saveError)&&<p className="error" role="alert">{player.error||assets.saveError}</p>}
    {!begun?<div className="ce-intro"><figure>{showContext()}<figcaption>{spec.summary}</figcaption></figure><Prediction key={attempt} task={teaching.prediction} onContinue={choice=>{setPrediction(choice);count(choice===null?'prediction_skipped':'prediction_attempted');setBegun(true);jump(0);}}/></div>:<>
      <section className="ce-workspace" aria-label="Build the explanation">
        <nav className="ce-steps" aria-label="Learning steps"><p>Follow the cause</p><ol>{teaching.beats.map((b,i)=><li key={b.id}><button aria-current={i===beat.stage?'step':undefined} onClick={()=>jump(i)}><span>{i+1}</span>{b.short}</button></li>)}</ol><button className="ce-reset" aria-label="Start over" title="Start over" onClick={reset}><RotateCcw size={15}/>Start over</button></nav>
        <div className="ce-main">
          <div className="ce-instruction"><span className="ce-overline">Step {beat.stage+1} of {spec.stages.length}</span><h2>{stage.title}</h2><p>{beat.bridge}</p></div>
          {options.length>0&&<section className="ce-scenarios" aria-label="Test a different setup"><h3>{teaching.renderer==='ac-cutaway-v2'?'Where does the hot coil release its heat?':'Change one condition'}</h3><div role="group" aria-label="Scenario">{options.map(s=><button key={s.id} aria-pressed={scenario?.id===s.id} onClick={()=>{video.current?.pause();setScenario(s.id);player.change();}}>{s.label}</button>)}</div></section>}
          <div className="ce-visuals">
            <Detail spec={spec} seconds={player.seconds} scenario={scenarioId} still={reduced} progress={progress}/>
          </div>
          {scenario&&options.length>0&&<p className="ce-condition-outcome" role="status">{scenario.outcome}</p>}
          <div className="ce-animation"><span>Before</span><input aria-label="Inspect the change" type="range" min="0" max="1" step=".01" value={progress} onChange={e=>{video.current?.pause();player.scrub(Number(e.target.value));}}/><span>After</span></div>
          <footer className="ce-actions"><button aria-label="Previous learning step" disabled={beat.stage===0} onClick={()=>jump(beat.stage-1)}><ArrowLeft size={18}/></button><button className="ce-primary" onClick={primary}>{player.moving?'Show the result':progress<.99?beat.action:last?'Try a new situation':`Next: ${teaching.beats[beat.stage+1].short}`}</button><button aria-label="Replay this change" onClick={()=>{video.current?.pause();count('change_replayed');player.change();}}><Play size={17}/></button></footer>
          <div className="ce-state-strip" aria-label="Qualitative state">{beat.properties.map(p=><div key={p.name}><span>{p.name}</span><strong>{progress<.01?p.before:progress>.99?p.after:`${p.before} → ${p.after}`}</strong></div>)}</div>
          <p className="ce-static-explanation">{beat.static_explanation}</p>
          {scenario&&options.length>0&&<details className="ce-comparison-note"><summary>Why this changes the result</summary><p>{scenario.explanation}</p><small>Qualitative comparison · schematic paths, not measured predictions</small></details>}
          <details key={beat.id} className="ce-locator" open={last}><summary>See where this fits in the whole system</summary><figure className="ce-machine">{showContext(scenario?.context)}<figcaption>Whole-system locator · use the component buttons to revisit a step</figcaption><div className="ce-components" aria-label="Locate a working component">{teaching.core.map(id=><button key={id} aria-pressed={stage.focus===id} onClick={()=>inspect(id)}>{spec.parts.find(p=>p.id===id)?.name||id}</button>)}</div></figure></details>
        </div>
      </section>
      <div className="ce-playback"><button disabled={!lesson.video_ready||player.loading} onClick={()=>void listen()}>{player.listening?<Pause size={16}/>:<Headphones size={16}/>} {player.loading?'Loading narration…':player.listening?'Pause narration':'Listen to the explanation'}</button><p>{teaching.operation_note}</p></div>
      {last&&<section ref={transfer} className="ce-learning-finish"><h2>Revisit your first prediction</h2><p>{teaching.prediction.prompt}</p>{prediction!==null&&<p>Your first prediction: <strong>{teaching.prediction.choices[prediction]}</strong></p>}<details><summary>Reveal and trace the result</summary><p>{teaching.prediction.explanation}</p></details><Transfer key={attempt} task={teaching.transfer} teachBack={teaching.teach_back} reasoning={teaching.teach_back_reasoning} onReveal={()=>count('transfer_revealed')}/></section>}
      <div className="ce-afterword"><div>
        <Evidence spec={spec} beat={beat}/>
        <details className="ce-evidence"><summary>Read this step without sound or motion</summary><p>{stage.narration}</p><dl><dt>Comes in</dt><dd>{stage.input_state}</dd><dt>Changes because</dt><dd>{stage.cause}</dd><dt>Leaves</dt><dd>{stage.output_state}</dd></dl></details>
        <details className="ce-evidence"><summary>Watch the complete narrated video</summary><video ref={video} controls playsInline preload="none" src={assets.videoUrl} onPlay={()=>player.pause()} onTimeUpdate={e=>{const time=playingMediaTime(e.currentTarget);if(time!==null){setScenario(undefined);player.time(time);}}} onError={()=>assets.setSaveError('The video could not load. You can still use the interactive explanation.')}><track kind="captions" src={assets.captionUrl} srcLang="en" label="English captions"/></video><p>Same lesson and causal states, with computer narration. Pause when a prediction appears.</p></details>
        <FeedbackPanel lesson={lesson} online={online} stage={beat.stage}/>
      </div><ChatPanel lesson={lesson} member={member} online={online} onShow={show}/></div>
    </>}
    <label className="ce-consent"><input type="checkbox" disabled={!online} checked={consent} onChange={e=>setConsent(e.target.checked)}/><span>Share usage counts with the owner, such as a skipped prediction or replay. Answers and written reasoning are excluded.</span></label>{countError&&<p className="ce-private-note" role="status">Usage counts could not be saved. Learning still works.</p>}
    <audio ref={audio} src={assets.videoUrl} preload="none" onLoadedMetadata={e=>{e.currentTarget.currentTime=player.initialTime();}} onTimeUpdate={e=>{const time=playingMediaTime(e.currentTarget);if(time!==null){setScenario(undefined);player.time(time);}}} onPause={()=>player.stopped()} onEnded={e=>{player.time(e.currentTarget.currentTime);player.stopped();}} onError={()=>assets.setSaveError('Narration could not load. The visual and text explanation still work.')}/>
  </article>;
}
