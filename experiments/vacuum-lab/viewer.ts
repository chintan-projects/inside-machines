import {duration, story} from './model';

interface Candidate {
  readonly name:string; readonly videos:Readonly<Record<'core'|'blocked',string>>;
  readonly stills:Readonly<Record<string,string>>; readonly provenance:object;
}
interface Experiment {readonly candidates:Readonly<Record<string,Candidate>>;readonly prompts:Readonly<Record<string,string>>;readonly version:string;}
function element<T extends HTMLElement>(id:string):T {
  const result=document.getElementById(id);if(!result)throw new Error(`Missing ${id}`);return result as T;
}
const data:Experiment=JSON.parse(element('experiment-data').textContent??'{}');
const film=element<HTMLVideoElement>('film'),still=element<HTMLImageElement>('still');
const seek=element<HTMLInputElement>('seek'), play=element<HTMLButtonElement>('play');
const name=element('engine-name'), caption=element('caption'), title=element('beat-title'),copy=element('beat-copy');
const tabs=[...document.querySelectorAll<HTMLButtonElement>('[data-engine]')];
const chapters=[...document.querySelectorAll<HTMLButtonElement>('[data-beat]')];
const calm=matchMedia('(prefers-reduced-motion: reduce)').matches;
let engine='anatomy', blocked=false, staticMode=calm, selectedBeat=0, chosen='', loadId=0;
let savedCoreTime=0, mediaUrl='', hasMedia=false, requestedTime=0;
let votedPrediction:string|null=null;
film.muted=true;

function timestamp(seconds:number):string {return `${Math.floor(seconds/60)}:${String(Math.floor(seconds%60)).padStart(2,'0')}`;}
function asset(kind:'core'|'blocked',beat=selectedBeat):string {
  const key=kind==='blocked'?'blocked':String(beat);
  return `data:image/png;base64,${data.candidates[engine].stills[key]}`;
}
function update(time:number):void {
  if(!Number.isFinite(time))return;
  selectedBeat=blocked?3:Math.max(0,story.beats.findLastIndex(beat=>time>=beat.start));
  const beat=story.beats[selectedBeat];
  title.textContent=blocked?story.experiment.title:beat.title;
  copy.textContent=blocked?story.experiment.explanation:beat.explanation;
  caption.textContent=blocked?story.experiment.narration:beat.narration;
  seek.value=String(time);seek.max=String(blocked?story.experiment.duration:duration);
  element('time').textContent=`${timestamp(time)} / ${timestamp(Number(seek.max))}`;
  for(const button of chapters)button.setAttribute('aria-pressed',String(!blocked&&Number(button.dataset.beat)===selectedBeat));
  still.src=asset(blocked?'blocked':'core');still.alt=`${data.candidates[engine].name}: ${title.textContent} ${copy.textContent}`;
  const showingStill=staticMode||film.seeking;
  still.hidden=!showingStill;film.hidden=showingStill;
  element('static-mode').setAttribute('aria-pressed',String(staticMode));
  element('static-mode').textContent=staticMode?'Return to video':'Use still diagrams';
  play.innerHTML=film.paused?'▶ <span>Play</span>':'Ⅱ <span>Pause</span>';
  play.setAttribute('aria-label',film.paused?'Play explanation':'Pause explanation');
}
function decodeVideo(base64:string):Blob {
  const binary=atob(base64),bytes=new Uint8Array(binary.length);
  for(let i=0;i<binary.length;i++)bytes[i]=binary.charCodeAt(i);
  return new Blob([bytes],{type:'video/mp4'});
}
function showFailure():void {
  hasMedia=false;staticMode=true;film.pause();
  element('media-error').hidden=false;
  update(requestedTime);
}
async function resume():Promise<void> {
  if(!hasMedia)return;
  staticMode=false;update(film.currentTime);
  try{await film.play();}catch{element('media-error').textContent='Playback could not start. Tap Play again, or use the static steps.';element('media-error').hidden=false;}
}
function load(time:number,continuePlaying=false):void {
  const current=++loadId;hasMedia=false;film.pause();requestedTime=time;
  if(mediaUrl)URL.revokeObjectURL(mediaUrl);
  mediaUrl=URL.createObjectURL(decodeVideo(data.candidates[engine].videos[blocked?'blocked':'core']));
  film.poster=asset(blocked?'blocked':'core');
  film.onloadedmetadata=()=>{
    if(current!==loadId)return;
    hasMedia=true;film.currentTime=Math.max(0,Math.min(time,film.duration-.05));
    update(film.currentTime);if(continuePlaying&&!staticMode)void resume();
  };
  film.onerror=()=>{if(current===loadId)showFailure();};
  element('media-error').hidden=true;film.src=mediaUrl;film.load();update(time);
}
function select(candidate:string):void {
  if(!(candidate in data.candidates))return;
  const playing=!film.paused,time=hasMedia?film.currentTime:requestedTime;
  engine=candidate;name.textContent=data.candidates[engine].name;
  for(const button of tabs){const active=button.dataset.engine===engine;button.setAttribute('aria-selected',String(active));button.tabIndex=active?0:-1;}
  element('explanation').setAttribute('aria-labelledby',`tab-${engine}`);
  element('choose').textContent=`Keep ${data.candidates[engine].name}`;
  element('provenance').textContent=JSON.stringify(data.candidates[engine].provenance,null,2);
  history.replaceState(null,'',`#${engine}`);load(time,playing);
}
for(const button of tabs){
  button.addEventListener('click',()=>select(button.dataset.engine??''));
  button.addEventListener('keydown',event=>{
    if(!['ArrowRight','ArrowLeft','Home','End'].includes(event.key))return;
    event.preventDefault();let index=tabs.indexOf(button);
    index=event.key==='Home'?0:event.key==='End'?tabs.length-1:(index+(event.key==='ArrowRight'?1:-1)+tabs.length)%tabs.length;
    tabs[index].focus();select(tabs[index].dataset.engine??'');
  });
}
film.addEventListener('timeupdate',()=>update(film.currentTime));
film.addEventListener('play',()=>update(film.currentTime));
film.addEventListener('pause',()=>update(film.currentTime));
film.addEventListener('ended',()=>update(film.currentTime));
film.addEventListener('seeking',()=>update(film.currentTime));
film.addEventListener('seeked',()=>update(film.currentTime));
play.addEventListener('click',()=>{if(film.paused)void resume();else film.pause();});
seek.addEventListener('input',()=>{requestedTime=Number(seek.value);if(hasMedia)film.currentTime=requestedTime;update(requestedTime);});
element('replay').addEventListener('click',()=>{if(hasMedia)film.currentTime=0;requestedTime=0;update(0);});
element('static-mode').addEventListener('click',()=>{film.pause();staticMode=!staticMode;update(hasMedia?film.currentTime:requestedTime);});
element('sound').addEventListener('click',()=>{
  film.muted=!film.muted;
  element('sound').textContent=film.muted?'Sound off':'Sound on';
  element('sound').setAttribute('aria-pressed',String(!film.muted));
  element('sound').setAttribute('aria-label',film.muted?'Turn narration on':'Turn narration off');
});
function openInlet():void {
  blocked=false;element('result').hidden=true;element('prediction').hidden=true;
  element('try').textContent='Make a prediction';element('try').hidden=false;
  load(savedCoreTime);update(savedCoreTime);
}
element('try').addEventListener('click',()=>{
  if(blocked){openInlet();return;}
  film.pause();element('prediction').hidden=false;element('try').hidden=true;
});
for(const button of document.querySelectorAll<HTMLButtonElement>('[data-prediction]'))button.addEventListener('click',()=>{
  votedPrediction=button.dataset.prediction??'skip';savedCoreTime=hasMedia?film.currentTime:requestedTime;blocked=true;
  element('prediction').hidden=true;element('try').hidden=false;element('try').textContent='Open the inlet again';
  element('result').hidden=false;load(0,!calm);
});
for(const button of chapters)button.addEventListener('click',()=>{
  if(blocked){blocked=false;element('result').hidden=true;element('try').textContent='Make a prediction';element('prediction').hidden=true;}
  const beat=Number(button.dataset.beat);requestedTime=story.beats[beat].start;
  if(!hasMedia||film.src!==mediaUrl){load(requestedTime);return;}
  // Core media must be restored when a chapter exits the blocked experiment.
  if(seek.max!==String(duration)){load(requestedTime);return;}
  film.pause();film.currentTime=requestedTime;update(requestedTime);
});
element('choose').addEventListener('click',()=>{
  chosen=engine;element('choice').textContent=`Your pick: ${data.candidates[chosen].name}. You can change it after comparing.`;
});
element('download').addEventListener('click',()=>{
  const review={version:data.version,preferred:chosen||null,prediction:votedPrediction,
    note:'Personal preference only; no independent factual or beginner learning acceptance.',
    authoring:'Same OpenAI Codex interactive coding session; not an API-model comparison.'};
  const url=URL.createObjectURL(new Blob([JSON.stringify(review,null,2)],{type:'application/json'}));
  const a=document.createElement('a');a.href=url;a.download='vacuum-comparison.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),5000);
});
const dialog=element<HTMLDialogElement>('full-view');
element('expand').addEventListener('click',()=>{
  film.pause();let src=still.src;
  if(!staticMode&&hasMedia){const canvas=document.createElement('canvas');canvas.width=story.width;canvas.height=story.height;
    const context=canvas.getContext('2d');if(context){context.drawImage(film,0,0);src=canvas.toDataURL('image/png');}}
  element<HTMLImageElement>('full-image').src=src;dialog.showModal();
});
element('close-view').addEventListener('click',()=>dialog.close());
for(const [label,prompt]of Object.entries(data.prompts)){
  const details=document.createElement('details'),summary=document.createElement('summary'),pre=document.createElement('pre');
  summary.textContent=label;pre.textContent=prompt;details.append(summary,pre);element('prompts').append(details);
}
window.addEventListener('pagehide',()=>{film.pause();if(mediaUrl)URL.revokeObjectURL(mediaUrl);});
window.addEventListener('pageshow',event=>{if(event.persisted)load(requestedTime);});
select(location.hash.slice(1)||'anatomy');
