import test from 'node:test';
import assert from 'node:assert/strict';
import {stateAt,pointAt,duration,story} from '../../.vercel/vacuum-lab/model.mjs';

test('an airtight blockage stops throughflow markers while the powered fan keeps turning',()=>{
  for(const time of [0,0.5,4,11.99]){
    const blocked=stateAt(time,true),open=stateAt(time,false);
    assert.deepEqual(blocked.air,[]);assert.deepEqual(blocked.dirt,[]);
    assert.equal(blocked.angle,open.angle);
    assert.ok(open.air.length>0&&open.dirt.length>0);
  }
  assert.ok(stateAt(4,true).angle>stateAt(1,true).angle);
});
test('chapter seeking changes attention without turning the physical jobs on in sequence',()=>{
  for(const [time,beat] of [[0,0],[11.99,0],[12,1],[22.99,1],[23,2],[33.99,2],[34,3],[43.99,3]]){
    const state=stateAt(time);
    assert.equal(state.beat,beat);
    assert.equal(state.air.length,12);assert.equal(state.dirt.length,5);
    assert.ok(state.air.every(v=>v>=0&&v<1));assert.ok(state.dirt.every(v=>v>=0&&v<1));
  }
  assert.equal(duration,44);assert.equal(story.beats.at(-1).start+story.beats.at(-1).duration,duration);
});
test('seek is deterministic and unknown time fails rather than inventing a scene',()=>{
  const first=stateAt(28.25);stateAt(4,true);stateAt(42);
  assert.deepEqual(stateAt(28.25),first);
  for(const bad of [-1,NaN,Infinity])assert.throws(()=>stateAt(bad));
});
test('material placement follows connected segments, including unequal lengths and clamping',()=>{
  const route=[[0,0],[100,0],[100,300]];
  assert.deepEqual(pointAt(route,0),[0,0]);assert.deepEqual(pointAt(route,.5),[100,100]);
  assert.deepEqual(pointAt(route,1),[100,300]);assert.deepEqual(pointAt(route,2),[100,300]);
  assert.deepEqual(pointAt([[0,0],[0,0],[4,0]],.5),[2,0]);
  assert.throws(()=>pointAt([[0,0]],.5));assert.throws(()=>pointAt(route,NaN));
});
