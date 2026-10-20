/** Trusted local study composition. No arbitrary client-selected entry or remote code. */
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {gpuNarration} from '../gpu-study/narration.ts';
import {coreNarration,memoryNarration,matrixNarration} from '../gpu-study/depth-narration.ts';
import {parsePath} from './path-contract.ts';
import {validateNarration} from './narration.ts';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
// A registry is enough. New studies add a trusted entry and separately reviewed artwork.
const studies=Object.freeze({gpu:{operation:'gpu-art-1',entry:'experiments/gpu-study/entry.ts',title:'How does a GPU work?',
  narrations:[gpuNarration,coreNarration,memoryNarration,matrixNarration],
  pathFile:'experiments/gpu-study/path.json',lessons:['gpu-core-s3','gpu-study-1','gpu-memory-s3','gpu-matrix-s3']}});
const study=process.argv[2]||'gpu';
if(!Object.hasOwn(studies,study))throw new Error('Unsupported local study');
const selected=studies[study], operation=selected.operation;
const privateDir=path.join(root,'.vercel/claude-vacuum/private');
const out=path.join(root,'.vercel/visual-studio/public',study);
const [original,art,repairs,css,license]=await Promise.all([
  readFile(path.join(privateDir,operation+'.txt'),'utf8'),
  readFile(path.join(privateDir,operation+'-reviewed.js'),'utf8'),
  readFile(path.join(privateDir,operation+'-repairs.json'),'utf8').then(JSON.parse),
  readFile(path.join(root,'experiments/visual-studio/theme.css'),'utf8'),
  readFile(path.join(root,'vendor/anatomy/LICENSE'),'utf8'),
]);
const sha=s=>createHash('sha256').update(s).digest('hex');
const learningPath=parsePath(JSON.parse(await readFile(path.join(root,selected.pathFile),'utf8')),selected.lessons);
const audioAssets={},audioManifests=[];
for(const plan of selected.narrations) {
  validateNarration(plan);
  const audioDir=path.join(privateDir,plan.id===gpuNarration.id?'gpu-s2-audio':`gpu-s3-audio/${plan.id}`);
  const [mp3,manifest]=await Promise.all([readFile(path.join(audioDir,'narration.mp3')),
    readFile(path.join(audioDir,'manifest.json'),'utf8').then(JSON.parse)]);
  if(manifest.plan_sha256!==sha(JSON.stringify(plan))||manifest.mp3_sha256!==sha(mp3)||
      manifest.story_seconds!==plan.duration||Math.abs(manifest.encoded_seconds-plan.duration)>.15) {
    throw new Error('Narration asset does not match the reviewed cue plan');
  }
  audioAssets[plan.id]={planId:plan.id,src:'data:audio/mpeg;base64,'+mp3.toString('base64')};
  audioManifests.push({...manifest,clips:undefined});
}
// The same portable data must pass backend/API boundary validation too.
const schema=execFileSync(path.join(root,'.venv/bin/python'),['-c',
  'import json,sys; import backend; from backend.learning_paths import LearningPath,validate_path; validate_path(sys.argv[1],set(json.loads(sys.argv[2]))); sys.stdout.write(json.dumps(LearningPath.model_json_schema()))',
  JSON.stringify(learningPath),JSON.stringify(selected.lessons)],{cwd:root,encoding:'utf8'});
if(repairs.original_sha256!==sha(original)||repairs.reviewed_sha256!==sha(art))throw new Error('Art repair chain mismatch');
const forbidden=[/\bfetch\s*\(/,/\bXMLHttpRequest\b/,/\bWebSocket\b/,/\bimport\s*\(/,
  /\beval\s*\(/,/\bFunction\s*\(/,/\blocalStorage\b/,/\bsessionStorage\b/,/\bserviceWorker\b/,
  /\bprocess\b/,/\brequire\s*\(/,/\bdocument\b/,/\blocation\b/,/\bnavigator\b/,/\bsetInterval\b/];
if(forbidden.some(r=>r.test(art)))throw new Error('Inspect unsupported art execution/network construct');
const receipts=JSON.parse(execFileSync(path.join(root,'.venv/bin/python'),['-c',
  'import json; import backend; from pathlib import Path; from backend.store import Store; s=Store("",Path(".vercel/claude-vacuum/private")).snapshot(); print(json.dumps({"spent":s.spent,"ledger":s.ledger,"jobs":s.jobs}))',
],{cwd:root,encoding:'utf8'}));
if(receipts.jobs[operation]?.status!=='completed'||receipts.jobs[operation]?.output_sha256!==sha(original))throw new Error('Unsettled art checkpoint');
const esbuild=await import(pathToFileURL(path.join(root,'.vercel/vacuum-lab/runtime/node_modules/esbuild/lib/main.js')));
const bundle=async entry=>(await esbuild.build({entryPoints:[path.join(root,entry)],bundle:true,write:false,
  format:'iife',platform:'browser',minify:true})).outputFiles[0].text;
const [runtime,player]=await Promise.all([bundle('experiments/visual-studio/runtime.mjs'),bundle(selected.entry)]);
const receipt=receipts.ledger[operation];
const metadata={study,operation,model:receipt.models,input_tokens:receipt.input_tokens,output_tokens:receipt.output_tokens,
  prompt_sha256:receipts.jobs[operation].prompt_sha256,config_sha256:receipts.jobs[operation].config_sha256,
  list_price_cost_usd:receipt.cost_usd,trial_accounted_usd:receipts.spent,api_art_sha256:sha(original),art_sha256:sha(art),
  runtime_sha256:sha(runtime),player_sha256:sha(player),manual_repairs:repairs.changes,
  narrations:audioManifests,learning_path_sha256:sha(JSON.stringify(learningPath)),
  craft_feedback:'pending for GPU; vacuum received positive owner feedback',technical_review:'pending',learning:'unmeasured'};
const script=code=>`<script>${code.replaceAll('</script','<\\/script')}</script>`;
const csp="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; connect-src 'none'; font-src 'none'; media-src data:; frame-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'; worker-src 'none'";
const narration=script(`window.studioNarrations=${JSON.stringify(audioAssets)};window.studioPath=${JSON.stringify(learningPath)};`);
const html=`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="${csp}"><title>${selected.title}</title><style>${css}</style></head><body><div id="app"></div><noscript>A program specifies work; memory supplies data; the GPU calculates and stores results. This interactive local draft needs JavaScript. Optional paths explain independent work, data supply and matrix multiplication.</noscript><footer class="provenance"><p><a href="http://127.0.0.1:8067/">Revisit the vacuum example</a></p><details><summary>About this local learning study</summary><p>Claude authored the original Anatomy board and parallel-work artwork. Codex authored the new complete story, data-supply and matrix views, pure domain rules, versioned learning path and shared navigation/player. Narration is embedded local computer speech (Samantha); captions follow the same cue plans. Question lookup opens saved explanations; it is not AI chat. This is a manually inspected local experiment; production consumes validated lesson data instead. Viewing makes no model call. No MP4 export or automatic new-topic generation is included. Human technical, actual-device, learning and release gates remain pending.</p><pre>${JSON.stringify(metadata,null,2).replaceAll('<','&lt;')}</pre></details></footer>${script('/* Anatomy MIT license\n'+license+'*/\n'+runtime)}${script(art)}${narration}${script(player)}</body></html>`;
await mkdir(out,{recursive:true});await writeFile(path.join(out,'index.html'),html);
await writeFile(path.join(privateDir,operation+'-studio-manifest.json'),JSON.stringify({...metadata,html_sha256:sha(html)},null,2));
await writeFile(path.join(out,'learning-path.schema.json'),schema);
