/** Reversible local review build. Never writes the frozen R1 output or calls a provider. */
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {build} from 'esbuild';
import {refrigeratorNarrations} from '../narration.ts';
const root=fileURLToPath(new URL('../../../',import.meta.url));
const out=path.join(root,'.vercel/refrigerator-r2/public');
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const frozen=path.join(root,'.vercel/visual-studio/public/refrigerator/index.html');
const frozenBefore=hash(await readFile(frozen));
const narration={};
if(process.argv.includes('--reuse-audio')) {
  for(const plan of refrigeratorNarrations) {
    const audioDir=path.join(root,'.vercel/claude-vacuum/private/refrigerator-r1-audio',plan.id);
    const mp3=await readFile(path.join(audioDir,'narration.mp3'));
    const manifest=JSON.parse(await readFile(path.join(audioDir,'manifest.json'),'utf8'));
    if(manifest.plan_sha256!==hash(JSON.stringify(plan))||manifest.mp3_sha256!==hash(mp3)||
      manifest.story_seconds!==plan.duration||Math.abs(manifest.encoded_seconds-plan.duration)>.15)throw new Error('Narration provenance mismatch');
    narration[plan.id]={...plan,src:'data:audio/mpeg;base64,'+mp3.toString('base64')};
  }
}
const [bundle,css,license]=await Promise.all([
  build({entryPoints:[path.join(root,'experiments/refrigerator-study/r2/entry.ts')],bundle:true,write:false,format:'iife',platform:'browser',minify:true}),
  readFile(path.join(root,'web/studio/theme.css'),'utf8'),readFile(path.join(root,'vendor/anatomy/LICENSE'),'utf8'),
]);
const script=code=>'<script>'+code.replaceAll('</script','<\\/script')+'</script>';
const html='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'+
  '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; script-src \'unsafe-inline\'; style-src \'unsafe-inline\'; media-src data:; img-src data:; base-uri \'none\'; form-action \'none\'">'+
  '<title>Refrigerator · R2 local craft review</title><style>'+css+'</style></head><body><div id="app"></div>'+
  '<footer class="provenance"><p>R2 local craft candidate. Trusted Anatomy geometry; source-led R1 causal model and unchanged cue plans. '+
  (Object.keys(narration).length?'Reused matching R1 local computer-speech assets.':'No audio is attached to this build.')+
  ' No model call occurs when viewing. Technical, actual-device and beginner acceptance remain pending.</p></footer>'+
  script('/* Anatomy MIT license\n'+license+'*/\nwindow.refrigeratorR2Narrations='+JSON.stringify(narration)+';')+
  script(bundle.outputFiles[0].text)+'</body></html>';
await mkdir(out,{recursive:true});await writeFile(path.join(out,'index.html'),html);
if(hash(await readFile(frozen))!==frozenBefore)throw new Error('Frozen R1 artifact changed');
console.log(JSON.stringify({output:path.join(out,'index.html'),sha256:hash(html),frozen_r1_sha256:frozenBefore,reused_audio:Object.keys(narration).length},null,2));
