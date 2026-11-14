const $=selector=>document.querySelector(selector);
const CHAPTERS=/* ACTUAL_TIMELINE_CHAPTERS */ [];
const DURATION=/* ACTUAL_MEDIA_DURATION */ null;
const MEDIA_READY=/* ACTUAL_MEDIA_READY */ false;
const escape=value=>String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const number=(label,value,output=false)=>`<div class="number ${output?'output':''}"><small>${escape(label)}</small><strong>${escape(value)}</strong></div>`;
function draw(){
 const cache=$('#cache').value==='keep',pass=Number($('#pass').value),layer=Number($('#layer').value),word=$('#word').value;
 const result=run({cache,tokens:['The',word,'is']}),p=result.passes[pass],t=p.traces.find(x=>x.position===p.text.length-1).layers[layer];
 $('#diagram').innerHTML=`<article class="panel"><p class="tag">${pass?'NEW CHOSEN INPUT':'SUPPLIED TEXT'} · LAYER ${layer+1}</p><h2>${escape(t.word)} reads, then reworks its number.</h2><p>Text input: <strong>${p.text.map(escape).join(' / ')}</strong></p><div class="operation">${number('Input to this layer',format(t.input))}<span class="arrow" aria-hidden="true">→</span>${number('Combined reading',format(t.blend))}<span class="arrow" aria-hidden="true">→</span>${number('Finished layer result',format(t.output),true)}</div><p>Read ${format(t.blend)} from allowed values, add it to ${format(t.input)} to get ${format(t.mixed)}, then add the local adjustment ${format(t.adjustment)}.</p><div class="reading"><table><caption>Query ${format(t.query)} reads keys and values at this layer</caption><thead><tr><th>Source</th><th>Key</th><th>Value</th><th>Share</th><th>Contribution</th></tr></thead><tbody>${t.sources.map((s,i)=>`<tr><th>${escape(s.word)}${s.position===t.position?' · self':''}</th><td>${format(s.key)}</td><td>${format(s.value)}</td><td>${(100*t.shares[i]).toFixed(1)}%</td><td>${format(t.contributions[i])}</td></tr>`).join('')}</tbody></table></div></article><div class="two"><article class="panel"><p class="tag">PREPARATION IN THIS PASS</p><p class="metric">${p.preparedPerLayer[layer]} ${p.preparedPerLayer[layer]===1?'entry':'entries'}</p><p>One entry is one key and one value, prepared from one position’s input to this layer. This counts preparations, not time.</p></article><article class="panel"><p class="tag">AFTER BOTH LAYERS</p><p class="metric">${escape(p.selection.word)} chosen</p><p>The finished number ${format(p.result)} scores blue at ${format(p.selection.candidates[0].score)} and and at ${format(p.selection.candidates[1].score)}. The higher score wins. The selected piece still needs processing before another choice.</p></article></div>`;
 $('#scenario-note').textContent=word==='sky'?'The movie and experiment use the same fixed example. Keeping versus clearing preparation changes the work, while the computed choices stay equal.':'This edited experiment recomputes the prompt before continuing. The movie keeps its original The / sky / is example.';
}
for(const id of ['pass','layer','cache','word'])$('#'+id).addEventListener('change',draw);
$('#film-mode').hidden=!MEDIA_READY;
$('#film-mode').textContent='Watch with narration'+(DURATION?' · '+Math.ceil(DURATION/60)+' min':'');
let pendingSeek=null;
if(MEDIA_READY){$('#film').poster='poster.png';for(const asset of document.querySelectorAll('#film [data-src]'))asset.src=asset.dataset.src;$('#film').load();}
function mode(film){$('#film-panel').hidden=!film;$('#lesson').hidden=film;$('#film-mode').setAttribute('aria-pressed',String(film));$('#core-mode').setAttribute('aria-pressed',String(!film));history.replaceState(null,'',film?'#film':'#core');if(!film)$('#film').pause();}
$('#core-mode').addEventListener('click',()=>mode(false));$('#film-mode').addEventListener('click',()=>mode(true));
$('.brand').addEventListener('click',event=>{event.preventDefault();mode(false);});
function mediaStatus(){const v=$('#film');$('#media-status').textContent=v.error?'The local movie could not load. Read the explanation below or explore the numbers.':v.ended?'Finished. Choose a chapter to revisit or explore the numbers.':v.paused?'Paused. Choose a chapter or press play to continue.':v.seeking||v.readyState<3?'Loading the selected moment…':v.muted||v.volume===0?'Playing silently. Turn sound on or read the captions.':'Playing with sound. Captions are available in the player’s CC control.';}
for(const event of ['playing','pause','ended','volumechange','seeking','seeked','waiting'])$('#film').addEventListener(event,mediaStatus);
$('#sound').addEventListener('click',async()=>{const v=$('#film');v.muted=false;v.volume=1;try{await v.play();mediaStatus();}catch{$('#media-status').textContent='Could not start the local film. The read-along explanation and experiment still work.';}});
$('#film').addEventListener('loadedmetadata',()=>{if(pendingSeek!==null){$('#film').currentTime=pendingSeek;pendingSeek=null;}});
$('#film').addEventListener('error',()=>{$('#media-status').textContent='The local movie could not load. Read the explanation below or explore the numbers.';});
$('#film-chapters').innerHTML=CHAPTERS.map((c,i)=>`<button data-chapter="${i}">${i+1}. ${escape(c.title)}</button>`).join('');
$('#film-chapters').addEventListener('click',event=>{const b=event.target.closest('[data-chapter]');if(b){const seconds=CHAPTERS[Number(b.dataset.chapter)].seconds;if($('#film').readyState)$('#film').currentTime=seconds;else pendingSeek=seconds;}});
$('#transcript').innerHTML=NARRATION.scenes.map(s=>`<h3>${escape(s.title)}</h3>${s.beats.map(b=>`<p>${escape(b.narration)}</p>`).join('')}`).join('');
$('#reset').addEventListener('click',()=>{$('#pass').value='1';$('#layer').value='0';$('#cache').value='keep';$('#word').value='sky';$('#film').pause();pendingSeek=null;if($('#film').readyState)$('#film').currentTime=0;draw();});
draw();if(MEDIA_READY&&location.hash==='#film')mode(true);
