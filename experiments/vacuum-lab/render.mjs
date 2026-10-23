/** Actual local render orchestration. Outputs/dependencies stay in ignored .vercel. */
import {readFile, writeFile, mkdir, rmdir} from 'node:fs/promises';
import {createRequire} from 'node:module';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {dirname, join, resolve} from 'node:path';
import {spawnSync, spawn} from 'node:child_process';
import {createServer} from 'node:http';
import {createHash} from 'node:crypto';
import {anatomySvg} from './anatomy.mjs';

const HERE=dirname(fileURLToPath(import.meta.url));
const ROOT=resolve(HERE,'../..');
const OUT=join(ROOT,'.vercel/vacuum-lab');
const RUNTIME=process.env.VACUUM_LAB_RUNTIME??join(OUT,'runtime');
const require=createRequire(join(RUNTIME,'package.json'));
const esbuild=require('esbuild');
const puppeteer=require('puppeteer');
const {Resvg}=require('@resvg/resvg-js');
const story=JSON.parse(await readFile(join(HERE,'story.json'),'utf8'));
await mkdir(join(OUT,'rendered'),{recursive:true});
await esbuild.build({entryPoints:[join(HERE,'model.ts')],bundle:true,platform:'node',format:'esm',
  outfile:join(OUT,'model.mjs'),target:'es2023'});
const {stateAt,duration}=await import(pathToFileURL(join(OUT,'model.mjs')).href);

/** @param {string} command @param {string[]} args @param {object} [options] @returns {void} */
function execute(command,args,options={}) {
  const r=spawnSync(command,args,{cwd:ROOT,encoding:'utf8',maxBuffer:8*1024*1024,...options});
  if(r.status!==0) throw new Error(`${command} failed: ${r.stderr?.slice(-2500)??r.error}`);
}
/** @param {Buffer|string} value @returns {string} */
function sha(value){return createHash('sha256').update(value).digest('hex');}
/** @param {boolean} blocked @returns {string} */
function key(blocked){return blocked?'blocked':'core';}
/** @param {boolean} blocked @returns {number} */
function count(blocked){return(blocked?story.experiment.duration:duration)*story.fps;}

/** Pad each narration beat to its exact shared chapter duration. No paid speech call. */
async function audio(){
  const all=[...story.beats,{...story.experiment,id:'blocked'}];
  for(const beat of all){
    const text=join(OUT,`${beat.id}.txt`), aiff=join(OUT,`${beat.id}.aiff`), wav=join(OUT,`${beat.id}.wav`);
    await writeFile(text,beat.narration);
    execute('/usr/bin/say',['-v','Samantha','-r','168','-f',text,'-o',aiff]);
    const measured=spawnSync('ffprobe',['-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',aiff],{encoding:'utf8'});
    const spoken=Number(measured.stdout);
    if(!Number.isFinite(spoken)||spoken>beat.duration) throw new Error(`Narration exceeds ${beat.id}: ${spoken}`);
    execute('ffmpeg',['-v','error','-y','-i',aiff,'-af',`apad=whole_dur=${beat.duration}`,'-t',String(beat.duration),'-ar','24000','-ac','1',wav]);
  }
  const files=story.beats.map(/** @param {{id:string}} beat */beat=>`file '${join(OUT,`${beat.id}.wav`)}'`).join('\n');
  await writeFile(join(OUT,'audio-list.txt'),files);
  execute('ffmpeg',['-v','error','-y','-f','concat','-safe','0','-i',join(OUT,'audio-list.txt'),'-c','copy',join(OUT,'core.wav')]);
}

/** @param {string} engine @param {boolean} blocked @param {(frame:number)=>Promise<Buffer>} draw */
async function encodeFrames(engine,blocked,draw){
  const name=`${engine}-${key(blocked)}`, destination=join(OUT,'rendered',`${name}-silent.mp4`);
  const encoder=spawn('ffmpeg',['-v','error','-y','-f','image2pipe','-framerate',String(story.fps),'-i','pipe:0',
    '-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',destination],{stdio:['pipe','ignore','pipe']});
  let failure=''; encoder.stderr.setEncoding('utf8');encoder.stderr.on('data',/** @param {string} chunk */chunk=>{failure+=chunk;});
  const done=new Promise((resolve,reject)=>{encoder.on('error',reject);encoder.on('exit',code=>code===0?resolve(0):reject(new Error(failure)));});
  try{
    for(let i=0;i<count(blocked);i++){
      const png=await draw(i);
      if(i===0||(!blocked&&[6,18,28,40].includes(i/story.fps))) await writeFile(join(OUT,'rendered',`${name}-${i}.png`),png);
      if(!encoder.stdin.write(png)) await new Promise(resolve=>encoder.stdin.once('drain',resolve));
    }
    encoder.stdin.end();await done;
  }catch(error){encoder.kill();await done.catch(()=>undefined);throw error;}
}

/** Actual Anatomy kit → SVG → resvg frames. */
async function anatomy(){
  for(const blocked of [false,true]) await encodeFrames('anatomy',blocked,async i=>{
    const svg=anatomySvg(stateAt(i/story.fps,blocked));
    if(i===0)await writeFile(join(OUT,'rendered',`anatomy-${key(blocked)}.svg`),svg);
    return new Resvg(svg,{font:{loadSystemFonts:false,fontFiles:['/System/Library/Fonts/Supplemental/Arial.ttf'],defaultFontFamily:'Arial'}}).render().asPng();
  });
}

/** Actual Motion Canvas Scene2D + PlaybackManager + Stage frames in Chromium. */
async function motion(){
  await esbuild.build({entryPoints:[join(HERE,'motion-canvas.ts')],bundle:true,platform:'browser',format:'iife',
    outfile:join(OUT,'motion.js'),target:'es2022',nodePaths:[join(RUNTIME,'node_modules')],
    define:{'import.meta.hot':'undefined'}});
  const server=createServer(async(req,res)=>{
    if(req.url?.startsWith('/motion.js')){res.setHeader('Content-Type','text/javascript');res.end(await readFile(join(OUT,'motion.js')));}
    else{res.setHeader('Content-Type','text/html');res.end('<!doctype html><html><body style="margin:0"><script src="/motion.js"></script></body></html>');}
  });
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  const address=server.address();if(!address||typeof address==='string')throw new Error('Local motion server failed');
  const browser=await puppeteer.launch({headless:true,args:['--no-sandbox'],defaultViewport:{width:960,height:720}});
  try{
    for(const blocked of [false,true]){
      const page=await browser.newPage();const errors=[];
      page.on('pageerror',/** @param {Error} e */e=>errors.push(e.message));
      await page.goto(`http://127.0.0.1:${address.port}/?blocked=${blocked?'1':'0'}`);
      await page.waitForFunction('window.motionReady===true',{timeout:30000}).catch(e=>{throw new Error(`${e.message}: ${errors.join(';')}`);});
      await encodeFrames('motion-canvas',blocked,async i=>Buffer.from(await page.evaluate(async frame=>await window.drawMotionFrame(frame),i),'base64'));
      if(errors.length)throw new Error(errors.join(';'));await page.close();
    }
  }finally{await browser.close();await new Promise(resolve=>server.close(resolve));}
}

/** Actual Remotion Webpack bundle → Chromium renderMedia output. */
async function remotion(){
  const {bundle}=require('@remotion/bundler');
  const {renderMedia,selectComposition}=require('@remotion/renderer');
  const serveUrl=await bundle({entryPoint:join(HERE,'remotion.tsx'),outDir:join(OUT,'remotion-bundle'),
    webpackOverride:config=>({...config,resolve:{...config.resolve,modules:[join(RUNTIME,'node_modules'),join(ROOT,'node_modules'),'node_modules']}})});
  const browserExecutable=await puppeteer.executablePath();
  for(const blocked of [false,true]){
    const id=blocked?'Blocked':'Vacuum';
    const composition=await selectComposition({serveUrl,id,browserExecutable});
    await renderMedia({serveUrl,composition,codec:'h264',outputLocation:join(OUT,'rendered',`remotion-${key(blocked)}-silent.mp4`),
      browserExecutable,concurrency:2,crf:20});
  }
}

/** Actual Manim process reads common frame states; no independent causal rules. */
async function manim(){
  for(const blocked of [false,true]){
    const frames=Array.from({length:count(blocked)},(_,i)=>stateAt(i/story.fps,blocked));
    const file=join(OUT,`${key(blocked)}-frames.json`);await writeFile(file,JSON.stringify(frames));
    const target=join(OUT,'rendered',`manim-${key(blocked)}-silent.mp4`);
    execute(join(OUT,'python/bin/manim'),['render','--disable_caching','--media_dir',join(OUT,'manim-media'),
      '-o',target,join(HERE,'manim_scene.py'),'VacuumProof'],{env:{...process.env,VACUUM_LAB_FRAMES:file},timeout:600000});
  }
}

/** @param {string} engine */
async function finish(engine){
  for(const blocked of [false,true]){
    const prefix=join(OUT,'rendered',`${engine}-${key(blocked)}`);
    execute('ffmpeg',['-v','error','-y','-i',`${prefix}-silent.mp4`,'-i',join(OUT,`${key(blocked)}.wav`),
      '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','96k','-t',String(blocked?story.experiment.duration:duration),'-movflags','+faststart',`${prefix}.mp4`]);
    for(const time of blocked?[0,4]:[0,6,18,28,40]) execute('ffmpeg',['-v','error','-y','-ss',String(time),'-i',`${prefix}.mp4`,'-frames:v','1',`${prefix}-at-${time}.png`]);
  }
}

const commands={audio,anatomy,manim,motion,remotion};
const adapterFiles={anatomy:'anatomy.mjs',manim:'manim_scene.py',motion:'motion-canvas.ts',remotion:'remotion.tsx'};
const requested=process.argv[2]??'all';
const names=requested==='all'?Object.keys(commands):[requested];
for(const name of names){
  if(!(name in commands))throw new Error('Expected audio, anatomy, manim, motion, remotion or all');
  const lock=join(OUT,`.render-${name}.lock`);
  await mkdir(lock);
  try {
  const source=adapterFiles[name]?await readFile(join(HERE,adapterFiles[name])):null;
  const sourceSha256=source?sha(source):null;
  const started=Date.now();await commands[name]();
  const engine=name==='motion'?'motion-canvas':name;
  if(name!=='audio')await finish(engine);
  await writeFile(join(OUT,`${name}-receipt.json`),JSON.stringify({engine,elapsedSeconds:(Date.now()-started)/1000,
    author:'OpenAI Codex interactive coding session',apiModelIdentity:null,apiTokenUsage:null,
    appPaidModelCalls:0,storySha256:sha(await readFile(join(HERE,'story.json'))),
    sourceSha256,
    videoSha256:name==='audio'?null:Object.fromEntries(await Promise.all(['core','blocked'].map(async mode=>[mode,sha(await readFile(join(OUT,'rendered',`${engine}-${mode}.mp4`)))]))),
    limitation:'Human-directed prototype, not an autonomous API generation benchmark.'},null,2));
  } finally {await rmdir(lock);}
}
