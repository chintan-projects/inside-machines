/** Owner-operated local production. Executes only the finite trusted source registry. */
import {build} from 'esbuild';
import {createHash} from 'node:crypto';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
import {resolve,relative,join} from 'node:path';
import {pathToFileURL} from 'node:url';

const root=resolve(import.meta.dirname,'..'),scratch=join(root,'.vercel/native-export');
const sha=value=>createHash('sha256').update(value).digest('hex');
const python=(args,input)=>JSON.parse(execFileSync(join(root,'.venv/bin/python'),args,
  {cwd:root,input:JSON.stringify(input),encoding:'utf8',timeout:60000,maxBuffer:32*1024*1024}));

async function loadDefinitions() {
  await mkdir(scratch,{recursive:true});
  const output=join(scratch,`definitions-${process.pid}.mjs`);
  await build({absWorkingDir:root,entryPoints:[join(root,'native/definitions.ts')],bundle:true,platform:'node',format:'esm',outfile:output,logLevel:'silent'});
  return import(pathToFileURL(output).href+`?v=${Date.now()}`);
}
async function sourceIdentity(entry) {
  const graph=await build({absWorkingDir:root,entryPoints:[join(root,entry.entry)],bundle:true,platform:'node',format:'esm',write:false,metafile:true,logLevel:'silent'});
  const names=[...Object.keys(graph.metafile.inputs),'public/fonts/Inter.ttf'];
  const sources=await Promise.all([...new Set(names)].sort().map(async name=>{
    const file=resolve(root,name),local=relative(root,file);
    if(local.startsWith('..')||local.includes('node_modules/'))throw new Error('Untrusted renderer dependency');
    return {path:local,sha256:sha(await readFile(file))};
  }));
  return sources;
}
async function writeRegistry() {
  const {nativeDefinitions,rendererEntries}=await loadDefinitions(),definitions=nativeDefinitions();
  const renderers=[],specs={};
  for(const entry of rendererEntries) {
    const own=definitions.filter(item=>item.spec.renderer.id===entry.id);
    if(!own.length)throw new Error(`No lessons for ${entry.id}`);
    const identity={id:entry.id,lessons:own.map(item=>item.spec.canonical).sort(),sources:await sourceIdentity(entry)};
    // Hash the exact Python canonical bytes, not JS's number serialization.
    const encoded=execFileSync(join(root,'.venv/bin/python'),['-c',
      'import sys,json; print(json.dumps(json.load(sys.stdin),sort_keys=True,separators=(",",":")),end="")'],
    {input:JSON.stringify(identity),encoding:'utf8',timeout:10000});
    const entryFingerprint=sha(encoded),hashes={};
    for(const item of own) {
      const normalized=python(['-m','backend.native_publication','canonicalize'],
        {...item.spec,renderer:{id:entry.id,fingerprint:entryFingerprint}});
      specs[item.spec.canonical]=normalized.canonical_json;hashes[item.spec.canonical]=normalized.sha256;
    }
    renderers.push({...identity,fingerprint:entryFingerprint,spec_sha256:hashes});
  }
  const previous=JSON.parse(await readFile(join(root,'native/registry.json'),'utf8'));
  const oldSpecs=JSON.parse(await readFile(join(root,'native/specs.json'),'utf8'));
  for(const entry of previous.renderers) {
    const fresh=renderers.find(item=>item.id===entry.id);
    if(fresh&&JSON.stringify(fresh)!==JSON.stringify(entry))throw new Error(`Registered native revision ${entry.id} is immutable. Use a new renderer/lesson revision.`);
    if(!fresh)renderers.push(entry);
  }
  await writeFile(join(root,'native/registry.json'),JSON.stringify({schema_version:'native-renderers-1',renderers},null,2)+'\n');
  await writeFile(join(root,'native/specs.json'),JSON.stringify({...oldSpecs,...specs},null,2)+'\n');
  process.stdout.write(`Registered ${Object.keys(specs).length} native revisions. No publication or paid calls.\n`);
}
function frameFor(definition,time,controls,scenarioId='') {
  const state=definition.lesson.stateAt(time,controls),scene=definition.lesson.render(state);
  return {cue_id:state.beatId,time,scenario_id:scenarioId,controls,...scene,
    viewport:scene.viewport??{x:0,y:0,width:720,height:620}};
}
function checkpoints(definition,spec) {
  const frames=[];
  for(const cue of spec.stages) {
    const times=cue.kind==='causal'?[cue.start+.05,cue.still,cue.end-.05]:[cue.still];
    for(const time of times)frames.push(frameFor(definition,time,spec.default_controls));
  }
  for(const scenario of spec.teaching.scenarios) {
    const cue=spec.stages.find(item=>item.id===scenario.cue_id);
    if(!cue)throw new Error('Scenario has no reviewed cue');
    frames.push(frameFor(definition,cue.still,{...spec.default_controls,...scenario.controls},scenario.id));
  }
  return frames;
}
async function prepare(output) {
  if(!output.startsWith(join(root,'.vercel/') ))throw new Error('Production proofs and media must stay under ignored .vercel/');
  const {nativeDefinitions,nativeSuggestedPath}=await loadDefinitions(),definitions=nativeDefinitions();
  const registry=JSON.parse(await readFile(join(root,'native/registry.json'),'utf8'));
  const specs=JSON.parse(await readFile(join(root,'native/specs.json'),'utf8'));
  await mkdir(output,{recursive:true});const artifacts=[];
  for(const definition of definitions) {
    const stored=specs[definition.spec.canonical],spec=stored?JSON.parse(stored):undefined;
    const entry=registry.renderers.find(item=>item.id===spec?.renderer.id);
    if(!spec||!entry||!entry.lessons.includes(spec.canonical))throw new Error('Run the registry build before preparation');
    const folder=join(output,spec.canonical);await mkdir(folder,{recursive:true});
    const frames=checkpoints(definition,spec);
    await writeFile(join(folder,'source.json'),JSON.stringify({spec,frames},null,2));
    await writeFile(join(folder,'narration-plan.json'),JSON.stringify({id:`${spec.canonical}-narration`,
      duration:definition.lesson.duration,cues:spec.stages.map(cue=>({start:cue.start,end:cue.end,still:cue.still,text:cue.narration}))}));
    artifacts.push({spec,proof:join(folder,'proof.json'),video_file:join(folder,'lesson.mp4'),
      narration:'Local macOS Samantha computer speech, rendered from the same versioned cue plan; no speech API call.',replaces:[]});
  }
  await writeFile(join(output,'manifest.json'),JSON.stringify({schema_version:'native-publication-1',artifacts,path:nativeSuggestedPath},null,2));
  process.stdout.write(`Prepared ${artifacts.length} native definitions at ${output}. Render and verify before import.\n`);
}
async function speech(folder) {
  const {renderNarration}=await import('../experiments/visual-studio/render-narration.mjs');
  const plan=JSON.parse(await readFile(join(folder,'narration-plan.json'),'utf8'));
  await renderNarration(plan,join(folder,'narration'));
  process.stdout.write(`Synthesized local computer narration for ${plan.id}. No provider call.\n`);
}
async function finalize(output) {
  const file=join(output,'manifest.json'),manifest=JSON.parse(await readFile(file,'utf8'));
  for(const artifact of manifest.artifacts) {
    const folder=join(output,artifact.spec.canonical);
    artifact.proof=JSON.parse(await readFile(join(folder,'proof.json'),'utf8'));
    artifact.video_file=relative(output,join(folder,'lesson.mp4'));
  }
  await writeFile(file,JSON.stringify(manifest,null,2)+'\n');
  process.stdout.write(`Finalized ${manifest.artifacts.length} local artifacts. Run native_publication verify; nothing is published.\n`);
}
async function stream(id) {
  const {nativeDefinitions}=await loadDefinitions(),definition=nativeDefinitions().find(item=>item.spec.canonical===id);
  if(!definition)throw new Error('Unknown trusted native revision');
  for(let frame=0;frame<Math.ceil(definition.lesson.duration*24);frame++) {
    const value=frameFor(definition,frame/24,definition.lesson.defaultControls);
    if(!process.stdout.write(JSON.stringify(value)+'\n'))await new Promise(resolve=>process.stdout.once('drain',resolve));
  }
}
async function proofFrames(id) {
  const {nativeDefinitions}=await loadDefinitions(),definition=nativeDefinitions().find(item=>item.spec.canonical===id);
  const specs=JSON.parse(await readFile(join(root,'native/specs.json'),'utf8'));
  if(!definition||!specs[id])throw new Error('Unknown trusted native revision');
  process.stdout.write(JSON.stringify(checkpoints(definition,JSON.parse(specs[id]))));
}
const [command,argument]=process.argv.slice(2);
if(command==='registry')await writeRegistry();
else if(command==='prepare'&&argument)await prepare(resolve(argument));
else if(command==='frames'&&argument)await stream(argument);
else if(command==='checkpoints'&&argument)await proofFrames(argument);
else if(command==='speech'&&argument)await speech(resolve(argument));
else if(command==='finalize'&&argument)await finalize(resolve(argument));
else throw new Error('Usage: node native/export.mjs registry | prepare <ignored-output-folder> | frames <trusted-revision> | speech <prepared-folder> | finalize <ignored-output-folder>');
