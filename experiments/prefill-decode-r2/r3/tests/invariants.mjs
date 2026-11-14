import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runRequest} from '../lesson/mechanism.js';
import {CACHED,REBUILT} from '../lesson/states.js';
import {createJourney,resolveHelp} from '../lesson/recovery.js';

test('cache preparation comes from layer inputs and differs from completed outputs',()=>{
  const first=CACHED.passes[0];
  assert.deepEqual(first.cacheByLayer[0][0],{key:[1,.5],value:[.8,0]});
  assert.notDeepEqual(first.cacheByLayer[0][0].value,first.traces[0].layers[0].output);
  assert.deepEqual(first.traces[0].layers[1].input,first.traces[0].layers[0].output);
  assert.deepEqual(first.cacheByLayer[0],CACHED.passes[1].cacheByLayer[0].slice(0,3));
  assert.equal(first.cacheByLayer[0].length,3);
});
test('cached and rebuilt calculations, selections and every layer input agree over changed cases',()=>{
  for(let length=1;length<=8;length+=1)for(let offset=0;offset<5;offset+=1){
    const prompt=Array.from({length},(_,i)=>['The','sky','is','blue','and'][(i+offset)%5]);
    const kept=runRequest({prompt,cache:true,answerTokens:4}),empty=runRequest({prompt,cache:false,answerTokens:4});
    assert.deepEqual(kept.picks,empty.picks);
    for(let pass=0;pass<4;pass+=1){
      assert.deepEqual(kept.passes[pass].trace,empty.passes[pass].trace);
      assert.deepEqual(kept.passes[pass].cacheByLayer,empty.passes[pass].cacheByLayer);
    }
  }
  assert.deepEqual(CACHED.picks,['blue','and']);
  for(const pass of CACHED.passes)for(const item of pass.scores.list)assert.equal(item.score,item.products.reduce((sum,value)=>sum+value,0));
  assert.equal(CACHED.passes[1].positions.length,1);assert.equal(REBUILT.passes[1].positions.length,4);
});
test('layer reading, residual and local adjustment each contribute to the computed output',()=>{
  for(const pass of CACHED.passes)for(const layer of pass.trace.layers){
    for(let coordinate=0;coordinate<2;coordinate+=1){
      assert.equal(layer.mixed[coordinate],layer.input[coordinate]+layer.attention.output[coordinate]);
      assert.equal(layer.output[coordinate],layer.mixed[coordinate]+layer.feedForward.delta[coordinate]);
    }
    assert.ok(Math.abs(layer.attention.weights.reduce((a,b)=>a+b,0)-1)<1e-12);
  }
});
test('recovery follows current topic metadata, clarifies ambiguous questions and preserves experiments',()=>{
  for(const fixture of [
    {frames:['tasks','choice'],concept:'slot_dependency',id:'slot',word:'score'},
    {frames:['room_heat','outside'],concept:'heat_transfer',id:'heat',word:'refrigerant'},
  ]){
    const journey=createJourney(fixture.frames);journey.move(fixture.frames[1],2);journey.compare(false);
    const repairs=[{id:fixture.id,concept:fixture.concept}],aliases={[fixture.id]:[fixture.word]};
    assert.equal(resolveHelp({text:"I'm lost",concept:fixture.concept,repairs,aliases}).id,fixture.id);
    assert.equal(resolveHelp({text:fixture.word,concept:'other',repairs,aliases}).reason,'named_concept');
    assert.equal(resolveHelp({text:'dive deeper',concept:fixture.concept,repairs,aliases}).kind,'clarify');
    assert.equal(resolveHelp({text:'unrelated question',concept:fixture.concept,repairs,aliases}).kind,'clarify');
    journey.help(fixture.id);journey.back();assert.deepEqual(journey.state(),{frame:fixture.frames[1],beat:2,cache:false,repair:null});
    journey.reset();assert.deepEqual(journey.state(),{frame:fixture.frames[0],beat:0,cache:true,repair:null});
  }
});
test('story keeps dependency prerequisites and gives the replay a prediction before counts',()=>{
  const lesson=JSON.parse(readFileSync(new URL('../lesson/teaching.json',import.meta.url)));
  const ids=lesson.core.flatMap(frame=>frame.beats.map(b=>b.id));
  assert.ok(ids.indexOf('core_preparation')<ids.indexOf('core_reuse'));
  assert.ok(ids.indexOf('core_valid')<ids.indexOf('core_reuse'));
  assert.equal(lesson.core.at(-1).beats[0].id,'replay_predict');
  assert.ok(lesson.core.at(-1).beats[0].pause>=3);
});
