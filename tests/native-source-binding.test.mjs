import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,writeFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createHash} from 'node:crypto';
import {verifyNativeSources,verifyNativeSpecs} from '../native/verify.mjs';
const sha=value=>createHash('sha256').update(value).digest('hex');
const stable=value=>JSON.stringify(value,(_key,item)=>item&&typeof item==='object'&&!Array.isArray(item)
  ?Object.fromEntries(Object.entries(item).sort()):item);

test('a source-only artwork change cannot ship under an earlier reviewed renderer identity',async()=>{
  const root=await mkdtemp(join(tmpdir(),'native-source-'));
  try {
    await writeFile(join(root,'scene.ts'),'original mechanism');
    const identity={id:'test-native-r1',lessons:['test-native-r1'],sources:[{path:'scene.ts',sha256:sha('original mechanism')}]};
    const registry={schema_version:'native-renderers-1',renderers:[{...identity,fingerprint:sha(stable(identity)),spec_sha256:{'test-native-r1':'a'.repeat(64)}}]};
    assert.equal(await verifyNativeSources(root,registry),1);
    await writeFile(join(root,'scene.ts'),'different causal outcome');
    await assert.rejects(verifyNativeSources(root,registry),/source changed/);
    assert.equal(registry.renderers[0].fingerprint,sha(stable(identity)));
  }finally{await rm(root,{recursive:true,force:true});}
});
test('native semantic metadata is verified using the exact canonical string, including fractional serialization',()=>{
  const encoded='{"stages":[{"start":0.0}],"title":"A native lesson"}';
  const registry={renderers:[{lessons:['native-r1'],spec_sha256:{'native-r1':sha(encoded)}}]};
  verifyNativeSpecs(registry,{'native-r1':encoded});
  assert.throws(()=>verifyNativeSpecs(registry,{'native-r1':encoded.replace('0.0','1.0')}),/semantic metadata/);
});
