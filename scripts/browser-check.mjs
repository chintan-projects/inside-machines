// Local Chrome checks using the same dependency-free CDP approach as Anatomy.
import { spawn } from 'node:child_process';
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import assert from 'node:assert/strict';
import { chromePort } from '../vendor/anatomy/scripts/chrome-port.mjs';
const profile=mkdtempSync(join(tmpdir(),'inside-check-'));
const binary=process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const chrome=spawn(binary,['--headless=new','--remote-debugging-port=0',`--user-data-dir=${profile}`,'--no-first-run','--hide-scrollbars','about:blank']);
let socket;
try {
  const port=await chromePort(chrome,profile);
  const page=await(await fetch(`http://127.0.0.1:${port}/json/new?about:blank`,{method:'PUT'})).json();
  socket=new WebSocket(page.webSocketDebuggerUrl);
  const pending=new Map(), errors=[];
  let id=0;
  socket.onmessage=({data})=>{
    const m=JSON.parse(data);
    if(m.id && pending.has(m.id)) { pending.get(m.id)(m);pending.delete(m.id); }
    if(m.method==='Runtime.exceptionThrown') errors.push(m.params.exceptionDetails.text);
    if(m.method==='Runtime.consoleAPICalled' && ['error','warning'].includes(m.params.type)) errors.push(m.params.args.map(a=>a.value).join(' '));
  };
  await new Promise(resolve=>socket.onopen=resolve);
  const send=(method,params={})=>new Promise((resolve,reject)=>{
    const call=++id;
    const timer=setTimeout(()=>reject(new Error(`Timed out: ${method}`)),15000);
    pending.set(call,m=>{clearTimeout(timer);if(m.error)reject(new Error(m.error.message));else resolve(m.result);});
    socket.send(JSON.stringify({id:call,method,params}));
  });
  const evaluate=async expression=>{
    const r=await send('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true});
    if(r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || r.exceptionDetails.text);
    return r.result.value;
  };
  const until=async expr=>{
    for(let i=0;i<100;i++) {if(await evaluate(expr))return;await new Promise(r=>setTimeout(r,100));}
    throw new Error(`Condition not reached: ${expr}`);
  };
  const screenshot=async(path,selector='body',scale=1)=>{
    await evaluate('window.scrollTo(0,0)');
    const box=await evaluate(`(()=>{const r=document.querySelector(${JSON.stringify(selector)}).getBoundingClientRect();return {x:Math.max(0,r.x+scrollX),y:Math.max(0,r.y+scrollY),width:r.width,height:r.height,scale:${scale}}})()`);
    const result=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:true,clip:box});
    if(path)writeFileSync(path,Buffer.from(result.data,'base64'));
    return result.data;
  };
  await send('Runtime.enable');await send('Page.enable');await send('Network.enable');
  await send('Emulation.setDeviceMetricsOverride',{width:1440,height:1200,deviceScaleFactor:1,mobile:false});
  await send('Page.navigate',{url:'http://127.0.0.1:4173/'});
  await until('Boolean(window.labState)');
  mkdirSync('shots',{recursive:true});
  await screenshot('shots/desktop.png');
  assert.equal(await evaluate('document.documentElement.scrollWidth <= innerWidth'),true);
  await evaluate("document.getElementById('play').click()");
  await until('window.labState.t > 0.2');
  await evaluate("document.getElementById('play').click()");
  const paused=await evaluate('window.labState.t');
  await new Promise(r=>setTimeout(r,150));
  assert.equal(await evaluate('window.labState.t'),paused);
  const frames=[];
  for(const time of [4,19,34,48,65]) {
    await evaluate(`(()=>{const el=document.getElementById('timeline');el.value=${time};el.dispatchEvent(new Event('input'));})()`);
    const result=await evaluate('({t:labState.t,water:labState.water,rpm:labState.rpm,stage:labState.stage.name})');
    assert.equal(result.t,time);
    console.log('Stage:',JSON.stringify(result));
    frames.push(await screenshot(null,'.lesson',.55));
  }
  const sheet=await evaluate(`(async()=>{const srcs=${JSON.stringify(frames)};const imgs=await Promise.all(srcs.map(s=>new Promise(resolve=>{const i=new Image();i.onload=()=>resolve(i);i.src='data:image/png;base64,'+s})));const w=imgs[0].width,h=imgs[0].height,c=document.createElement('canvas');c.width=w*3;c.height=h*2;const ctx=c.getContext('2d');ctx.fillStyle='#f5f3eb';ctx.fillRect(0,0,c.width,c.height);imgs.forEach((i,n)=>ctx.drawImage(i,(n%3)*w,Math.floor(n/3)*h));return c.toDataURL('image/png').split(',')[1]})()`);
  writeFileSync('shots/stages.png',Buffer.from(sheet,'base64'));
  await screenshot('shots/mechanism-closeup.png','#machine',2);
  await evaluate("document.getElementById('specific-mode').click()");
  assert.equal(await evaluate("document.getElementById('specific-panel').hidden"),false);
  await evaluate("document.getElementById('machine-model').value='Example washer';document.getElementById('manual').value='<script>test</script>';document.getElementById('specific-form').requestSubmit()");
  assert.equal(await evaluate('window.machineContext.verified'),false);
  assert.match(await evaluate("document.getElementById('evidence-status').textContent"),/Unverified/);
  await evaluate("document.getElementById('question').value='How does a refrigerator work?';document.getElementById('question-form').requestSubmit()");
  assert.match(await evaluate("document.getElementById('request-status').textContent"),/not connected/);
  await evaluate("document.getElementById('question').value='How does my washing machine work?';document.getElementById('question-form').requestSubmit()");
  assert.equal(await evaluate("document.getElementById('specific-panel').hidden"),false);
  await screenshot('shots/specific-machine.png');
  await evaluate("document.getElementById('general-mode').click();document.getElementById('reset').click()");
  await send('Emulation.setDeviceMetricsOverride',{width:390,height:1000,deviceScaleFactor:1,mobile:true});
  assert.equal(await evaluate('document.documentElement.scrollWidth <= innerWidth'),true);
  await screenshot('shots/mobile.png');
  await send('Emulation.setEmulatedMedia',{features:[{name:'prefers-reduced-motion',value:'reduce'}]});
  assert.equal(await evaluate("getComputedStyle(document.getElementById('inlet-flow')).animationName"),'none');
  await evaluate("document.getElementById('timeline').value=65;document.getElementById('timeline').dispatchEvent(new Event('input'))");
  assert.equal(await evaluate('window.labState.stage.name'),'Spin');
  await until('Boolean(navigator.serviceWorker.controller)');
  assert.equal(await evaluate("caches.open('inside-lab-v1').then(c=>c.keys()).then(k=>k.length)"),9);
  await send('Network.emulateNetworkConditions',{offline:true,latency:0,downloadThroughput:0,uploadThroughput:0});
  await evaluate('window.labState=null');
  await send('Page.reload',{ignoreCache:true});
  await until('Boolean(window.labState)');
  await evaluate("document.getElementById('timeline').value=65;document.getElementById('timeline').dispatchEvent(new Event('input'))");
  assert.equal(await evaluate('window.labState.stage.name'),'Spin');
  assert.deepEqual(errors,[]);
  console.log('PASS: playback, pause, five stages, specific-model intake, unsupported questions, mobile layout, reduced motion, service worker cache, and offline reload. Console clean.');
} finally {
  socket?.close();chrome.kill('SIGKILL');
  await new Promise(resolve=>chrome.once('exit',resolve));
  rmSync(profile,{recursive:true,force:true});
}
