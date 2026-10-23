import test from 'node:test';
import assert from 'node:assert/strict';
import {bagWindow, bagWindowAlpha} from './bag-window.mjs';

const pose = {time:28,phase:.4,focus:'bag',flow:true,blocked:false};

test('causal window belongs to its storyboard beat and has deterministic seeking',()=>{
  assert.equal(bagWindow({...pose,time:14,focus:'air'}),'');
  assert.equal(bagWindowAlpha({...pose,time:24}),0);
  assert.equal(bagWindowAlpha({...pose,time:34}),0);
  const first=bagWindow(pose);
  bagWindow({...pose,time:30,phase:.9});
  assert.equal(bagWindow(pose),first);
  assert.match(first,/data-bag-inset/);
});

test('blocked flow stops all incoming markers and preserves the retained sample',()=>{
  const open=bagWindow(pose);
  const blocked=bagWindow({...pose,flow:false,blocked:true});
  assert.match(open,/data-air/);
  assert.match(open,/data-incoming/);
  assert.doesNotMatch(blocked,/data-air|data-incoming/);
  const retained=(html)=>html.match(/<rect data-retained[^>]+>/g);
  assert.deepEqual(retained(open),retained(blocked));
  assert.equal(bagWindow({...pose,flow:false,blocked:true,phase:.9}),blocked);
});

test('renderer consumes authoritative flow and fails on nonfinite active phase',()=>{
  assert.doesNotMatch(bagWindow({...pose,flow:false}),/data-air/);
  assert.throws(()=>bagWindow({...pose,phase:NaN}),RangeError);
  assert.equal(bagWindow({...pose,time:NaN}),'');
});
