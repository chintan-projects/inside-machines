import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {exportStates} from './lesson/states.js';
const root=dirname(fileURLToPath(import.meta.url));
const at=(...parts)=>join(root,...parts);
const write=(file,body)=>{mkdirSync(dirname(file),{recursive:true});writeFileSync(file,body);};
const teaching=JSON.parse(readFileSync(at('lesson/teaching.json'),'utf8'));
const words=teaching.core.flatMap(frame=>frame.beats).reduce((total,beat)=>total+beat.narration.split(/\s+/).length,0);
if(words>600)throw new Error(`Core exceeds 600 words: ${words}`);
let yaml='# Generated from lesson/teaching.json.\nscenes:\n';
for(const frame of teaching.core){
  yaml+=`  - id: ${frame.id}\n    purpose: ${JSON.stringify(frame.title)}\n    beats:\n`;
  for(const beat of frame.beats){yaml+=`      - id: ${beat.id}\n        narration_text: ${JSON.stringify(beat.narration)}\n        visual: ${JSON.stringify(beat.visual)}\n`;if(beat.pause)yaml+=`        pause_duration_seconds: ${beat.pause}\n`;}
}
write(at('video/production/episodes/ep01/script.yaml'),yaml);
write(at('video/production/shared/lesson_states.json'),JSON.stringify(exportStates(),null,2)+'\n');
write(at('video/production/shared/teaching.json'),JSON.stringify(teaching,null,2)+'\n');
const strip=source=>source.replace(/^import .*$/gm,'').replace(/^export (const|function|let)/gm,'$1');
const modules=['lesson/mechanism.js','lesson/states.js','lesson/recovery.js'].map(file=>strip(readFileSync(at(file),'utf8'))).join('\n');
const script=`(()=>{\n'use strict';\n${modules}\nconst TEACHING=${JSON.stringify(teaching)};\n${readFileSync(at('interactive/src/views.js'),'utf8')}\n${readFileSync(at('interactive/src/app.js'),'utf8')}\n})();`;
if(/<\/script/i.test(script))throw new Error('Unsafe inline script delimiter.');
const html=readFileSync(at('interactive/src/template.html'),'utf8').replace('{{STYLE}}',()=>readFileSync(at('interactive/src/styles.css'),'utf8')).replace('{{SCRIPT}}',()=>script);
write(at('interactive/index.html'),html);
process.stdout.write(`Built r3: ${words} words, ${teaching.core.length} chapters, shared checkpoints and local HTML.\n`);
