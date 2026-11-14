import test from 'node:test';
import assert from 'node:assert/strict';
import {loadNarration} from '../lesson/load.mjs';
import {run,KEPT,CLEARED,RULES,INPUTS} from '../lesson/mechanism.mjs';
import {panel,describe} from '../lesson/panels.mjs';
const n=loadNarration();
const beats=n.scenes.flatMap(s=>s.beats),byId=id=>beats.find(b=>b.id===id);
const close=(a,b)=>assert.ok(Math.abs(a-b)<1e-10,`${a} != ${b}`);

test('the fixed toy chooses blue then and; a choice has not yet entered processing',()=>{
 assert.deepEqual(KEPT.picks,['blue','and']);
 assert.deepEqual(KEPT.passes[0].text,['The','sky','is']);
 assert.deepEqual(KEPT.passes[1].text,['The','sky','is','blue']);
 assert.equal(KEPT.passes[0].cache[0].length,3);assert.equal(KEPT.passes[1].cache[0].length,4);
 assert.equal(KEPT.passes[1].text.includes('and'),false);
});
test('cached and reconstructed results, candidate scores and every saved entry agree over changed inputs',()=>{
 const words=Object.keys(INPUTS);
 for(let length=1;length<=9;length++)for(let offset=0;offset<words.length;offset++){
  const tokens=Array.from({length},(_,i)=>words[(i+offset)%words.length]);
  const kept=run({tokens,choices:4}),clear=run({tokens,choices:4,cache:false});
  assert.deepEqual(kept.picks,clear.picks);
  for(let i=0;i<4;i++){
   assert.deepEqual(kept.passes[i].traces.at(-1),clear.passes[i].traces.at(-1));
   assert.deepEqual(kept.passes[i].cache,clear.passes[i].cache);
   assert.deepEqual(kept.passes[i].selection,clear.passes[i].selection);
   if(i){assert.deepEqual(kept.passes[i].preparedPerLayer,[1,1]);assert.deepEqual(clear.passes[i].preparedPerLayer,[length+i,length+i]);}
  }
 }
});
test('per-layer preparation depends on that layer input, not the finished layer result',()=>{
 const the=KEPT.passes[0].traces[0].layers;
 close(the[0].key,.25);close(the[0].value,.8);close(the[0].output,2.7);
 close(the[1].input,the[0].output);close(the[1].key,.675);close(the[1].value,2.16);
 assert.notEqual(the[0].key,the[1].key);
 assert.deepEqual(CLEARED.passes[1].traces.slice(0,3),KEPT.passes[0].traces);
 assert.deepEqual(KEPT.passes[0].cache,KEPT.passes[1].cache.map(layer=>layer.slice(0,3)));
});
test('an earlier edit preserves exactly the guaranteed dependencies, without a blanket prefix reuse claim',()=>{
 const a=run().passes[0],b=run({tokens:['The','and','is']}).passes[0];
 assert.deepEqual(a.traces[0],b.traces[0]);
 close(a.traces[2].layers[0].key,b.traces[2].layers[0].key);close(a.traces[2].layers[0].value,b.traces[2].layers[0].value);
 assert.notEqual(a.traces[2].layers[0].output,b.traces[2].layers[0].output);
 assert.notEqual(a.traces[2].layers[1].key,b.traces[2].layers[1].key);
});
test('reading shares, contribution sums, residual additions and the local update remain coherent',()=>{
 for(const pass of [KEPT,CLEARED].flatMap(r=>r.passes))for(const trace of pass.traces)for(const t of trace.layers){
  assert.ok(t.sources.every(s=>s.position<=t.position));close(t.shares.reduce((a,b)=>a+b,0),1);
  close(t.contributions.reduce((a,b)=>a+b,0),t.blend);close(t.input+t.blend,t.mixed);
  close(t.positive,Math.max(0,t.mixed));close(t.adjustment,RULES.local*t.positive);close(t.output,t.mixed+t.adjustment);
 }
 assert.equal(KEPT.passes[1].traces[0].layers[0].adjustment,0);
});
test('all narrated views have actual computed visible data and unique stable ids',()=>{
 assert.equal(new Set(beats.map(b=>b.id)).size,beats.length);
 for(const b of beats){const p=panel(b);assert.ok(p.subject);assert.ok(p.rows.length||p.workbench||p.operation||p.handoff||p.markers?.length||p.counts?.length||p.lanes?.length||p.block||p.pipeline||p.distribution);assert.ok(describe(p).length>20);}
});
test('operation-card results display the corresponding mechanism result, rounded rather than invented',()=>{
 for(const b of beats){const p=panel(b);if(p.kind!=='operation'||b.view==='stage_handoff_goal')continue;
  const pass=b.pass??0,current=b.position??(pass?3:2),pos=b.view==='prepare'&&b.part!=='query'?(b.source_index??current):current,layer=b.layer??0;
  const trace=KEPT.passes[pass].traces.find(t=>t.position===pos)??KEPT.passes[0].traces.find(t=>t.position===pos);const t=trace.layers[layer];
  const expected=b.view==='prepare'?t[b.part]:b.view==='matches'?t.matches[b.source_index]:b.view==='parts'?(b.part==='clip'?t.positiveMatches[b.source_index]:t.parts[b.source_index]):b.view==='share'?t.shares[b.source_index]:b.view==='contribute'?t.contributions[b.source_index]:b.view==='single_read'?t.blend:b.view==='mix'?t.mixed:b.view==='adjust'?t.adjustment:t.output;
  assert.ok(Math.abs((b.view==='share'?parseFloat(p.operation.right)/100:Number(p.operation.right))-expected)<=.000500001,b.id);
 }
});
test('the basic sharing recipe is explicit and its normalized fractions total one',()=>{
 for(const p of KEPT.passes)for(const trace of p.traces)for(const t of trace.layers){
  close(t.shares.reduce((a,b)=>a+b,0),1);
  for(let i=0;i<t.matches.length;i++){close(t.positiveMatches[i],Math.max(0,t.matches[i]));close(t.parts[i],1+t.positiveMatches[i]);assert.ok(t.parts[i]>=1);close(t.shares[i],t.parts[i]/t.total);}
 }
});
test('new token K/V is prepared at each appropriate layer and never before selection becomes input',()=>{
 assert.deepEqual(panel(byId('cache_name')).counts,[4,4]);
 assert.equal(panel(byId('cache_name')).visibleLayer,0);
 assert.equal(panel(byId('separate_stores')).visibleLayer,null);
 assert.deepEqual(KEPT.passes[1].preparedPerLayer,[1,1]);assert.deepEqual(CLEARED.passes[1].preparedPerLayer,[4,4]);
 assert.notEqual(KEPT.passes[0].selection.candidates[0].weight,INPUTS.blue);
});
test('invalid inputs and unknown renderer views fail rather than fabricating a lesson',()=>{
 assert.throws(()=>run({tokens:['unknown']}),RangeError);assert.throws(()=>run({choices:0}),RangeError);assert.throws(()=>run({cache:'yes'}),RangeError);
 assert.throws(()=>panel({view:'invented'}),/Unsupported view/);
});

test('parallel repeated operations retain EVERY allowed source, including the current position',()=>{
 for(const b of beats.filter(b=>['match_all','parts_all','shares_all','contribute_all'].includes(b.narration_template))){
  const pass=b.pass??0,pos=b.position??(pass?3:2),p=panel(b);
  assert.equal(p.rows.length,pos+1,b.id);
  assert.ok(p.rows.some(r=>r.label===KEPT.passes[pass].text[pos]),b.id+' omits self');
 }
});

test('a retained-fraction reminder never appears before that SAME reading has calculated its fractions',()=>{
 for(const [index,b] of beats.entries())if(panel(b).readingFractions){
  const key=x=>`${x.pass??0}/${x.position??((x.pass??0)?3:2)}/${x.layer??0}`;
  assert.ok(beats.slice(0,index).some(a=>a.view==='shares_all'&&key(a)===key(b)),b.id+' prematurely reveals fractions');
 }
 assert.equal(panel(byId('reading_number')).readingFractions,undefined);
});

test('the persistent first-reading diagram keeps both operands bound to the same current reading',()=>{
 for(const b of beats.filter(b=>b.workbench)){
  const p=panel(b),w=p.workbench,t=KEPT.passes[0].traces[1].layers[0],i=b.workbench.source_index;
  assert.equal(w.reader,'sky');assert.equal(w.source,t.sources[i].word);
  assert.ok(Math.abs(Number(w.query)-t.query)<.00051);assert.ok(Math.abs(Number(w.key)-t.sources[i].key)<.00051);
  assert.ok(Math.abs(Number(w.parts)-t.parts[i])<.00051);
 }
});

test('visible diagram labels anchor query/key names only once their concrete job has been shown',()=>{
 assert.equal(panel(byId('sky_query')).workbench.readerLabel,'prepared number');
 assert.equal(panel(byId('sky_key_the')).workbench.sourceLabel,'prepared number');
 assert.equal(panel(byId('sky_query_name')).workbench.readerLabel,'query');
 assert.equal(panel(byId('sky_key_name')).workbench.sourceLabel,'key');
 assert.ok(describe(panel(byId('sky_query_name'))).includes('query 1.000'));
 assert.ok(describe(panel(byId('sky_key_name'))).includes('key 0.250'));
 assert.ok(!beats.some(b=>b.view==='parts_warmup'));
});

test('the unchanged-source proof does not announce a later key/value conclusion',()=>{
 const p=panel(byId('same_restriction'));
 assert.deepEqual(p.rows.map(r=>r.value),['The','The + sky','The + sky + is']);
 assert.ok(!/keys|values|unchanged preparation/.test(describe(p)));
 assert.throws(()=>panel({view:'unchanged',part:'typo'}),/Unsupported unchanged/);
});
