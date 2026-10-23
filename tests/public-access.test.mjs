import test from 'node:test';
import assert from 'node:assert/strict';
import {openSession,checkedMember,entryPage} from '../web/session.ts';
import {api,ApiError,askChat} from '../web/api.ts';
import {rememberMember,offlineMember,prepareSavedPath} from '../web/offline.ts';
import {coreBundle} from '../web/studio/learning-bundle.ts';
import {reviewLabel} from '../web/review-label.ts';
import {previewChange} from '../web/public-preview.ts';

const guest=id=>({id,name:'Curious visitor',owner:false,guest:true});
const owner={id:'owner-a',name:'Owner',owner:true,guest:false};

test('public entry opens a unique guest session directly and preserves the server identity',async()=>{
  for(const id of ['visitor-one','visitor-two']) {
    const calls=[];
    const session=await openSession(async(path,body)=>{
      calls.push([path,body]);return path==='/health'?{public_access:true}:guest(id);
    });
    assert.deepEqual(calls,[['/health',undefined],['/auth/guest',{}]]);
    assert.equal(session.member.id,id);assert.equal(session.member.guest,true);assert.equal(session.publicAccess,true);
    assert.equal(entryPage('lesson/refrigerator-r2-core',session.member,true,false,true),'content');
  }
});
test('guest bootstrap preserves an existing authenticated owner rather than downgrading it',async()=>{
  const session=await openSession(async path=>path==='/health'?{public_access:true}:owner);
  assert.deepEqual(session.member,owner);assert.equal(entryPage('owner',session.member,true,false,true),'owner');
});
test('closed mode still probes its member cookie and shows invite access only for a confirmed401',async()=>{
  const calls=[];
  const session=await openSession(async path=>{
    calls.push(path);if(path==='/health')return {public_access:false};throw new ApiError('Expired',401);
  });
  assert.deepEqual(calls,['/health','/auth/me']);assert.deepEqual(session,{publicAccess:false,member:null});
  assert.equal(entryPage('',null,false,false,true),'join');
  assert.equal(entryPage('',null,false,false,true,true),'unavailable');
  await assert.rejects(openSession(async path=>{if(path==='/health')return {public_access:false};throw new ApiError('Unavailable',503);}),/Unavailable/);
});
test('failed public bootstrap never falls back to an invite form or invents a guest',async()=>{
  await assert.rejects(openSession(async path=>{if(path==='/health')return {public_access:true};throw new ApiError('Guest unavailable',503);}),/Guest unavailable/);
  assert.equal(entryPage('',null,true,false,true),'unavailable');
  assert.equal(entryPage('',null,null,false,true),'unavailable');
  assert.throws(()=>checkedMember({id:'shared-guest',name:'Visitor',owner:true,guest:true}),/invalid browser session/);
  assert.throws(()=>checkedMember({id:'',name:'Visitor',owner:false,guest:true}),/invalid browser session/);
});
test('pending offline sign-out is revoked before a new public session and failures stop renewal',async()=>{
  const calls=[];
  await openSession(async(path)=>{calls.push(path);return path==='/health'?{public_access:true}:path==='/auth/guest'?guest('after-logout'):{};},true);
  assert.deepEqual(calls,['/health','/auth/logout','/auth/guest']);
  const failed=[];
  await assert.rejects(openSession(async path=>{
    failed.push(path);if(path==='/health')return {public_access:true};throw new ApiError('Logout unconfirmed',503);
  },true),/Logout unconfirmed/);
  assert.deepEqual(failed,['/health','/auth/logout']);
});
test('owner routes are explicit and never render owner controls for a public visitor or offline profile',()=>{
  const visitor=guest('visitor');
  assert.equal(entryPage('owner',visitor,true,false,true),'owner-login');
  assert.equal(entryPage('owner/login',visitor,true,false,true),'owner-login');
  assert.equal(entryPage('owner',owner,true,false,false),'offline');
  assert.equal(entryPage('owner/login',owner,true,false,true),'owner');
  assert.equal(entryPage('lesson/fridge',visitor,true,true,true),'opening');
  assert.equal(entryPage('',null,true,false,false),'offline');
});
test('offline profiles retain individual guest IDs while stripping owner authority',()=>{
  const previous=globalThis.localStorage,values=new Map();
  globalThis.localStorage={getItem:key=>values.get(key)??null,setItem:(key,value)=>values.set(key,value)};
  try {
    rememberMember(guest('private-browser-id'));assert.deepEqual(offlineMember(),guest('private-browser-id'));
    rememberMember(owner);assert.equal(offlineMember().owner,false);assert.equal(offlineMember().guest,false);
    assert.equal(offlineMember().id,'owner-a');
  } finally{globalThis.localStorage=previous;}
});
test('public review-draft labels survive offline preparation without private feedback',async()=>{
  const lesson={id:'native-demo',spec:{version:2,title:'A draft',summary:'A native public demonstration.',question:'How does it work?',teaching:{goal:'Follow the input through a working mechanism.'},graphics:[{id:'working-section'}]},
    review_needed:true,public_preview:true,video_ready:false,spec_sha256:'1'.repeat(64),video_sha256:'',feedback:{value:'down',reason:'private'}};
  const [saved]=await prepareSavedPath('unique-visitor',coreBundle(lesson),'native-demo',async()=>{throw new Error('No media expected');});
  assert.equal(saved.lesson.public_preview,true);assert.equal(saved.lesson.review_needed,true);assert.equal(saved.lesson.feedback,null);
  assert.equal(reviewLabel(saved.lesson),'Review draft · public preview');
  assert.equal(reviewLabel({public_preview:true,review_needed:false}),'Review draft · public preview');
  assert.equal(reviewLabel({review_needed:false}),'');
});
test('authentication probes do not trigger global expiry and failed chat is never retried',async()=>{
  const previousFetch=globalThis.fetch,previousWindow=globalThis.window;
  const events=new EventTarget();let expired=0,calls=0;
  events.addEventListener('inside:unauthorized',()=>expired++);globalThis.window=events;
  globalThis.fetch=async()=>{calls++;return new Response(JSON.stringify({detail:'Expired'}),{status:401});};
  try {
    await assert.rejects(api('/auth/me'),ApiError);await assert.rejects(api('/auth/guest',{}),ApiError);
    assert.equal(expired,0);
    await assert.rejects(api('/requests',{}),ApiError);assert.equal(expired,1);
    await assert.rejects(askChat('chat-id','A private question',()=>{}),/not retried/);
    assert.equal(expired,2);assert.equal(calls,4);
  } finally{globalThis.fetch=previousFetch;globalThis.window=previousWindow;}
});
test('preview exposure uses the candidate to grant and the original saved binding to revoke stale access',()=>{
  const binding=char=>({spec_sha256:char.repeat(64),video_sha256:char.repeat(64),bundle_sha256:char.repeat(64),bindings:[]});
  const state={lesson_id:'native-demo',candidate:binding('b'),preview:{binding:binding('a'),enabled:true,by:'owner',at:1},enabled:false,issue:'Changed source',notice:''};
  assert.deepEqual(previewChange(state,true),{enabled:true,spec_sha256:'b'.repeat(64),video_sha256:'b'.repeat(64),bundle_sha256:'b'.repeat(64)});
  assert.deepEqual(previewChange({...state,candidate:null},false),{enabled:false,spec_sha256:'a'.repeat(64),video_sha256:'a'.repeat(64),bundle_sha256:'a'.repeat(64)});
  assert.equal(previewChange({...state,candidate:null},true),undefined);
  assert.equal(previewChange({...state,preview:{...state.preview,enabled:false}},false),undefined);
});
