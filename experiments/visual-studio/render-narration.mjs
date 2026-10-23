/** Offline local authoring only: no model/provider call, browser speech or network. */
import {mkdir, readFile, writeFile} from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import path from 'node:path';
import {validateNarration} from './narration.ts';

/** @param {Buffer|string} value @returns {string} */
const sha=value=>createHash('sha256').update(value).digest('hex');
/** @param {string} command @param {string[]} args @returns {string} */
const execute=(command,args)=>execFileSync(command,args,{encoding:'utf8',timeout:60000,stdio:['ignore','pipe','pipe']});
/** @param {string} file @returns {number} */
function duration(file) {
  const seconds=Number(execute('ffprobe',['-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',file]));
  if(!Number.isFinite(seconds)||seconds<=0)throw new Error('Invalid audio duration');
  return seconds;
}

/** @param {import('./contracts.ts').NarrationPlan} plan @param {string} dir @returns {Promise<void>} */
export async function renderNarration(plan,dir) {
  validateNarration(plan); await mkdir(dir,{recursive:true});
  const voice='Samantha', wordsPerMinute=168, clips=[];
  for(const [i,cue] of plan.cues.entries()) {
    const stem=path.join(dir,`cue-${i}`), text=stem+'.txt', raw=stem+'.aiff', wav=stem+'.wav';
    await writeFile(text,cue.text);
    execute('/usr/bin/say',['-v',voice,'-r',String(wordsPerMinute),'-f',text,'-o',raw]);
    const spoken=duration(raw), available=cue.end-cue.start;
    if(spoken>available)throw new Error(`${plan.id} cue ${i} exceeds its scene: ${spoken.toFixed(3)} > ${available}`);
    execute('ffmpeg',['-v','error','-y','-i',raw,'-af',`apad=whole_dur=${available}`,
      '-t',String(available),'-ar','24000','-ac','1',wav]);
    clips.push({start:cue.start,end:cue.end,spoken_seconds:spoken,file:wav});
  }
  const list=path.join(dir,'clips.txt'), mp3=path.join(dir,'narration.mp3');
  // ffconcat quoting is independent of shell quoting; commands never invoke a shell.
  await writeFile(list,clips.map(c=>`file '${c.file.replaceAll("'","'\\''")}'`).join('\n'));
  execute('ffmpeg',['-v','error','-y','-f','concat','-safe','0','-i',list,
    '-codec:a','libmp3lame','-b:a','96k','-t',String(plan.duration),mp3]);
  const encoded=duration(mp3);
  if(Math.abs(encoded-plan.duration)>.15)throw new Error('Encoded audio/story duration mismatch');
  await writeFile(path.join(dir,'manifest.json'),JSON.stringify({
    plan_id:plan.id,plan_sha256:sha(JSON.stringify(plan)),mp3_sha256:sha(await readFile(mp3)),
    synthesis:'local macOS computer speech',voice,words_per_minute:wordsPerMinute,
    encoded_seconds:encoded,story_seconds:plan.duration,clips:clips.map(({file,...cue})=>({...cue,file:path.basename(file)})),
    api_cost_usd:0,
  },null,2));
}
