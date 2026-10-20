import test from 'node:test';
import assert from 'node:assert/strict';
import {NarrationTransport, cueAt, validateNarration} from './narration.ts';
import {gpuNarration} from '../gpu-study/narration.ts';
import {stateAt} from '../gpu-study/model.ts';

class Media extends EventTarget {
  currentTime=0; muted=false; ended=false; paused=true; requests=[];
  play() { return new Promise((resolve,reject)=>this.requests.push({resolve,reject})); }
  pause() { const wasPlaying=!this.paused; this.paused=true; if(wasPlaying)this.dispatchEvent(new Event('pause')); }
  start(i=0) { this.paused=false; this.dispatchEvent(new Event('playing')); this.requests[i].resolve(); }
}
const setup=()=>{const media=new Media();return {media,transport:new NarrationTransport(media,42,()=>{})};};

test('delayed play cannot resume audio after pause, reset or leaving the narrated scenario',async()=>{
  for(const operation of ['pause','reset']) {
    const {media,transport}=setup(); media.currentTime=22;
    const pending=transport.play(); transport[operation]();
    media.start(); await pending;
    assert.equal(media.paused,true); assert.notEqual(transport.status,'playing');
    if(operation==='reset')assert.equal(transport.time,0);
  }
});
test('an old rejected play cannot erase a newer successful playback',async()=>{
  const {media,transport}=setup(); const old=transport.play(); transport.pause();
  const current=transport.play(); media.start(1); await current;
  media.requests[0].reject(new Error('Aborted old request')); await old;
  assert.equal(transport.status,'playing'); assert.equal(media.paused,false);
});
test('a queued native pause event cannot cancel a newer play intent',async()=>{
  const {media,transport}=setup(); const first=transport.play(); media.start(); await first;
  transport.pause(); const next=transport.play(); media.start(1); await next;
  media.dispatchEvent(new Event('pause'));
  assert.equal(transport.status,'playing'); assert.equal(media.paused,false);
  media.pause(); assert.equal(transport.status,'paused');
});
test('blocked/unsupported playback and decode failure stay visible; resume is deliberate',async()=>{
  const {media,transport}=setup(); const blocked=transport.play();
  media.requests[0].reject(new Error('NotAllowedError')); await blocked;
  assert.equal(transport.status,'error'); assert.equal(media.paused,true);
  const retry=transport.play(); media.start(1); await retry;
  media.dispatchEvent(new Event('waiting')); assert.equal(transport.status,'waiting');
  media.dispatchEvent(new Event('playing')); assert.equal(transport.status,'playing');
  media.dispatchEvent(new Event('error')); assert.equal(transport.status,'error'); assert.equal(media.paused,true);
});
test('seek pauses, clamps the media clock, and mute does not move time',async()=>{
  const {media,transport}=setup(); const pending=transport.play(); media.start(); await pending;
  media.currentTime=22.5; assert.equal(transport.time,22.5);
  transport.seek(31); assert.equal(transport.time,31); assert.equal(media.paused,true);
  transport.toggleMute(); assert.equal(media.muted,true); assert.equal(transport.time,31);
  transport.seek(100); assert.equal(transport.time,42); assert.equal(transport.status,'ended');
  transport.seek(Number.NaN); assert.equal(transport.time,0);
  transport.seek(-3); assert.equal(transport.time,0);
});
test('natural completion stops at the story duration and reset is reusable',async()=>{
  const {media,transport}=setup(); const pending=transport.play(); media.start(); await pending;
  media.currentTime=42; media.dispatchEvent(new Event('timeupdate'));
  assert.equal(transport.status,'ended'); assert.equal(media.paused,true);
  transport.reset(); assert.equal(transport.time,0); assert.equal(transport.status,'idle');
});
test('GPU captions and reduced-motion poses cover the same authored causal beats',()=>{
  validateNarration(gpuNarration);
  const controls={lanes:'4',work:'auto',data:'ready'};
  assert.equal(cueAt(gpuNarration,6).start,6); assert.equal(cueAt(gpuNarration,20).start,20);
  assert.equal(cueAt(gpuNarration,42).start,36);
  for(const cue of gpuNarration.cues) {
    assert.equal(stateAt(cue.still,controls).beatId,stateAt(cue.start,controls).beatId);
  }
  assert.equal(stateAt(cueAt(gpuNarration,7).still,controls).lanes.filter(l=>l.jobId).length,4);
  assert.equal(stateAt(cueAt(gpuNarration,23).still,controls).lanes.filter(l=>l.jobId).length,1);
  const cues=gpuNarration.cues.map(c=>({...c})); cues[1].start=6.1;
  assert.throws(()=>validateNarration({...gpuNarration,cues}));
  assert.throws(()=>validateNarration({...gpuNarration,duration:43}));
});
