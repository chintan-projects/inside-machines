import {readFileSync,writeFileSync,mkdirSync,readdirSync,existsSync} from 'node:fs';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {panel,describe} from './lesson/panels.mjs';
import {loadNarration} from './lesson/load.mjs';
const root=dirname(fileURLToPath(import.meta.url)),at=(...x)=>join(root,...x);
const write=(path,body)=>{mkdirSync(dirname(path),{recursive:true});writeFileSync(path,body);};
const n=loadNarration(),panels={};let yaml='scenes:\n';
const ids=new Set();
for(const s of n.scenes){
 if(!/^[a-z][a-z_]*$/.test(s.id)||ids.has(s.id))throw new Error('Invalid or duplicate scene id.');ids.add(s.id);
 for(const b of s.beats){if(!/^[a-z][a-z_0-9]*$/.test(b.id)||ids.has(b.id))throw new Error('Invalid or duplicate beat id.');ids.add(b.id);if(typeof b.narration!=='string'||!b.narration.trim())throw new Error('A beat needs narration.');}
}
for(const scene of n.scenes){
 yaml+=`  - id: ${scene.id}\n    purpose: ${JSON.stringify(scene.title)}\n    beats:\n`;
 for(const b of scene.beats){
  const p=panel({...b,guide:b.guide??scene.guide??''});panels[b.id]=p;
  yaml+=`      - id: ${b.id}\n        narration_text: ${JSON.stringify(b.narration)}\n        visual: ${JSON.stringify(describe(p))}\n`;
  if(b.pause)yaml+=`        pause_duration_seconds: ${b.pause}\n`;
 }
 const cls='Scene'+scene.id.replace(/(^|_)([a-z])/g,(_,a,b)=>b.toUpperCase());
 write(at('video/production/episodes/ep01/scenes',scene.id+'.py'),`from shared.series import WorkedScene\n\n\nclass ${cls}(WorkedScene):\n    scene_id = '${scene.id}'\n`);
}
write(at('video/production/episodes/ep01/script.yaml'),yaml);
write(at('video/production/shared/narration.json'),JSON.stringify({...n,panels},null,2)+'\n');
const rounds=at('review/rounds');
if(existsSync(rounds))write(at('video/production/episodes/ep01/audience-reviews/script.yaml'),JSON.stringify({rounds:readdirSync(rounds).filter(x=>/^\d+\.json$/.test(x)).sort().map(x=>JSON.parse(readFileSync(join(rounds,x))))},null,2));
const mechanism=readFileSync(at('lesson/mechanism.mjs'),'utf8').replace(/^export (const|function)/gm,'$1');
const script=`(()=>{'use strict';\n${mechanism}\nconst NARRATION=${JSON.stringify(n)};\n${readFileSync(at('interactive/src/app.js'),'utf8')}\n})();`;
if(/<\/script/i.test(script))throw new Error('Unsafe inline script.');
const html=readFileSync(at('interactive/src/template.html'),'utf8').replace('{{STYLE}}',()=>readFileSync(at('interactive/src/styles.css'),'utf8')).replace('{{SCRIPT}}',()=>script);
write(at('interactive/index.html'),html);
console.log(`Built r6: ${n.scenes.flatMap(s=>s.beats).length} beats; ${n.scenes.flatMap(s=>s.beats).reduce((a,b)=>a+b.narration.split(/\s+/).length,0)} spoken words.`);
