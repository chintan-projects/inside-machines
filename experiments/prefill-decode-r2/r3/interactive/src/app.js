const $ = selector => document.querySelector(selector);
const journey=createJourney(FRAME_IDS);
let helpStep=0,helpLayer=0,helpChoice=null,helpFeedback=null,rebuilding=false;
const ACTUAL_CHAPTERS=/* ACTUAL_TIMELINE_CHAPTERS */ [];
const MEDIA_READY=/* ACTUAL_MEDIA_READY */ false;
$('#film-mode').hidden=!MEDIA_READY;
if(MEDIA_READY){
  $('#film').setAttribute('poster','poster.png');
  for(const asset of document.querySelectorAll('#film [data-src]'))asset.setAttribute('src',asset.dataset.src);
  $('#film').load();
}
const frameTitle=['Next-slot tasks','The first choice','Back in as input','The next choice','What caching saves'];
function currentFrame(){return TEACHING.core.find(item=>item.id===journey.state().frame);}
function drawCore(){
  const state=journey.state(),frame=currentFrame(),index=FRAME_IDS.indexOf(frame.id),beat=frame.beats[state.beat];
  $('#chapters').innerHTML=TEACHING.core.map((item,i)=>`<button data-frame="${item.id}" ${item.id===frame.id?'aria-current="step"':''}>${i+1}. ${frameTitle[i]}</button>`).join('');
  $('#stage').innerHTML=coreView(frame.id,state.beat,state.cache,rebuilding);
  $('#story').innerHTML=`<p class="eyebrow">${index+1} / 5 · ${frameTitle[index]}</p><h2>${frame.title}</h2><p class="step-copy">${escapeText(beat.narration)}</p><p class="note">${frame.id==='tasks'?'The prompt is supplied text. One position’s result targets one next slot.':frame.id==='first_choice'?'Matching lists set the shares. Reading lists supply what gets combined. Word choice comes afterward.':frame.id==='feed_back'?'Text visible on the page and preparation inside the model are different states.':frame.id==='second_choice'?'Saved preparation still gets read at every layer.':'Same fixed toy, same text, same choices. We count positions, not seconds.'}</p>`;
  $('#previous').disabled=index===0&&state.beat===0;
  $('#position').textContent=`Chapter ${index+1} of 5 · step ${state.beat+1} of ${frame.beats.length}`;
  $('#next').textContent=state.beat<frame.beats.length-1?'Show the next step →':index<4?frame.nextLabel+' →':'Try a new case →';
}
function move(direction){
  const state=journey.state(),frame=currentFrame(),index=FRAME_IDS.indexOf(frame.id);
  if(direction>0&&state.beat===frame.beats.length-1){if(index===4){$('#transfer').scrollIntoView({behavior:'auto'});return;}journey.move(FRAME_IDS[index+1]);}
  else if(direction<0&&state.beat===0){if(index===0)return;journey.move(FRAME_IDS[index-1],TEACHING.core[index-1].beats.length-1);}
  else journey.move(frame.id,state.beat+direction);
  rebuilding=false;closeHelp();drawCore();
}
function closeHelp(){journey.back();$('#help-panel').hidden=true;helpStep=0;helpLayer=0;helpChoice=null;helpFeedback=null;}
function showRepair(id){
  journey.help(id);helpStep=0;helpLayer=0;helpChoice=null;helpFeedback=null;drawHelp();
  $('#help-panel').scrollIntoView({behavior:'auto',block:'nearest'});$('#help-panel').focus({preventScroll:true});
}
function drawHelp(){
  const state=journey.state(),id=state.repair,panel=$('#help-panel');
  if(!id){panel.hidden=true;return;}
  panel.hidden=false;
  const top=`<button data-close-help>← Return to chapter ${FRAME_IDS.indexOf(state.frame)+1}, step ${state.beat+1}</button>`;
  if(id==='clarify') {
    panel.innerHTML=top+'<h2>Which part should we unpack?</h2><p>Keep your place. Pick the relationship you want to see.</p><div class="choices">'+[...new Set([DEFAULT_REPAIR[currentFrame().beats[state.beat].concept??currentFrame().concept],'layers','saved_work','scoring'])].filter(Boolean).slice(0,3).map(key=>TEACHING.repairs.find(item=>item.id===key)).map(item=>`<button data-repair="${item.id}">${escapeText(item.title)}</button>`).join('')+'</div>';
    return;
  }
  if(id==='scoring'){
    panel.innerHTML=top+`<h2>How word scoring works</h2><div class="help-visual">${scoringView(helpStep,['tasks','first_choice'].includes(state.frame)?0:1)}</div><div class="actions"><button data-help-prev ${helpStep===0?'disabled':''}>← Previous detail</button><button data-help-next>${helpStep<3?'Show the next operation →':'Return to the explanation →'}</button></div>`;
    return;
  }
  const repair=TEACHING.repairs.find(item=>item.id===id);
  if(!repair)throw new Error('Unknown help route.');
  const depth=id==='layers'||id==='cache_walk';
  const actualCacheWalk=id==='saved_work'&&helpStep>0;
  if(depth||actualCacheWalk){
    const cache=id!=='layers';
    panel.innerHTML=top+`<h2>${cache?'How the saved lists are used':'What changes inside one layer'}</h2><div class="help-visual">${cache?cacheView(Math.max(0,helpStep-1)):layerView(helpLayer,helpStep,['tasks','first_choice'].includes(state.frame)?0:1)}</div><div class="actions"><button data-help-prev ${helpStep===0?'disabled':''}>← Previous detail</button><button data-help-next>${(cache?helpStep<6:helpStep<5)?'Show the next operation →':!cache&&helpLayer===0?'Follow into layer 2 →':'Return to the explanation →'}</button></div>`;
    return;
  }
  const visual=id==='next_slot'?tasksView(true,3):id==='feed_input'?`${tokenRow([...PROMPT,'blue'],['?'])}<div class="branch">is processed → choose blue outside → blue becomes input → process blue → choose the following piece.</div>`:id==='saved_work'?`<div class="branch">Input to a layer → prepare two lists → save for later.<br>One list helps set how much to read. The other supplies what gets read.<br>The finished layer output goes onward on a separate path.</div>${trayView(3)}`:`<div class="comparison"><article><h3>Kept</h3><div class="big-number">1</div><p>New position through both layers; read the saved past.</p></article><article><h3>Cleared</h3><div class="big-number">4</div><p>Rebuild the earlier positions, and process blue too.</p></article></div>`;
  panel.innerHTML=top+`<h2>${escapeText(repair.title)}</h2><p class="explanation">${escapeText(repair.explanation)}</p><div class="help-visual">${visual}</div><h3>${escapeText(repair.question)}</h3><div class="choices">${repair.choices.map(choice=>`<button data-answer="${choice.id}" aria-pressed="${helpChoice===choice.id}">${escapeText(choice.label)}</button>`).join('')}</div>${helpChoice?`<p class="feedback" role="status">${escapeText(repair.choices.find(choice=>choice.id===helpChoice).feedback)}</p>`:''}<div class="actions">${id==='saved_work'?'<button data-walk-cache>Show me how the two lists are used →</button>':''}<button data-helpful="yes">This helped</button><button data-helpful="no">Try another view</button></div>${helpFeedback?`<p class="small" role="status">${helpFeedback==='yes'?'Good. Your place is saved; return whenever you’re ready.':'Choose a concrete route below. Your place is saved.'}</p>`:''}`;
}
function ask(text){
  const frame=currentFrame(),beat=frame.beats[journey.state().beat];
  const focus=beat.concept??frame.concept;
  const contextualId=DEFAULT_REPAIR[focus];
  const concept=TEACHING.repairs.find(item=>item.id===contextualId)?.concept??focus;
  const route=resolveHelp({text,concept,repairs:TEACHING.repairs,aliases:HELP_ALIASES});
  showRepair(route.kind==='repair'?route.id:'clarify');
}
$('#chapters').addEventListener('click',event=>{const button=event.target.closest('[data-frame]');if(button){journey.move(button.dataset.frame);rebuilding=false;closeHelp();drawCore();}});
$('#next').addEventListener('click',()=>move(1));$('#previous').addEventListener('click',()=>move(-1));
$('#stage').addEventListener('click',event=>{
  const compare=event.target.closest('[data-compare]');
  if(compare){journey.compare(compare.dataset.compare==='keep');rebuilding=compare.dataset.compare==='clear';drawCore();}
  if(event.target.closest('[data-rebuild]')){rebuilding=false;drawCore();}
});
$('#help-form').addEventListener('submit',event=>{event.preventDefault();ask($('#help-query').value);});
$('#lost').addEventListener('click',()=>ask('I am lost'));$('#deeper').addEventListener('click',()=>ask('Dive deeper'));
$('#scoring-help').addEventListener('click',()=>showRepair('scoring'));
$('#layer-help').addEventListener('click',()=>showRepair('layers'));$('#cache-help').addEventListener('click',()=>{showRepair('saved_work');helpStep=1;drawHelp();});
$('#help-panel').addEventListener('click',event=>{
  const button=event.target.closest('button');if(!button)return;
  if(button.hasAttribute('data-close-help')){closeHelp();$('#next').focus();return;}
  if(button.dataset.repair){showRepair(button.dataset.repair);return;}
  if(button.dataset.answer){helpChoice=button.dataset.answer;drawHelp();return;}
  if(button.hasAttribute('data-walk-cache')){helpStep=1;drawHelp();return;}
  if(button.hasAttribute('data-help-next')){
    if(journey.state().repair==='scoring'&&helpStep===3){closeHelp();return;}
    if(journey.state().repair==='layers'&&helpStep===5){if(helpLayer===0){helpLayer=1;helpStep=0;}else{closeHelp();return;}}
    else if(journey.state().repair==='saved_work'&&helpStep===6){closeHelp();return;}else helpStep+=1;
    drawHelp();return;
  }
  if(button.hasAttribute('data-help-prev')){helpStep=Math.max(0,helpStep-1);drawHelp();return;}
  if(button.dataset.helpful){helpFeedback=button.dataset.helpful;if(helpFeedback==='no'){showRepair('clarify');}else drawHelp();}
});
$('#reveal').addEventListener('click',()=>{
  $('#transfer-answer').hidden=false;$('#transfer-answer').innerHTML='<h3>Kept: 1. Cleared: 7.</h3><p>The new piece needs its own result before another can be chosen. With preparation kept, only that new position goes through the whole model. With it cleared, all six old positions must be reprocessed as well.</p><p>The new position reads the past in both cases. Earlier positions cannot read later ones, so appending a piece cannot change their preparation. Rebuilding it from the same text gives the same lists and the same choice in this toy.</p>';$('#reveal').hidden=true;
});
function setMode(film){$('#film-panel').hidden=!film;$('#lesson').hidden=film;$('#film-mode').setAttribute('aria-pressed',String(film));$('#core-mode').setAttribute('aria-pressed',String(!film));if(!film)$('#film').pause();}
$('#core-mode').addEventListener('click',()=>setMode(false));$('#film-mode').addEventListener('click',()=>setMode(true));
$('#sound').addEventListener('click',async()=>{const film=$('#film');film.muted=false;film.volume=1;try{await film.play();$('#media-status').textContent='Playing with sound. Use the player’s CC control for captions.';}catch{$('#media-status').textContent='Video is not available in this preview. Interactive mode and the transcript still work.';}});
$('#film').addEventListener('error',()=>{$('#media-status').textContent='This preview has no rendered film yet. Read the transcript or explore the steps.';});
$('#film-chapters').innerHTML=ACTUAL_CHAPTERS.map((chapter,index)=>`<button data-film-chapter="${index}">${index+1}. ${escapeText(chapter.title)}</button>`).join('');
$('#film-chapters').addEventListener('click',event=>{const button=event.target.closest('[data-film-chapter]');if(button){$('#film').currentTime=ACTUAL_CHAPTERS[Number(button.dataset.filmChapter)].seconds;}});
$('#transcript').innerHTML=TEACHING.core.map(frame=>`<h3>${escapeText(frame.title)}</h3>${frame.beats.map(beat=>`<p>${escapeText(beat.narration)}</p>`).join('')}`).join('');
$('#reset').addEventListener('click',()=>{journey.reset();rebuilding=false;closeHelp();$('#attempt').value='';$('#help-query').value='';$('#transfer-answer').hidden=true;$('#transfer-answer').textContent='';$('#reveal').hidden=false;$('#film').pause();if($('#film').readyState)$('#film').currentTime=0;drawCore();});
document.addEventListener('keydown',event=>{if(event.target.closest('input,textarea,button,summary,video')||!$('#film-panel').hidden||!$('#help-panel').hidden)return;if(event.key==='ArrowRight'){event.preventDefault();move(1);}if(event.key==='ArrowLeft'){event.preventDefault();move(-1);}});
drawCore();
