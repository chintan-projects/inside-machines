import assert from 'node:assert/strict';
import { existsSync, readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
const root = process.argv[2] || '.vercel/linux-validation/.vercel/output';
function configs(folder) {
  return readdirSync(folder, { withFileTypes: true }).flatMap(entry => {
    const path = join(folder, entry.name);
    return entry.isDirectory() ? configs(path) : entry.name === '.vc-config.json' ? [path] : [];
  });
}
const functions = configs(join(root, 'functions')).map(path => ({ path, config:JSON.parse(readFileSync(path, 'utf8')) }));
const api = functions.find(f => f.path.includes('fastapi.func'));
assert.ok(api, 'The API function must be packaged');
assert.equal(api.config.maxDuration, 300);
assert.ok(functions.some(f => f.config.experimentalTriggers?.some(t => t.type === 'queue/v2beta' && t.topic === 'inside-lessons' && t.maxConcurrency === 1)), 'A real queue subscriber must be packaged');
for (const { path, config } of functions) {
  const names = Object.keys(config.filePathMap || {});
  assert.ok(!names.some(name => name === '.env.local' || name.startsWith('.data/') || name === '.vercel/alpha-access.json'), `${path}: private local inputs must be excluded`);
  assert.ok(names.some(name => name.endsWith('public/fonts/Inter.ttf')), `${path}: the diagram font must be bundled`);
  assert.ok(names.some(name => name.endsWith('native/registry.json')), `${path}: native artwork identities must be bundled`);
  for (const asset of ['ac-outside.svg', 'ac-inside.svg', 'vacuum-fan.svg', 'vacuum-nozzle.svg', 'vacuum-bag.svg', 'vacuum-context.svg']) assert.ok(names.some(name => name.endsWith(`public/figures/${asset}`)), `${path}: immutable cutaway sources must be bundled`);
  assert.ok(names.some(name => name.includes('resvg_py/') && name.endsWith('.so')), `${path}: the Linux SVG rasterizer must be bundled`);
  assert.ok(names.some(name => name.includes('_shared/services/model_gateway/')), `${path}: actual shared gateway must be bundled`);
  assert.ok(names.some(name => name.includes('imageio_ffmpeg/binaries/') && name.includes('linux')), `${path}: Linux video encoder must be bundled`);
}
assert.ok(existsSync(join(root, 'static/index.html')), 'The built app shell must be served from the CDN');
assert.ok(existsSync(join(root, 'static/shell-assets.json')), 'The offline asset manifest must be served');
assert.match(readFileSync(join(root, 'static/sw.js'), 'utf8'), /inside-shell-[a-f0-9]{12}/, 'Serve the built, versioned service worker');
console.log(`Verified ${functions.length} Python functions, durable queue trigger, private-input exclusions, shared services, Linux encoder and versioned CDN shell.`);
