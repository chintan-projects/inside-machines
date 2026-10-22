import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {refrigeratorR2Definitions,createRefrigeratorR2Lessons,refrigeratorR2Path} from './index.ts';
import {refrigeratorRoutes} from './artwork.ts';
import {mechanismPoints,cycleStateAt} from './model.ts';
import {refrigeratorCore} from '../narration.ts';
import {parsePath} from '../../../web/studio/path-contract.ts';

const definitions=refrigeratorR2Definitions();
const frames=definitions.flatMap(({lesson,spec})=>spec.stages.flatMap(cue=>{
  const times=[cue.start+.01,cue.still,Math.min(cue.end-.01,cue.start+(cue.end-cue.start)*.8)];
  return [...new Set(times)].map(time=>{
    const state=lesson.stateAt(time,lesson.defaultControls);
    return {...lesson.render(state),cue_id:state.beatId,time:state.time,scenario_id:'',controls:lesson.defaultControls};
  });
}));
const controlFrames=definitions.flatMap(({lesson,spec})=>lesson.controls.flatMap(control=>
  control.options.flatMap(option=>spec.stages.map(cue=>{
    const controls={...lesson.defaultControls,[control.key]:option.value};
    const state=lesson.stateAt(cue.still,controls);
    return {canonical:spec.canonical,case_id:control.key+'-'+option.value,
      frame:{...lesson.render(state),cue_id:state.beatId,time:state.time,scenario_id:'',controls}};
  }))));

test('new immutable node IDs share one valid depth path and keep actual cue identities',()=>{
  assert.equal(definitions.length,3);
  parsePath(refrigeratorR2Path,definitions.map(({lesson})=>lesson.id));
  for(const {lesson,spec} of definitions) {
    assert.equal(spec.canonical,lesson.id);
    assert.ok(lesson.id.startsWith('refrigerator-r2-'));
    assert.equal(spec.stages.at(-1).end,lesson.duration);
    for(const cue of spec.stages) {
      assert.equal(lesson.stateAt(cue.still,lesson.defaultControls).beatId,cue.id);
      assert.equal(cue.narration,cue.explanation);
    }
  }
});

test('native source is usable without inventing an audio URL and rejects a mismatched script',()=>{
  assert.ok(createRefrigeratorR2Lessons().every(lesson=>lesson.narration===undefined));
  const narration={...refrigeratorCore,src:'data:audio/mpeg;base64,AA=='};
  assert.equal(createRefrigeratorR2Lessons({[narration.id]:narration})[0].narration,narration);
  assert.throws(()=>createRefrigeratorR2Lessons({[narration.id]:{...narration,duration:1}}),/cue plan/);
});

test('physical routes join their actual adjacent tube endpoints without a missing return',()=>{
  const r=refrigeratorRoutes;
  for(const [from,to] of [[r.coldCoil,r.suction],[r.discharge,r.warmCoil],
    [r.warmCoil,r.liquid],[r.liquid,r.capillary],[r.capillary,r.coldCoil]])assert.deepEqual(from.at(-1),to[0]);
  for(const route of Object.values(r))for(let i=1;i<route.length;i++) {
    assert.ok(Math.hypot(...route[i].map((n,j)=>n-route[i-1][j]))>0,'No duplicate point creates a pinched span');
  }
});

test('the 3D crank projection preserves the existing fixed rod, stop and valve rules',()=>{
  for(let time=34;time<49;time+=.07) {
    const state=cycleStateAt(time,{power:'on'}),{crank,piston}=mechanismPoints(state);
    assert.ok(Math.abs(Math.hypot(...crank.map((n,i)=>n-piston[i]))-150)<1e-8);
    assert.ok(!(state.intakeOpen&&state.outletOpen));
  }
  assert.deepEqual(mechanismPoints(cycleStateAt(35,{power:'off'})),mechanismPoints(cycleStateAt(48,{power:'off'})));
});

test('real control cases change the rendered mechanism, room boundary and pressure outcome',()=>{
  const [{lesson:core},{lesson:energy},{lesson:phase}]=definitions;
  const on=core.render(core.stateAt(36.9,{power:'on'})),off=core.render(core.stateAt(36.9,{power:'off'}));
  assert.notEqual(on.svg,off.svg);assert.match(off.alt,/Stopped/);
  const closed=energy.render(energy.stateAt(30,{door:'closed'})),open=energy.render(energy.stateAt(30,{door:'open'}));
  assert.notEqual(closed.svg,open.svg);assert.match(open.alt,/4 units returned minus 3 removed leaves 1 added/);
  const low=phase.render(phase.stateAt(16,{pressure:'lower'})),high=phase.render(phase.stateAt(16,{pressure:'higher'}));
  assert.match(low.svg,/data-phase-bubbles/);assert.doesNotMatch(high.svg,/data-phase-bubbles/);
  assert.match(high.alt,/Heat can still enter/);
});

test('all actual scenes have bounded labels, exportable palette values and safe update selectors',()=>{
  for(const frame of frames) {
    assert.doesNotMatch(frame.svg,/\b(?:NaN|Infinity)\b|var\(--|<script|<foreignObject/);
    assert.match(frame.svg,/#(?:[0-9a-f]{6})/i);
    for(const label of frame.labels) {
      assert.ok(label.x>=0&&label.x<=frame.viewport.width);
      assert.ok(label.y>=0&&label.y<=frame.viewport.height);
    }
    for(const update of frame.attributes??[])assert.match(update.selector,/^\[data-[a-z0-9-]+\]$/);
  }
});

test('Python validates native contracts and materializes every causal checkpoint with real geometry change',()=>{
  const python=fileURLToPath(new URL('../../../.venv/bin/python',import.meta.url));
  const script=`import json,sys
from backend.native_contracts import NativeLessonSpec
from backend.native_render import RawFrame,materialize
from backend.native_proof import inspect_svg
data=json.load(sys.stdin)
for spec in data['specs']:
    spec['renderer']['fingerprint']='0'*64
    NativeLessonSpec.model_validate(spec)
frames=[materialize(RawFrame.model_validate(f)) for f in data['frames']]
cases=[(c['canonical'],c['case_id'],materialize(RawFrame.model_validate(c['frame']))) for c in data['cases']]
for spec in data['specs']:
    core={c['id']:c['label'] for c in spec['components'] if c['id'] in spec['teaching']['core']}
    own=[f for f in frames if any(c['id']==f.cue_id for c in spec['stages'])]
    assert any(all(any(label.casefold() in text.casefold() for text in inspect_svg(f)[0]) for label in core.values()) for f in own)
    for cue in spec['stages']:
        values=[inspect_svg(f) for f in own if f.cue_id==cue['id']]
        label=next(c['label'] for c in spec['components'] if c['id']==cue['focus'])
        assert all(any(label.casefold() in text.casefold() for text in texts) for texts,_ in values),(spec['canonical'],cue['id'],label,values[0][0])
        if cue['kind']=='causal':assert len({geometry for _,geometry in values})>1,cue['id']
    for case_id in {case for canonical,case,_ in cases if canonical==spec['canonical']}:
        selected=[frame for canonical,case,frame in cases if canonical==spec['canonical'] and case==case_id]
        assert any(all(any(label.casefold() in text.casefold() for text in inspect_svg(f)[0]) for label in core.values()) for f in selected)
        for frame in selected:
            cue=next(c for c in spec['stages'] if c['id']==frame.cue_id)
            label=next(c['label'] for c in spec['components'] if c['id']==cue['focus'])
            assert any(label.casefold() in text.casefold() for text in inspect_svg(frame)[0]),(spec['canonical'],case_id,cue['id'],label)
print(len(frames))`;
  const result=execFileSync(python,[ '-c',script],{cwd:new URL('../../../',import.meta.url),encoding:'utf8',
    input:JSON.stringify({specs:definitions.map(({spec})=>spec),frames,cases:controlFrames}),maxBuffer:2_000_000});
  assert.ok(Number(result.trim())>=50);
});

test('the historical R1 packed artifact is preserved when available locally',async t=>{
  let file;
  try{file=await readFile(new URL('../../../.vercel/visual-studio/public/refrigerator/index.html',import.meta.url));}
  catch(error){if(error.code==='ENOENT'){t.skip('Ignored historical artifact is absent in this checkout');return;}throw error;}
  assert.equal(createHash('sha256').update(file).digest('hex'),'baa8eb1955889a696755c693331bdc82ef9ab0ad552f7d78400212dd810c7a4e');
});
