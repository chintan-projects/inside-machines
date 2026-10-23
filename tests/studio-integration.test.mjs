import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { prepareSavedPath } from '../web/offline.ts';
import { checkedBundle, coreBundle, matchesSavedBundle } from '../web/studio/learning-bundle.ts';
import { verifyVideo } from '../web/studio/artifact-integrity.ts';
import { mountPath } from '../web/studio/path-player.ts';
import { NarrationTransport } from '../web/studio/narration.ts';
import { discussionCheckpoint } from '../web/studio/discussion-checkpoint.ts';
import { progressWriter } from '../web/studio/progress-writer.ts';

const lesson = id => ({id, spec: {version:2, title:`${id} explanation`, summary:'A complete explanation of a working system.',
  question:'How does the system work?', teaching:{goal:'Trace an input through its useful output.'}, graphics:[{id:'working-section'}]},
  video_ready:true, spec_sha256:'1'.repeat(64), video_sha256:createHash('sha256').update('video-bytes').digest('hex'),
  feedback:{value:'up',reason:'private feedback'}});
const bundle = () => ({bundle_sha256:'a'.repeat(64),path:{schema_version:'learning-path-1',id:'system-path',title:'How the system works',
  example:'A trusted core and a deeper explanation.',entry:'overview',nodes:[
    {id:'overview',role:'core',label:'The complete picture',question:'How does the system work?',outcome:'Trace the input through the useful output.',
      lesson_id:'system-core',prerequisites:[],next:['detail'],queries:['system']},
    {id:'detail',role:'insight',label:'See the mechanism',question:'Why does this mechanism change the output?',outcome:'Explain how this working mechanism changes the output.',
      lesson_id:'system-detail',prerequisites:['overview'],next:[],queries:['mechanism']},
  ]},lessons:[lesson('system-core'),lesson('system-detail')]});

test('offline preparation includes every exact path revision and strips member feedback', async () => {
  const requests=[];
  const download=async url=>{requests.push(url);return new Response(url.endsWith('/video')?'video-bytes':'WEBVTT\n', {status:200});};
  const prepared=await prepareSavedPath('member-a',bundle(),'system-core',download);
  assert.equal(requests.length,4);
  assert.deepEqual(prepared.map(record=>record.lesson.id),['system-core','system-detail']);
  assert(prepared.every(record=>record.user==='member-a'&&record.key.startsWith('member-a:')&&record.lesson.feedback===null));
  assert(prepared.every(record=>record.video instanceof Blob&&record.captions==='WEBVTT\n'));
  assert.equal(prepared[0].learningPath.entry,'overview');
  assert.equal(prepared[0].bundleSha256,'a'.repeat(64));
  assert.equal(prepared[0].lesson.video_sha256,bundle().lessons[0].video_sha256);
  assert.equal(prepared[0].pathChild,false);assert.equal(prepared[1].pathChild,true);
});
test('a missing child or failed media prevents a partial offline save', async () => {
  const missing=bundle();missing.lessons.pop();
  await assert.rejects(prepareSavedPath('member',missing,'system-core',async()=>new Response('ok')));
  await assert.rejects(prepareSavedPath('member',bundle(),'system-core',async url=>new Response('no',{status:url.includes('detail')?503:200})),/Nothing new was saved/);
  const wrong=bundle();wrong.lessons[0].id='other-revision';
  assert.throws(()=>checkedBundle(wrong,'system-core'));
});
test('a complete core is a valid path without fabricated optional depth', () => {
  const core=lesson('system-core');
  const path=coreBundle(core);
  assert.equal(path.path.nodes.length,1);assert.deepEqual(path.path.nodes[0].next,[]);
  assert.equal(path.path.nodes[0].lesson_id,core.id);
});
test('a changed graph or node artifact invalidates saved status without changing the earlier offline copy', async () => {
  const previous=bundle(),original=structuredClone(previous),current=bundle();
  assert.equal(matchesSavedBundle(previous,current),true);
  current.bundle_sha256='b'.repeat(64);current.path.nodes[1].label='A clearer deeper question';
  assert.equal(matchesSavedBundle(previous,current),false);
  await assert.rejects(prepareSavedPath('member',current,'system-core',async url=>new Response('video-bytes',{status:url.includes('detail')?503:200})));
  assert.deepEqual(previous,original);
  const changedArtifact=bundle();changedArtifact.lessons[1].video_sha256='2'.repeat(64);
  assert.equal(matchesSavedBundle(previous,changedArtifact),false);
  const changedGraph=bundle();changedGraph.path.nodes[1].question='How does the changed deeper mechanism work?';
  assert.equal(matchesSavedBundle(previous,changedGraph),false);
});
test('a legacy offline graph stays readable but cannot stand in for the current bound graph', () => {
  const legacy=bundle();legacy.bundle_sha256='';
  legacy.lessons.forEach(item=>{delete item.spec_sha256;delete item.video_sha256;});
  assert.equal(checkedBundle(legacy,'system-core').path.nodes.length,2);
  assert.equal(matchesSavedBundle(legacy,bundle()),false);
  assert.throws(()=>checkedBundle(legacy,'system-core',true),/learning-path identity/);
  const standalone=coreBundle(lesson('system-core'));delete standalone.lessons[0].spec_sha256;
  assert.equal(matchesSavedBundle(standalone,coreBundle(lesson('system-core'))),false);
});
test('offline videos are verified against bound SHA256 before they can replace a saved path', async () => {
  const expected=createHash('sha256').update('video-bytes').digest('hex');
  await verifyVideo(new Blob(['video-bytes']),expected);
  await assert.rejects(verifyVideo(new Blob(['other-video']),expected),/does not match/);
  await assert.rejects(verifyVideo(new Blob(['video-bytes']),undefined),/missing its video identity/);
  await assert.rejects(prepareSavedPath('member',bundle(),'system-core',async url=>new Response(url.endsWith('/video')?'wrong-video':'WEBVTT\n')),/does not match/);
});
test('chat show-me links use only valid checkpoints in the active revision', () => {
  const spec={stages:[{focus:'motor',parts:['motor','inlet']},{focus:'filter',parts:['filter','outlet']}]};
  assert.equal(discussionCheckpoint(spec,{stage:null,part:'filter'}),1);
  assert.equal(discussionCheckpoint(spec,{stage:0,part:'filter'}),0);
  assert.equal(discussionCheckpoint(spec,{stage:20,part:'inlet'}),0);
  assert.equal(discussionCheckpoint(spec,{stage:-1,part:'other-revision-part'}),undefined);
});
test('an unchanged paused tab cannot erase another tab’s newer checkpoint, while a deliberate reset is saved', () => {
  const stored=new Map(),write=(id,value)=>stored.set(id,value);
  const idle=progressWriter(write),active=progressWriter(write);
  const progress=seconds=>({seconds,selected:'motor',mode:'explore',speed:1});
  idle.restored('core',0);active.restored('core',0);
  assert.equal(active.save('core',progress(54)),true);
  assert.equal(idle.save('core',progress(0)),false);assert.equal(stored.get('core').seconds,54);
  assert.equal(active.save('core',progress(0)),true);assert.equal(stored.get('core').seconds,0);
  active.restored('detail',12);assert.equal(active.save('detail',progress(12)),false);
  assert.equal(active.save('detail',progress(18)),true);assert.equal(stored.get('core').seconds,0);
});

class Element extends EventTarget {
  children=[];parent=null;dataset={};attributes={};textContent='';hidden=false;style={};
  classList={add:()=>{}};
  constructor(tag){super();this.tag=tag;}
  append(...nodes){nodes.forEach(node=>{node.parent=this;this.children.push(node);});}
  replaceChildren(...nodes){this.children=[];this.append(...nodes);}
  setAttribute(key,value){this.attributes[key]=value;}
  focus(){}scrollIntoView(){}
  remove(){if(this.parent)this.parent.children=this.parent.children.filter(child=>child!==this);}
}
function harness(throwChild=false){
  const replaced=[],selected=[],players={};
  globalThis.document={createElement:tag=>new Element(tag)};
  globalThis.location={hash:'#detail'};
  globalThis.window={history:{replaceState:(_state,_title,value)=>replaced.push(value)}};
  const factories=Object.fromEntries(bundle().lessons.map(record=>[record.id,host=>{
    if(throwChild&&record.id==='system-detail')throw new Error('unavailable child');
    const player={time:0,paused:0,disposed:0,muted:false,
      dispose(){this.disposed++;host.replaceChildren();if(window.lessonStudio===this)delete window.lessonStudio;},
      seek(time){this.time=time;},play(){},pause(){this.paused++;},reset(){this.time=0;},setControl(){},
      setMuted(value){this.muted=value;},getState(){return {time:this.time,muted:this.muted,playing:false,controls:{},beatId:'beat',description:'saved'};}};
    players[record.id]=player;window.lessonStudio=player;window.seek=player.seek;return player;
  }]));
  const root=new Element('div');
  const path=mountPath(root,bundle().path,factories,{hashNavigation:false,brand:false,onSelect:node=>selected.push(node.lesson_id)});
  return {path,players,selected,replaced,root};
}
test('path navigation preserves each paused revision and reports the active chat/feedback identity', () => {
  const {path,players,selected,replaced}=harness();
  assert.equal(path.getState().nodeId,'overview'); // app hash never changes the path entry
  const core=path.getPlayer('overview');core.seek(13);core.setMuted(true);
  path.select('detail');path.getPlayer('detail').seek(7);
  assert(core.paused>0);assert.equal(players['system-detail'].muted,true);
  assert.deepEqual(selected,['system-core','system-detail']);
  path.back();assert.equal(path.getPlayer('overview').getState().time,13);
  assert.equal(path.getPlayer('detail').getState().time,7);
  assert.deepEqual(selected,['system-core','system-detail','system-core']);assert.deepEqual(replaced,[]);
  path.dispose();path.dispose();
  assert.equal(players['system-core'].disposed,1);assert.equal(players['system-detail'].disposed,1);
  assert.equal(window.learningPath,undefined);assert.equal(window.lessonStudio,undefined);
  path.select('detail');assert.equal(players['system-detail'].disposed,1);
});
test('a failed deeper mount keeps the previous scene and discussion revision', () => {
  const {path,players,selected}=harness(true);players['system-core'].seek(9);path.select('detail');
  assert.equal(path.getState().nodeId,'overview');assert.equal(window.lessonStudio,players['system-core']);
  assert.equal(players['system-core'].getState().time,9);assert.deepEqual(selected,['system-core']);path.dispose();
});
test('disposing a pending narration prevents delayed media events from reviving the hidden lesson', async () => {
  class Media extends EventTarget {
    currentTime=0;muted=false;paused=true;ended=false;
    play(){return new Promise(resolve=>{this.finishPlay=resolve;});}
    pause(){this.paused=true;}
  }
  const media=new Media();let changed=0;const transport=new NarrationTransport(media,30,()=>changed++);
  const pending=transport.play();transport.dispose();const before=changed;
  media.paused=false;media.dispatchEvent(new Event('playing'));media.finishPlay();await pending;
  media.dispatchEvent(new Event('waiting'));media.dispatchEvent(new Event('error'));
  assert.equal(media.paused,true);assert.equal(changed,before);assert.notEqual(transport.status,'playing');
});
