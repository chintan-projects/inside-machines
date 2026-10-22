import test from 'node:test';
import assert from 'node:assert/strict';
import { chapterIndex, chapterStarts, componentIds, lessonDuration } from '../web/studio/native-contracts.ts';
import { checkedBundle, coreBundle } from '../web/studio/learning-bundle.ts';
import { discussionCheckpoint } from '../web/studio/discussion-checkpoint.ts';
import { prepareSavedPath } from '../web/offline.ts';
import { createHash } from 'node:crypto';

const spec={version:3,spec_version:'native-studio-1',title:'A native mechanism',question:'Where does the energy go?',
  summary:'Trace the energy through the mechanism.',components:[{id:'coil'},{id:'motor'}],
  teaching:{goal:'Follow the energy across the system boundary.'},
  stages:[{id:'orientation',duration:10,focus:'coil',parts:['coil']},
    {id:'working',duration:14,focus:'motor',parts:['motor','coil']}]};
const record={id:'native-r2',spec,quality:'authored-native',review_needed:true,video_ready:true,feedback:null,
  spec_sha256:'1'.repeat(64),video_sha256:createHash('sha256').update('native-media').digest('hex')};

test('native chapters and saved progress use semantic components without manufacturing primitive geometry',()=>{
  assert.deepEqual(componentIds(spec),['coil','motor']);assert.equal(lessonDuration(spec),24);
  assert.deepEqual(chapterStarts(spec),[0,10]);
  assert.equal(chapterIndex(spec,9.99),0);assert.equal(chapterIndex(spec,10),1);
  assert.equal(chapterIndex(spec,24),1);assert.equal(chapterIndex(spec,NaN),0);
  assert.equal(discussionCheckpoint(spec,{stage:null,part:'motor'}),1);
  assert.equal(discussionCheckpoint(spec,{stage:100,part:'unrelated'}),undefined);
  assert.equal('parts' in spec,false);assert.equal('graphics' in spec,false);
});
test('a native core can be saved through the same graph and verified media path',async()=>{
  const bundle=coreBundle(record);bundle.bundle_sha256='a'.repeat(64);
  assert.equal(checkedBundle(bundle,record.id,true).lessons[0].spec.version,3);
  const prepared=await prepareSavedPath('member',bundle,record.id,async url=>new Response(
    url.endsWith('/video')?'native-media':'WEBVTT\n'));
  assert.equal(prepared.length,1);assert.equal(prepared[0].lesson.spec.renderer,undefined);
  await assert.rejects(prepareSavedPath('member',bundle,record.id,async()=>new Response('different')),/does not match/);
  const incomplete=structuredClone(bundle);incomplete.lessons[0].spec.components=[];
  assert.throws(()=>checkedBundle(incomplete,record.id),/teaching data/);
});
