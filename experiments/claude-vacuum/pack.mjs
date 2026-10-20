import {readFile, writeFile, mkdir} from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {execFileSync} from 'node:child_process';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const privateDir = path.join(root, '.vercel/claude-vacuum/private');
const publicDir = path.join(root, '.vercel/claude-vacuum/public');
const operation = process.argv[2] || 'initial';
if (!/^[a-zA-Z0-9-]{1,60}$/.test(operation)) throw new Error('Invalid operation');
const original = await readFile(path.join(privateDir, operation + '.txt'), 'utf8');
const useRepairs = process.argv[3] === 'reviewed';
let repairs = null;
let html = original;
if (useRepairs) {
  repairs = JSON.parse(await readFile(path.join(privateDir, operation + '-repairs.json'), 'utf8'));
  html = await readFile(path.join(privateDir, operation + '-reviewed.html'), 'utf8');
}
if (!/^<!doctype html>/i.test(html.trimStart()) || !html.includes('</html>')) throw new Error('Incomplete HTML');
if (html.split('<!-- ANATOMY_RUNTIME -->').length !== 2) throw new Error('Missing or duplicate runtime insertion');
const prohibited = [/\bfetch\s*\(/, /\bXMLHttpRequest\b/, /\bWebSocket\b/, /\bimport\s*\(/,
  /<script[^>]+src\s*=/i, /\beval\s*\(/, /\blocalStorage\b/, /\bserviceWorker\b/, /\bprocess\.env\b/];
if (prohibited.some(rule => rule.test(html))) throw new Error('Inspect unexpected network/execution/storage code');
const esbuild = await import(pathToFileURL(path.join(root, '.vercel/vacuum-lab/runtime/node_modules/esbuild/lib/main.js')));
const bundle = await esbuild.build({
  entryPoints: [path.join(root, 'experiments/claude-vacuum/runtime.mjs')],
  bundle: true, write: false, format: 'iife', platform: 'browser', minify: true,
});
const license = await readFile(path.join(root, 'vendor/anatomy/LICENSE'), 'utf8');
const runtime = ('/* Anatomy toolkit — ' + license + ' */\n' + bundle.outputFiles[0].text).replaceAll('</script', '<\\/script');
const csp = `<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; connect-src 'none'; font-src 'none'; media-src 'none'; frame-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'; worker-src 'none'">`;
let packed = html.replace(/<head[^>]*>/i, match => match + csp)
  .replace('<!-- ANATOMY_RUNTIME -->', `<script>${runtime}</script>`);
const sha = value => createHash('sha256').update(value).digest('hex');
const receipt = JSON.parse(execFileSync(path.join(root, '.venv/bin/python'), ['-c',
  'import json; import backend; from pathlib import Path; from backend.store import Store; s=Store("",Path(".vercel/claude-vacuum/private")).snapshot(); print(json.dumps({"spent":s.spent,"ledger":s.ledger,"jobs":s.jobs}))',
], {cwd: root, encoding: 'utf8'}));
if (receipt.jobs[operation]?.output_sha256 !== sha(original)) throw new Error('Output does not match settled operation');
if (repairs && (repairs.original_sha256 !== sha(original) || repairs.reviewed_sha256 !== sha(html))) throw new Error('Repair chain mismatch');
const metadata = {
  operation, api_source_sha256: sha(original), source_sha256: sha(html), runtime_sha256: sha(runtime),
  manual_repairs: repairs?.changes || [],
  model: receipt.ledger[operation].models,
  prompt_sha256: receipt.jobs[operation].prompt_sha256,
  requested_effort: receipt.jobs[operation].config?.effort,
  thinking_mode: receipt.jobs[operation].config?.thinking || 'adaptive',
  authoring_seconds: receipt.jobs[operation].duration_seconds,
  input_tokens: receipt.ledger[operation].input_tokens,
  output_tokens: receipt.ledger[operation].output_tokens,
  list_price_cost_usd: receipt.ledger[operation].cost_usd,
  trial_accounted_usd: receipt.spent,
  human_approval: 'unmeasured', technical_review: 'pending', learning: 'unmeasured',
};
const authorship = repairs
  ? 'Claude authored the base HTML through the API using the real Anatomy kit. Codex supplied the brief, inspected renders, and applied the listed geometry, responsive and playback repairs. The original API response is preserved.'
  : 'Claude authored this HTML through the API using the real Anatomy kit. Codex supplied the brief, integration and inspection.';
const provenance = `<footer style="max-width:1100px;margin:24px auto;padding:16px 24px;font:13px/1.6 system-ui;color:#646464"><details><summary>About this Claude + Anatomy trial</summary><p>${authorship} This is a teaching draft, with technical and human learning review pending. No model call occurs when viewing.</p><pre style="white-space:pre-wrap;overflow-wrap:anywhere">${JSON.stringify(metadata, null, 2)}</pre></details></footer>`;
// The embedded kit contains pageHtml() string templates with their own body tags.
// Insert at the actual document's final close, never inside that library source.
const bodyEnd = packed.lastIndexOf('</body>');
if (bodyEnd < 0) throw new Error('Missing document body');
packed = packed.slice(0, bodyEnd) + provenance + packed.slice(bodyEnd);
await mkdir(publicDir, {recursive: true});
await writeFile(path.join(publicDir, 'index.html'), packed);
await writeFile(path.join(privateDir, operation + '-manifest.json'), JSON.stringify({...metadata, html_sha256: sha(packed)}, null, 2));
