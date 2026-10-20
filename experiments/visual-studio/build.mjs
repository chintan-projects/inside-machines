/** Trusted local study composition. No arbitrary client-selected entry or remote code. */
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
// A registry is enough. New studies add a trusted entry and separately reviewed artwork.
const studies=Object.freeze({gpu:{operation:'gpu-art-1',entry:'experiments/gpu-study/entry.ts',title:'How does a GPU work?'}});
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
  craft_feedback:'pending for GPU; vacuum received positive owner feedback',technical_review:'pending',learning:'unmeasured'};
const script=code=>`<script>${code.replaceAll('</script','<\\/script')}</script>`;
const csp="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; connect-src 'none'; font-src 'none'; media-src 'none'; frame-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'; worker-src 'none'";
const html=`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="${csp}"><title>${selected.title}</title><style>${css}</style></head><body><div id="app"></div><noscript>This interactive local draft needs JavaScript. Its core idea: independent jobs can run together; a dependent job must wait for its input. More lanes cannot remove a dependency.</noscript><footer class="provenance"><p><a href="http://127.0.0.1:8067/">Revisit the vacuum example</a></p><details><summary>About this local Claude + Anatomy study</summary><p>Claude authored the board and logical artwork. Codex authored the exact toy scheduler, teaching adapter, shared player and listed art repairs. This is a manually inspected local code-authoring experiment; production consumes validated lesson data instead. Viewing makes no model call. No narrated video export is included. Human technical, actual-device, learning and release gates remain pending.</p><pre>${JSON.stringify(metadata,null,2).replaceAll('<','&lt;')}</pre></details></footer>${script('/* Anatomy MIT license\n'+license+'*/\n'+runtime)}${script(art)}${script(player)}</body></html>`;
await mkdir(out,{recursive:true});await writeFile(path.join(out,'index.html'),html);
await writeFile(path.join(privateDir,operation+'-studio-manifest.json'),JSON.stringify({...metadata,html_sha256:sha(html)},null,2));
