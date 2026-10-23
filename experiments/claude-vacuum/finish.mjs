// Explicit Codex integration repairs after the three Claude craft rounds.
// Preserve the API response; publish no production lesson or human quality verdict.
import {readFile, writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const dir = path.join(root, '.vercel/claude-vacuum/private');
const original = await readFile(path.join(dir, 'sonnet-final.txt'), 'utf8');
let html = original;
const changes = [];
function repair(reason, before, after) {
  if (html.split(before).length !== 2) throw new Error('Source changed; inspect repair: ' + reason);
  html = html.replace(before, after);
  changes.push(reason);
}
repair('Keep SVG and anchored HTML labels in the same aspect ratio on desktop',
  '.stage{position:relative;width:100%;aspect-ratio:720/650;max-height:80vh}',
  '.stage{position:relative;width:min(100%,calc(80vh * 720 / 650));aspect-ratio:720/650;margin-inline:auto}');
repair('Use the actual corrugation API; pitch is not the kit ring option',
  "rings:{pitch:pitch||5,tone:'lo'}", "rings:{step:pitch||5,width:.5}");
repair('Seat motor cradle at its lower tangent rather than below it',
  'h+=slab({x:MX0,y:-30,w:70,d:60,r:6},22,10,MAT.metal,4);',
  'h+=slab({x:MX0,y:-30,w:70,d:60,r:6},22,20,MAT.metal,4);');
repair('Label the shaft that the causal hint refers to',
  "['Motor',[MX0+36,0,ZA-10],[MX0+60,0,-10],'m'],",
  "['Shaft',[188,0,ZA],[175,118,16],'s'],\n ['Motor',[MX0+36,0,ZA-10],[MX0+60,0,-10],'m'],");
repair('Connect plenum markers to the exposed fan inlet face',
  '[FX-8,0,ZA]', '[FX-2,0,ZA]');
repair('Connect schematic flow through fan to the actual outlet duct',
  'const OUT=[[FX,0,ZA+22]', 'const ROTOR=[[FX-2,0,ZA],[FX,0,ZA+14],[FX,0,ZA+34]];\nconst OUT=[[FX,0,ZA+34]');
repair('Include the fan transformation in the shared flow route',
  'const AIR=[NOZ,HOSE,BAG1,WALL,PLEN,OUT];', 'const AIR=[NOZ,HOSE,BAG1,WALL,PLEN,ROTOR,OUT];');
repair('Show room air entering an actual open nozzle passage',
  'const NOZ=[[-170,18,14]', 'const NOZ=[[-222,18,14]');
repair('Open the nozzle cutaway instead of overlaying airflow on a solid slab',
  'h+=slab({x:-210,y:-52,w:92,d:100,r:14},3,20,MAT.teal,8,1);',
  `h+=slab({x:-210,y:-52,w:92,d:100,r:14},3,4,MAT.teal,8,1);
 h+=slab({x:-210,y:-52,w:92,d:8,r:3},7,16,MAT.teal,4,.6);
 h+=slab({x:-210,y:40,w:92,d:8,r:3},7,16,MAT.teal,4,.6);
 h+=slab({x:-142,y:-44,w:24,d:84,r:4},23,4,MAT.teal,4,.6);`);
repair('Derive Pause/Resume label from actual playback state',
  "$('bPause').hidden=!(playing||$('bPause').dataset.held==='1');return s}",
  "$('bPause').hidden=!(playing||$('bPause').dataset.held==='1');$('bPause').textContent=playing?'Pause':'Resume';return s}");
repair('Clear stale paused-control state when a new manual segment starts',
  'function manual(f,t0,t1){playing=false;cancelAnimationFrame(raf);focus=f;time=t0;run(t1)}',
  "function manual(f,t0,t1){playing=false;cancelAnimationFrame(raf);$('bPause').dataset.held='0';focus=f;time=t0;run(t1)}");
repair('A Turn on press immediately reaches the operating state',
  "else manual('all',2,9)", "else manual('all',3,9)");
repair('Tour always starts its full timeline, including while a manual segment runs',
  "$('bTour').onclick=()=>{blocked=false;focus=null;time=0;$('bUnblock').hidden=true;if(reduced||RENDER)draw();else api.play()};",
  "$('bTour').onclick=()=>{api.pause();$('bPause').dataset.held='0';blocked=false;focus=null;time=0;stopAt=TOUR;$('bUnblock').hidden=true;if(reduced){api.seek(40)}else if(RENDER){draw()}else api.play()};");
repair('Reduced-motion whole-system action has a useful still instead of doing nothing',
  'if(RENDER){const m=/[?&]t=([\\d.]+)/.exec(location.search);if(m)time=Math.min(TOUR,+m[1])}',
  "if(reduced)$('bTour').textContent='See the whole system';\nif(RENDER){const m=/[?&]t=([\\d.]+)/.exec(location.search);if(m)time=Math.min(TOUR,+m[1])}");
repair('Animate the blocked-condition fan briefly on deliberate reveal (still under reduced motion)',
  "$('show').onclick=()=>{ensureOn();api.setBlocked(true);",
  "$('show').onclick=()=>{ensureOn();api.setBlocked(true);run(Math.min(TOUR,time+2));");
repair('The experiment remains demonstrable after the tour reaches its endpoint',
  "const ensureOn=()=>{if(!cur().on){focus='all';time=8;stopAt=8}};",
  "const ensureOn=()=>{api.pause();focus='all';if(!cur().on||time>TOUR-2)time=8;stopAt=time};");
repair('Restoring the inlet also restores the explanation from authoritative state',
  "$('bUnblock').onclick=()=>api.setBlocked(false);",
  "$('bUnblock').onclick=()=>{api.setBlocked(false);$('answer').textContent=cur().desc};");
repair('Make source references directly inspectable',
  'https://www.dyson.com/vacuum-cleaners.asp; Dyson',
  '<a href="https://www.dyson.com/vacuum-cleaners.asp" target="_blank" rel="noreferrer">Dyson vacuum FAQ</a>; Dyson');
repair('Make the bag evidence directly inspectable',
  'https://www.dyson.com/discover/innovation/behind-the-invention/filtration-at-dyson. The blocked-inlet',
  '<a href="https://www.dyson.com/discover/innovation/behind-the-invention/filtration-at-dyson" target="_blank" rel="noreferrer">bag filtration</a>. The blocked-inlet');
repair('Use one short whole-system takeaway rather than repeating a paragraph',
  'Plain version: a motor spins a fan. The fan moves air; room air flows in to replace it and carries loose dirt. The bag keeps the dirt and lets the air through.',
  'Air carries dirt into the bag. Dirt stays; air passes through.');
repair('Explain marker meaning in plain language',
  'specks in the bag = a small sample, not an amount', 'specks show a small sample of dirt');
repair('Avoid assuming that every generic vacuum bag is cloth or retains every particle',
  'The bag wall stops the dirt; the air slips through the cloth.',
  'Air passes through gaps in the bag wall. Larger dirt gets caught.');
repair('Add a native accessible return control for the independently rendered bag window',
  "const gDyn=mk('g');const gLbl=mk('g');gLbl.innerHTML=labelSvg();",
  `const gDyn=mk('g');const gLbl=mk('g');gLbl.innerHTML=labelSvg();
 const returnWhole=document.createElement('button');returnWhole.id='bWhole';returnWhole.textContent='Back to the whole';
 returnWhole.setAttribute('aria-label','Return to whole machine');returnWhole.hidden=true;
 returnWhole.style.cssText='position:absolute;right:12px;bottom:12px;z-index:3';stage.appendChild(returnWhole);
 returnWhole.onclick=()=>{api.seek(40);document.getElementById('bBag').focus()};`);
repair('Implement the missing labeled bag-wall mechanism from the shared pose, with a whole-machine locator',
  'function draw(){const s=cur();gDyn.innerHTML=dyn(s);',
  `function draw(){const s=cur();const a=window.AnatomyTeaching.bagWindowAlpha(s);
 gDyn.innerHTML='<g opacity="'+(1-a)+'">'+dyn(s)+'</g>'+window.AnatomyTeaching.bagWindow(s,STATIC+fan(s));
 fig.firstElementChild.setAttribute('opacity',String(1-.94*a));gLbl.setAttribute('opacity',String(1-a));
 for(const tag of stage.querySelectorAll('.tag')){tag.style.opacity=String(1-a);tag.style.visibility=a>.99?'hidden':'visible'}
 returnWhole.hidden=a<.99;
 fig.setAttribute('aria-label',a>.5?'Enlarged collecting bag wall: larger loose dirt is retained while air passes through gaps toward the fan. Qualitative schematic.':'Cutaway canister vacuum showing the connected nozzle, hose, bag, fan, shaft, motor and outlet.');`);
const sha = value => createHash('sha256').update(value).digest('hex');
await writeFile(path.join(dir, 'sonnet-final-reviewed.html'), html);
await writeFile(path.join(dir, 'sonnet-final-repairs.json'), JSON.stringify({
  author: 'Codex', meaning: 'Integration/source inspection, not owner acceptance or technical certification',
  original_sha256: sha(original), reviewed_sha256: sha(html), changes,
}, null, 2));
