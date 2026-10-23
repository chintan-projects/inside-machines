import test from 'node:test';
import assert from 'node:assert/strict';
import {build} from 'esbuild';

const bundle=await build({entryPoints:['native/gpu-memory-r1.ts'],bundle:true,write:false,
  platform:'node',format:'esm',logLevel:'silent'});
const {createGpuMemoryR1Definition}=await import('data:text/javascript;base64,'+
  Buffer.from(bundle.outputFiles[0].text).toString('base64'));

test('native GPU export updates only progress elements present in the supplied working state',()=>{
  const {lesson,metadata}=createGpuMemoryR1Definition();
  let working=0,idle=0;
  for(const supply of ['auto','1','4'])for(let frame=0;frame<lesson.duration*24;frame++){
    const state=lesson.stateAt(frame/24,{supply}),scene=lesson.render(state);
    assert.doesNotMatch(scene.svg,/data-studio-progress\s/);
    const widths=(scene.attributes??[]).filter(update=>
      update.selector==='[data-studio-progress]'&&update.name==='width');
    if(state.working.length){
      working++;assert.equal(widths.length,1);assert.match(scene.svg,/data-studio-progress/);
    }else{
      idle++;assert.equal(widths.length,0);assert.doesNotMatch(scene.svg,/data-studio-progress/);
    }
  }
  assert.ok(working>0&&idle>0);
  assert.equal(metadata.default_controls.supply,'auto');
  assert.equal(lesson.stateAt(14.5,{supply:'1'}).working.length,1);
  assert.equal(lesson.stateAt(14.5,{supply:'4'}).working.length,0);
});
