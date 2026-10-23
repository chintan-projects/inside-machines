import test from 'node:test';
import assert from 'node:assert/strict';
import {compressorPose,cycleStateAt,energyBalance,energyStateAt,phaseStateAt} from './model.ts';
import {refrigeratorNarrations} from './narration.ts';
import {validateNarration} from '../visual-studio/narration.ts';
test('compressor intake enlarges the chamber; compression/discharge shrink it without simultaneous valves',()=>{
  assert.ok(compressorPose(.1,true).piston>compressorPose(.4,true).piston);
  assert.ok(compressorPose(.5,true).piston<compressorPose(.9,true).piston);
  for(let i=0;i<=100;i++){const s=compressorPose(i/100,true);assert.ok(s.piston>=0&&s.piston<=1);assert.ok(!(s.intakeOpen&&s.outletOpen));
    assert.ok(Math.abs(Math.hypot(s.crankX-360,s.crankY-s.pistonPinY)-150)<1e-8);}
  const off=compressorPose(.2,false);assert.equal(off.intakeOpen,false);assert.equal(off.outletOpen,false);
  assert.deepEqual(off,compressorPose(.8,false));
});
test('steady energy accounting conserves energy and does not invent a closed-room net or off-state pumping',()=>{
  for(const open of [false,true])for(const running of [false,true]){
    const b=energyBalance(open,running);assert.equal(b.released,b.removed+b.work);
    assert.equal(b.sameRoomNet,open?b.work:null);
    if(!running)assert.deepEqual(b,{removed:0,work:0,released:0,sameRoomNet:open?0:null});
  }
  assert.equal(energyStateAt(32,{}).open,true);
  assert.equal(energyStateAt(32,{door:'closed'}).open,false);
  assert.equal(energyStateAt(0,{door:'open'}).open,true);
});
test('qualitative pressure comparison never equates no boiling with no heat transfer',()=>{
  assert.equal(phaseStateAt(16,{}).canBoil,true);
  const higher=phaseStateAt(16,{pressure:'higher'});
  assert.equal(higher.canBoil,false);assert.equal(higher.canAbsorbHeat,true);
  assert.equal(phaseStateAt(29,{}).pressure,'higher');
});
test('every cue and arbitrary seek is bounded, deterministic and preserves focus rather than exclusive machine stages',()=>{
  const states=[cycleStateAt,energyStateAt,phaseStateAt];
  refrigeratorNarrations.forEach((plan,i)=>{
    validateNarration(plan);
    for(const cue of plan.cues){
      for(const t of [cue.start,cue.still,cue.end-.001]){
        const a=states[i](t,{});assert.deepEqual(a,states[i](t,{}));assert.equal(a.beatId,plan.id+'-'+cue.start);
      }
    }
    assert.equal(states[i](Infinity,{}).time,0);assert.equal(states[i](-1,{}).time,0);
    assert.equal(states[i](9999,{}).time,plan.duration);
  });
  for(const t of [0,15,27,36,55,69,84,97])assert.equal(cycleStateAt(t,{}).running,true);
  const stopped=cycleStateAt(36,{power:'off'});assert.equal(stopped.running,false);
  assert.equal(stopped.intakeOpen,false);assert.equal(stopped.outletOpen,false);
});
