/** Read-only build gate: registering new artwork is always an explicit owner operation. */
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {resolve,relative} from 'node:path';
import {pathToFileURL} from 'node:url';

const digest=bytes=>createHash('sha256').update(bytes).digest('hex');
const stable=value=>JSON.stringify(value,(_key,item)=>item&&typeof item==='object'&&!Array.isArray(item)
  ?Object.fromEntries(Object.entries(item).sort(([a],[b])=>a<b?-1:a>b?1:0)):item);

export async function verifyNativeSources(root,registry) {
  if(registry.schema_version!=='native-renderers-1'||!Array.isArray(registry.renderers))throw new Error('Invalid native renderer registry');
  for(const entry of registry.renderers) {
    const identity={id:entry.id,lessons:entry.lessons,sources:entry.sources};
    if(digest(stable(identity))!==entry.fingerprint)throw new Error(`Native identity changed: ${entry.id}`);
    for(const source of entry.sources) {
      const file=resolve(root,source.path),local=relative(root,file);
      if(local.startsWith('..')||!local||digest(await readFile(file))!==source.sha256)
        throw new Error(`Native source changed without a new reviewed revision: ${source.path}`);
    }
  }
  return registry.renderers.length;
}
export function verifyNativeSpecs(registry,specs) {
  for(const entry of registry.renderers)for(const id of entry.lessons) {
    if(typeof specs[id]!=='string'||digest(specs[id])!==entry.spec_sha256[id])
      throw new Error(`Native semantic metadata changed without a new reviewed revision: ${id}`);
  }
}
if(process.argv[1]&&import.meta.url===pathToFileURL(resolve(process.argv[1])).href) {
  const root=resolve(import.meta.dirname,'..'),registry=JSON.parse(await readFile(resolve(root,'native/registry.json'),'utf8'));
  const count=await verifyNativeSources(root,registry);
  verifyNativeSpecs(registry,JSON.parse(await readFile(resolve(root,'native/specs.json'),'utf8')));
  process.stdout.write(`Verified ${count} exact native renderer source registrations.\n`);
}
