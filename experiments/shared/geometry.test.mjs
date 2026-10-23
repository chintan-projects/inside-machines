import test from 'node:test';
import assert from 'node:assert/strict';
import {pointAt} from './geometry.ts';
test('instruction/data copies follow their bends instead of cutting through the drawing',()=>{
  const points=[[0,0],[10,0],[10,30]];
  assert.deepEqual(pointAt(points,.25),[10,0]);
  assert.deepEqual(pointAt(points,.5),[10,10]);
  assert.deepEqual(pointAt(points,-1),[0,0]);assert.deepEqual(pointAt(points,2),[10,30]);
  assert.deepEqual(pointAt([[2,3],[2,3]],.5),[2,3]);
  assert.throws(()=>pointAt(points,NaN));assert.throws(()=>pointAt([],0));
});
