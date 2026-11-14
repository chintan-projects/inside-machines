import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdtemp,mkdir,writeFile,rm} from 'node:fs/promises';
import {join} from 'node:path';
import {tmpdir} from 'node:os';
import {validateTeachingReadiness,enforceTeachingReadiness} from '../plugins/inside-explain/skills/explain-visually/scripts/teaching-readiness.mjs';

const script='scenes: []\n';
const review=()=>({schema_version:1,episode:'ep01',script_sha256:createHash('sha256').update(script).digest('hex'),
  review_kind:'fresh_automated_reader',reviewer_id:'test-independent-reader',causal_teachback:'pass',novel_transfer:'pass',findings:[]});

test('automated comprehension evidence never implies human acceptance',()=>{
  assert.deepEqual(validateTeachingReadiness(review(),script),{automated_core:'passed',human_acceptance:false});
});
test('lost or wrong core findings remain blocking after kept disposition or repeated rounds',()=>{
  for(const kind of ['lost','wrong'])for(const status of ['open','kept']){
    assert.throws(()=>validateTeachingReadiness({...review(),rounds:99,findings:[{kind,scope:'core',status}]},script),/Unresolved core confusion/);
  }
});
test('script changes and failed transfer prevent spending, even with no recorded findings',()=>{
  assert.throws(()=>validateTeachingReadiness(review(),script+'# changed'),/stale/);
  assert.throws(()=>validateTeachingReadiness({...review(),novel_transfer:'fail'},script),/novel transfer/);
  assert.throws(()=>validateTeachingReadiness({...review(),causal_teachback:'not_run'},script),/teach-back/);
  assert.throws(()=>validateTeachingReadiness({...review(),review_kind:'author_self_review'},script),/fresh-reader/);
  assert.throws(()=>validateTeachingReadiness({...review(),findings:[{kind:'lost',status:'open'}]},script),/valid kind, scope/);
});
test('file gate binds the episode, supports default-series discovery and rejects traversal',async t=>{
  const root=await mkdtemp(join(tmpdir(),'inside-teaching-'));t.after(()=>rm(root,{recursive:true,force:true}));
  const series=join(root,'video'),episode=join(series,'production/episodes/ep01');
  await mkdir(episode,{recursive:true});await mkdir(join(root,'review'));
  await writeFile(join(root,'explanation.json'),JSON.stringify({teaching_gate:'review/core.json'}));
  await writeFile(join(series,'production/plan.yaml'),'title: test');
  await writeFile(join(episode,'script.yaml'),script);
  await assert.rejects(enforceTeachingReadiness(['narrate','ep01','--series',series]),/ENOENT/);
  await writeFile(join(root,'review/core.json'),JSON.stringify(review()));
  assert.equal((await enforceTeachingReadiness(['narrate','ep01','--series',series])).automated_core,'passed');
  assert.equal((await enforceTeachingReadiness(['narrate','ep01',`--series=${series}`])).automated_core,'passed');
  await assert.rejects(enforceTeachingReadiness(['narrate','ep01','--series',series,`--series=${series}`]),/one series/);
  assert.equal((await enforceTeachingReadiness(['deliver','ep01'],episode)).human_acceptance,false);
  await assert.rejects(enforceTeachingReadiness(['narrate','ep02','--series',series]),/different episode/);
  await writeFile(join(root,'explanation.json'),JSON.stringify({teaching_gate:'../not-owned.json'}));
  await assert.rejects(enforceTeachingReadiness(['narrate','ep01','--series',series]),/escapes/);
  assert.equal(await enforceTeachingReadiness(['preview','ep01','--series',series]),null);
  assert.equal(await enforceTeachingReadiness(['narrate','--help','--series',series]),null);
});
