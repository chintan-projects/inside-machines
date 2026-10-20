import test from 'node:test';
import assert from 'node:assert/strict';
import {schedule, stateAt} from './model.ts';

test('equal independent jobs complete in two or eight ideal rounds, with the same answers', () => {
  for (const lanes of [1,4]) {
    const rounds=8/lanes;
    const before=schedule('independent',lanes,true,rounds-.1);
    assert.equal(before.jobs.filter(j=>j.status==='done').length,8-lanes);
    const end=schedule('independent',lanes,true,rounds);
    assert.equal(end.totalRounds,rounds);
    assert.deepEqual(end.jobs.map(j=>j.output),[1,2,3,4,5,6,7,8]);
  }
});
test('concurrent readiness is computed from previous-round results, never same-round writes', () => {
  for(const lanes of [1,4]) for(let round=0;round<8;round++) {
    const p=schedule('chain',lanes,true,round+.5);
    assert.equal(p.jobs.filter(j=>j.status==='running').length,1);
    assert.equal(p.jobs[round].id,'ABCDEFGH'[round]);
    assert.equal(p.jobs[round].input,round);
    p.jobs.slice(round+1).forEach(j=>{assert.equal(j.input,null);assert.equal(j.status,'waiting');});
    assert.equal(p.totalRounds,8);
  }
});
test('holding data cannot fabricate work, results or elapsed teaching rounds',()=>{
  for(const mode of ['chain','independent']) for(const t of [0,1,8,100]) {
    const p=schedule(mode,4,false,t);
    assert.equal(p.round,0);assert.equal(p.progress,0);
    assert.ok(p.jobs.every(j=>j.input===null&&j.output===null&&j.status==='waiting'));
    assert.ok(p.lanes.every(l=>l.jobId===null));
  }
});
test('seeking, changed controls and out-of-range inputs are deterministic',()=>{
  const c={work:'chain',lanes:'4',data:'ready'};
  const first=stateAt(24,c); stateAt(40,c); stateAt(8,{work:'independent'});
  assert.deepEqual(stateAt(24,c),first);
  assert.equal(stateAt(Number.NaN,c).time,0);
  assert.equal(stateAt(-7,c).time,0);assert.equal(stateAt(100,c).time,42);
  assert.equal(stateAt(20,{lanes:'1',work:'independent'}).laneCount,1);
  assert.throws(()=>schedule('unsupported',4,true,0));
});
