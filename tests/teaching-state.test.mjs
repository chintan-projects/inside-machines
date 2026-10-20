import { test } from 'node:test';
import assert from 'node:assert/strict';
import { teachingAt, scenarioFor, sampledPose } from '../web/teaching/state.ts';

const pose={x:0,y:0,sx:1,sy:1,angle:0,fill:'#000000',opacity:1};
test('piecewise motion follows a pipe bend rather than cutting through its wall',()=>{
  const change={target:'water',before:pose,via:[{...pose,x:0,y:100}],after:{...pose,x:100,y:100,fill:'#ffffff'}};
  assert.deepEqual([sampledPose(change,.5).x,sampledPose(change,.5).y],[0,100]);
  assert.deepEqual([sampledPose(change,.75).x,sampledPose(change,.75).y],[50,100]);
  assert.equal(sampledPose(change,.75).fill,'#808080');
  assert.equal(sampledPose(change,2).x,100);
  assert.throws(()=>sampledPose(change,NaN));
});
test('seek boundaries preserve stable beat identities and reject cross-beat scenarios',()=>{
  const spec={stages:[{duration:10},{duration:20}],teaching:{beats:[{id:'first'},{id:'last'}],scenarios:[{id:'inside',beat:'last'}]}};
  assert.equal(teachingAt(spec,-1)[0].id,'first');
  assert.equal(teachingAt(spec,10)[0].id,'last');
  assert.equal(teachingAt(spec,999)[1],1);
  assert.equal(scenarioFor(spec,spec.teaching.beats[0]),undefined);
  assert.throws(()=>scenarioFor(spec,spec.teaching.beats[0],'inside'));
  assert.throws(()=>teachingAt(spec,Infinity));
});

test('empty fill uses the original graphic color before revealing a new state', () => {
  const before={x:0,y:0,sx:1,sy:1,angle:0,fill:'',opacity:1};
  const change={target:'sample',before,after:{...before,fill:'#ffffff'},via:[]};
  assert.equal(sampledPose(change,0,'#000000').fill,'#000000');
  assert.equal(sampledPose(change,.5,'#000000').fill,'#808080');
  assert.equal(sampledPose({...change,before:change.after,after:before},1,'#000000').fill,'#000000');
});
