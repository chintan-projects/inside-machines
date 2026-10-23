import test from 'node:test';
import assert from 'node:assert/strict';
import {A,B,INPUT,coreStateAt,feedStateAt,matrixStateAt,multiply} from './depth-model.ts';
import {coreNarration,memoryNarration,matrixNarration} from './depth-narration.ts';
import {validateNarration} from '../visual-studio/narration.ts';

test('complete pixel flow stores only computed results and a changed instruction changes the same inputs',()=>{
  assert.ok(coreStateAt(45,{}).results.every(n=>n===null));
  assert.deepEqual(coreStateAt(54,{}).results,[1,2,3,4,null,null,null,null]);
  assert.deepEqual(coreStateAt(62,{}).results,[1,2,3,4,5,6,7,8]);
  assert.deepEqual(coreStateAt(62,{add:'2'}).results,[2,3,4,5,6,7,8,9]);
  assert.deepEqual(INPUT,[0,1,2,3,4,5,6,7]);
  assert.deepEqual(coreStateAt(58,{}),coreStateAt(58,{}));
  assert.equal(coreStateAt(Number.NaN,{}).time,0);
});
test('data-supply experiments preserve four available slots and cannot compute an absent input',()=>{
  for(const supply of [1,4]) for(let round=0;round<=8/supply;round++) {
    const p=feedStateAt(10+round*1.5,{supply:String(supply)});
    assert.equal(p.rounds,8/supply);
    assert.equal(p.results.filter(n=>n!==null).length,Math.min(8,round*supply));
    assert.ok(p.working.length<=supply&&p.working.length<=4);
    for(const job of p.working) {assert.ok(job<p.arrived);assert.equal(p.results[job],null);}
  }
  assert.equal(feedStateAt(0,{}).arrived,0);
  assert.deepEqual(feedStateAt(22,{supply:'1'}).results,feedStateAt(13,{supply:'4'}).results);
});
test('matrix outputs follow row-column products and one changed B column affects only that output column',()=>{
  assert.deepEqual(A.flat(),coreStateAt(62,{add:'1'}).results.slice(0,4));
  assert.deepEqual(multiply(A,B),[[4,4],[10,8]]);
  assert.deepEqual(multiply(A,[[2,1],[1,2]]),[[4,5],[10,11]]);
  for(const weight of ['original','changed']) for(let cell=0;cell<4;cell++) {
    const s=matrixStateAt(50,{cell:String(cell),weight});
    assert.equal(s.sum,s.result[Math.floor(cell/2)][cell%2]);
  }
  assert.throws(()=>multiply([[NaN,2],[3,4]],B));
  assert.equal(matrixStateAt(1e6,{}).time,76);
  assert.equal(matrixStateAt(-1,{}).time,0);
});
test('each narration cue has a valid reduced-motion pose in the same semantic phase',()=>{
  for(const [plan,state,key] of [[coreNarration,coreStateAt,'phase'],[memoryNarration,feedStateAt,'supply'],[matrixNarration,matrixStateAt,'step']]) {
    validateNarration(plan);
    for(const cue of plan.cues) {
      const expected=state(cue.start,{cell:'0'})[key];
      assert.equal(expected,state(cue.still,{cell:'0'})[key]);
      assert.equal(expected,state(cue.end-.001,{cell:'0'})[key]);
    }
  }
});
