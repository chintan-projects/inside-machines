// Build a local review bundle from Studio's actual delivery; serve only its explicit assets.
// Usage: node build.mjs && node review.mjs [--port 8879]
import {readFileSync,writeFileSync,readdirSync,mkdirSync,copyFileSync,statSync,createReadStream,existsSync} from 'node:fs';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createServer} from 'node:http';
import {createHash} from 'node:crypto';
import {loadNarration} from './lesson/load.mjs';
const SCENES=loadNarration().scenes;
const root=dirname(fileURLToPath(import.meta.url));
const series=join(root,'video');
const records=join(series,'production/episodes/ep01/delivery-records');
const record=existsSync(records)?readdirSync(records).sort().at(-1):null;
const output=join(root,'review-site');mkdirSync(output,{recursive:true});
let metadata=null,timeline=null,chapters=[];
if(record){
 const deliveredScript=readFileSync(join(records,record,'script.yaml'));
 const currentScript=readFileSync(join(series,'production/episodes/ep01/script.yaml'));
 if(!deliveredScript.equals(currentScript))throw new Error('Delivered movie belongs to another script. Review and render the current revision before serving it.');
 metadata=JSON.parse(readFileSync(join(records,record,'metadata.json')));
 timeline=JSON.parse(readFileSync(join(records,record,'timeline.json')));
 for(const file of [metadata.files.video_file_name,metadata.files.cover_file_name,metadata.files.subtitles[0].file_name]){
  if(!file||file!==file.split(/[\\/]/).at(-1))throw new Error('Delivery filename must be a basename.');
 }
 copyFileSync(join(series,metadata.files.video_file_name),join(output,'film.mp4'));
 copyFileSync(join(series,metadata.files.cover_file_name),join(output,'poster.png'));
 const srt=readFileSync(join(series,metadata.files.subtitles[0].file_name),'utf8');
 writeFileSync(join(output,'captions.vtt'),'WEBVTT\n\n'+srt.replace(/(\d{2}:\d{2}:\d{2}),(\d{3})/g,'$1.$2'));
 chapters=timeline.scenes.map(scene=>({title:SCENES.find(item=>item.id===scene.scene_id)?.title??scene.scene_id,seconds:scene.start_seconds}));
}
const sourceHtml=readFileSync(join(root,'interactive/index.html'),'utf8');
const html=sourceHtml
 .replace('/* ACTUAL_TIMELINE_CHAPTERS */ []',()=>JSON.stringify(chapters))
 .replace('/* ACTUAL_MEDIA_DURATION */ null',()=>JSON.stringify(timeline?.duration_seconds??null))
 .replace('/* ACTUAL_MEDIA_READY */ false',()=>`/* ACTUAL_MEDIA_READY */ ${Boolean(record)}`);
writeFileSync(join(output,'index.html'),html);
const sha=path=>createHash('sha256').update(readFileSync(path)).digest('hex');
const gatePath=join(root,'review/core-readiness.json');
const gate=existsSync(gatePath)?JSON.parse(readFileSync(gatePath)):null;
const gateCurrent=gate?.script_sha256===sha(join(series,'production/episodes/ep01/script.yaml'));
const narrationPassed=gateCurrent&&gate.causal_teachback==='pass'&&gate.novel_transfer==='pass'&&!gate.findings.some(f=>['lost','wrong'].includes(f.kind)&&f.status!=='fixed');
writeFileSync(join(output,'receipt.json'),JSON.stringify({revision:'prefill-decode-r6',
 interactive_status:'computed_scalar_experiment_and_full_transcript',human_acceptance:false,
 narration_status:narrationPassed?'fresh_automated_read_and_novel_transfer_passed':'draft_or_stale_review',
 video_status:record?'delivered':'awaiting_delivery',
 duration_seconds:timeline?.duration_seconds??null,video_sha256:record?sha(join(output,'film.mp4')):null,
 script_sha256:sha(join(series,'production/episodes/ep01/script.yaml')),
 html_sha256:sha(join(output,'index.html')),chapters},null,2));
const args=process.argv.slice(2);const port=Number(args[args.indexOf('--port')+1]||8879);
if(!Number.isInteger(port)||port<1024||port>65535)throw new Error('Use an unprivileged port.');
const files=new Map([['/','index.html'],['/index.html','index.html'],['/receipt.json','receipt.json'],...(record?[['/film.mp4','film.mp4'],['/poster.png','poster.png'],['/captions.vtt','captions.vtt']]:[])]);
const types={html:'text/html; charset=utf-8',mp4:'video/mp4',png:'image/png',vtt:'text/vtt; charset=utf-8',json:'application/json'};
const server=createServer((req,res)=>{
 try {
  if(!['GET','HEAD'].includes(req.method)){res.writeHead(405,{Allow:'GET, HEAD'});return res.end();}
  const name=files.get(new URL(req.url,'http://localhost').pathname);
  if(!name){res.writeHead(404);return res.end('Not found');}
  const path=join(output,name),size=statSync(path).size;
  const headers={'Content-Type':types[name.split('.').at(-1)],'Cache-Control':'no-store','Accept-Ranges':'bytes','X-Content-Type-Options':'nosniff'};
  let start=0,end=size-1,status=200;
  if(req.headers.range){
   const match=/^bytes=(\d*)-(\d*)$/.exec(req.headers.range);
   if(!match||(!match[1]&&!match[2])){res.writeHead(416,{'Content-Range':`bytes */${size}`});return res.end();}
   start=match[1]?Number(match[1]):Math.max(0,size-Number(match[2]));
   end=match[1]?(match[2]?Math.min(Number(match[2]),size-1):size-1):size-1;
   if(!Number.isSafeInteger(start)||!Number.isSafeInteger(end)||start>end||start>=size){res.writeHead(416,{'Content-Range':`bytes */${size}`});return res.end();}
   status=206;headers['Content-Range']=`bytes ${start}-${end}/${size}`;
  }
  headers['Content-Length']=String(end-start+1);res.writeHead(status,headers);
  if(req.method==='HEAD')return res.end();
  createReadStream(path,{start,end}).on('error',()=>res.destroy()).pipe(res);
 }catch {if(!res.headersSent)res.writeHead(500);res.end('Could not serve review asset.');}
});
server.on('error',err=>{console.error(err.code==='EADDRINUSE'?`Port ${port} is in use; choose --port.`:'Local review server could not start.');process.exitCode=1;});
server.listen(port,'127.0.0.1',()=>console.log(`Local review: http://127.0.0.1:${port}/\nOnly the explicit local review assets are served. No AI calls.`));
