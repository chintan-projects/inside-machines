/** Package actual rendered outputs into one self-contained offline review page. */
import {readFile,writeFile,access} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
const HERE=dirname(fileURLToPath(import.meta.url)),ROOT=resolve(HERE,'../..'),OUT=join(ROOT,'.vercel/vacuum-lab');
const runtime=process.env.VACUUM_LAB_RUNTIME??join(OUT,'runtime');
const require=createRequire(join(runtime,'package.json'));
const {build}=require('esbuild');
const story=JSON.parse(await readFile(join(HERE,'story.json'),'utf8'));
/** @param {Buffer|string} bytes @returns {string} */
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
const names={anatomy:'Anatomy',manim:'Manim','motion-canvas':'Motion Canvas',remotion:'Remotion'};
const candidates={};
for(const [engine,name]of Object.entries(names)){
  const running=await access(join(OUT,`.render-${engine==='motion-canvas'?'motion':engine}.lock`)).then(()=>true,()=>false);
  if(running)throw new Error(`Wait for ${name} rendering to finish`);
  const receipt=JSON.parse(await readFile(join(OUT,`${engine==='motion-canvas'?'motion':engine}-receipt.json`),'utf8'));
  if(receipt.storySha256!==sha(await readFile(join(HERE,'story.json'))))throw new Error(`Stale ${name} story`);
  const source={anatomy:'anatomy.mjs',manim:'manim_scene.py','motion-canvas':'motion-canvas.ts',remotion:'remotion.tsx'}[engine];
  if(receipt.sourceSha256!==sha(await readFile(join(HERE,source))))throw new Error(`Stale ${name} adapter`);
  const videos={},hashes={};
  for(const mode of ['core','blocked']){
    const path=join(OUT,'rendered',`${engine}-${mode}.mp4`),bytes=await readFile(path);
    const p=spawnSync('ffprobe',['-v','error','-show_entries','stream=codec_type,width,height','-show_entries','format=duration','-of','json',path],{encoding:'utf8'});
    if(p.status!==0)throw new Error(`Invalid ${name} media`);
    const probe=JSON.parse(p.stdout),video=probe.streams.find(s=>s.codec_type==='video');
    if(!video||video.width!==story.width||video.height!==story.height||!probe.streams.some(s=>s.codec_type==='audio'))throw new Error(`Incomplete ${name} media`);
    const expected=mode==='core'?44:story.experiment.duration;
    if(Math.abs(Number(probe.format.duration)-expected)>.15)throw new Error(`Wrong ${name} duration`);
    const decode=spawnSync('ffmpeg',['-v','error','-i',path,'-f','null','-'],{encoding:'utf8'});
    if(decode.status!==0||decode.stderr)throw new Error(`Decode failed for ${name}`);
    videos[mode]=bytes.toString('base64');hashes[mode]=sha(bytes);
    if(receipt.videoSha256&&receipt.videoSha256[mode]!==hashes[mode])throw new Error(`Artifact changed since ${name} receipt`);
  }
  const stills={};
  for(const [i,time]of [6,18,28,40].entries())stills[String(i)]=(await readFile(join(OUT,'rendered',`${engine}-core-at-${time}.png`))).toString('base64');
  stills.blocked=(await readFile(join(OUT,'rendered',`${engine}-blocked-at-4.png`))).toString('base64');
  const packageName=engine==='motion-canvas'?'@motion-canvas/core':engine==='remotion'?'remotion':null;
  const toolVersion=packageName?require(`${packageName}/package.json`).version:engine==='manim'?'0.22.0':'vendored kit';
  candidates[engine]={name,videos,stills,provenance:{...receipt,toolVersion,videoSha256:hashes}};
}
const prompts={};
for(const key of ['common','anatomy','manim','motion-canvas','remotion'])prompts[key]=await readFile(join(HERE,'prompts',`${key}.md`),'utf8');
const result=await build({entryPoints:[join(HERE,'viewer.ts')],bundle:true,platform:'browser',format:'iife',target:'es2023',write:false,minify:true});
const script=result.outputFiles[0].text.replace(/<\/script/gi,'<\\/script');
const css=await readFile(join(HERE,'page.css'),'utf8');
const data=JSON.stringify({version:story.version,candidates,prompts}).replace(/</g,'\\u003c');
const html=(await readFile(join(HERE,'page.html'),'utf8')).replace('/*STYLE*/',()=>css).replace('/*DATA*/',()=>data).replace('/*SCRIPT*/',()=>script);
await writeFile(join(OUT,'index.html'),html);
await writeFile(join(OUT,'manifest.json'),JSON.stringify({version:story.version,pageSha256:sha(html),bytes:Buffer.byteLength(html),
  engines:Object.fromEntries(Object.entries(candidates).map(([id,value])=>[id,value.provenance])),
  promptSha256:Object.fromEntries(Object.entries(prompts).map(([id,value])=>[id,sha(value)])),
  technicalReview:'pending',ownerReview:'pending',beginnerLearning:'unmeasured'},null,2));
