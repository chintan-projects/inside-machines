import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {parsePath,resolveQuestion} from './path-contract.ts';
const raw=()=>JSON.parse(readFileSync(new URL('../gpu-study/path.json',import.meta.url),'utf8'));
const allowed=['gpu-core-s3','gpu-study-1','gpu-memory-s3','gpu-matrix-s3'];
test('portable path resolves available questions and context-dependent deeper without a model call',()=>{
  const p=parsePath(raw(),allowed);
  assert.equal(resolveQuestion(p,'core','dive deeper').id,'parallel');
  assert.equal(resolveQuestion(p,'parallel','dive deeper').id,'memory');
  assert.equal(resolveQuestion(p,'core','tell me more about memory').id,'memory');
  assert.equal(resolveQuestion(p,'core','explain the model').id,'matrix');
  assert.equal(resolveQuestion(p,'matrix','dive deeper'),undefined);
  assert.equal(resolveQuestion(p,'core','memory and matrices'),undefined);
  assert.equal(resolveQuestion(p,'core','how does a refrigerator work'),undefined);
  assert.equal(resolveQuestion(p,'core','explain the GPT model'),undefined);
  assert.equal(resolveQuestion(p,'core','explain the vacuum cleaner model'),undefined);
});
test('external graphs cannot supply code, unsupported references, cycles or unreachable nodes',()=>{
  const changes=[p=>{p.schema_version='other';},p=>{p.nodes[1].id='core';},
    p=>{p.nodes[0].prerequisites=['matrix'];},p=>{p.nodes[0].next=['absent'];},
    p=>{p.nodes[3].next=['core'];},p=>{p.nodes[0].next=['matrix'];},
    p=>{p.nodes[0].renderer='remote-script';}];
  for(const change of changes){const p=raw();change(p);assert.throws(()=>parsePath(p,allowed));}
  assert.throws(()=>parsePath(raw(),['gpu-core-s3']));
});
test('a physical concept uses the same navigator envelope without GPU-specific fields',()=>{
  const p=raw();p.id='vacuum-fixture';p.title='How does a vacuum work?';
  p.nodes=p.nodes.slice(0,2);p.nodes[0].next=['parallel'];p.nodes[1].next=[];
  p.nodes[0].lesson_id='vacuum-core';p.nodes[1].lesson_id='vacuum-filter';
  p.nodes[1].label='How the filter works';p.nodes[1].question='How can air pass while dirt stays?';
  p.nodes[1].queries=['filter'];
  const checked=parsePath(p,['vacuum-core','vacuum-filter']);
  assert.equal(resolveQuestion(checked,'core','filter').lesson_id,'vacuum-filter');
});
