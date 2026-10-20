import type { LessonSpec } from '../contracts';
import type { Beat, Change, Pose, Scenario } from './contracts';

export function teachingAt(spec:LessonSpec, seconds:number):[Beat,number] {
  if(!spec.teaching || !Number.isFinite(seconds)) throw new Error('A teaching scene needs a valid lesson and clock.');
  let elapsed=0;
  for(let i=0;i<spec.stages.length;i++) {
    const stage=spec.stages[i];
    if(seconds<elapsed+stage.duration || i===spec.stages.length-1) {
      const fraction=Math.max(0,Math.min(1,(seconds-elapsed)/stage.duration));
      return [spec.teaching.beats[i],Math.max(0,Math.min(1,(fraction-.12)/.58))];
    }
    elapsed+=stage.duration;
  }
  throw new Error('Lesson has no teaching checkpoints.');
}
export function scenarioFor(spec:LessonSpec, beat:Beat, id?:string):Scenario|undefined {
  if(!spec.teaching) throw new Error('Missing teaching contract.');
  if(id===undefined) return spec.teaching.scenarios.find(s=>s.beat===beat.id);
  const scenario=spec.teaching.scenarios.find(s=>s.id===id);
  if(!scenario || scenario.beat!==beat.id) throw new Error('Scenario is unavailable for this step.');
  return scenario;
}
export function sampledPose(change:Change|undefined, progress:number):Pose {
  if(!Number.isFinite(progress)) throw new Error('Scene progress must be finite.');
  if(!change) return {x:0,y:0,sx:1,sy:1,angle:0,fill:'',opacity:1};
  const poses=[change.before,...(change.via||[]),change.after], overall=Math.max(0,Math.min(1,progress));
  const segment=Math.min(poses.length-2,Math.floor(overall*(poses.length-1))),p=overall*(poses.length-1)-segment,a=poses[segment],b=poses[segment+1];
  let fill=a.fill || b.fill;
  if(a.fill && b.fill) fill='#'+[1,3,5].map(i=>Math.round(parseInt(a.fill.slice(i,i+2),16)*(1-p)+parseInt(b.fill.slice(i,i+2),16)*p).toString(16).padStart(2,'0')).join('');
  return { x:a.x+(b.x-a.x)*p,y:a.y+(b.y-a.y)*p,sx:a.sx+(b.sx-a.sx)*p,sy:a.sy+(b.sy-a.sy)*p,angle:a.angle+(b.angle-a.angle)*p,fill,opacity:a.opacity+(b.opacity-a.opacity)*p };
}
