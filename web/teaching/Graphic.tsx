import { useId } from 'react';
import type { ReactElement } from 'react';
import { sectionArtwork } from './Sections';
import type { LessonSpec, Part } from '../contracts';
import type { Change } from './contracts';
import { sampledPose, scenarioFor, teachingAt } from './state';

function Mark({part,change,progress}:{readonly part:Part;readonly change?:Change;readonly progress:number}):ReactElement {
  const pose=sampledPose(change,progress,part.color), {x,y,w,h}=part, cx=x+w/2,cy=y+h/2;
  const attrs={fill:pose.fill||part.color,stroke:part.stroke,strokeWidth:2};
  let shape:ReactElement;
  if(part.shape==='box') shape=<rect x={x} y={y} width={w} height={h} rx={7} {...attrs}/>;
  else if(part.shape==='ellipse'||part.shape==='ring') shape=<ellipse cx={cx} cy={cy} rx={w/2} ry={h/2} {...attrs} fill={part.shape==='ring'?'none':attrs.fill} strokeWidth={part.shape==='ring'?5:2}/>;
  else if(part.shape==='text') shape=<text x={x} y={y} dominantBaseline="hanging" fontSize={h} fontWeight={550} fill={attrs.fill}>{part.label}</text>;
  else if(part.shape==='polygon') shape=<polygon points={part.points.map(p=>p.join(',')).join(' ')} {...attrs}/>;
  else shape=<polyline points={part.points.map(p=>p.join(',')).join(' ')} fill="none" stroke={part.stroke} strokeWidth={Math.max(2,w)} strokeLinecap="round" strokeLinejoin="round"/>;
  return <g data-graphic={part.id} transform={`translate(${pose.x} ${pose.y}) translate(${cx} ${cy}) rotate(${pose.angle}) scale(${pose.sx} ${pose.sy}) translate(${-cx} ${-cy})`} opacity={pose.opacity}>{shape}</g>;
}
export function Graphic({spec,seconds,scenario,still=false}:{readonly spec:LessonSpec;readonly seconds:number;readonly scenario?:string;readonly still?:boolean}):ReactElement {
  const namespace=useId().replaceAll(':','');
  const [beat,rawProgress]=teachingAt(spec,seconds), selected=scenarioFor(spec,beat,scenario);
  const art=spec.teaching?.renderer==='authored-sections-v1'?sectionArtwork(spec,beat.stage,namespace):undefined;
  const progress=still?(rawProgress<.5?0:1):rawProgress;
  const changes=new Map(beat.changes.map(c=>[c.target,c]));
  selected?.changes.forEach(c=>changes.set(c.target,c));
  return <svg className="ce-graphic" viewBox="0 0 900 540" role="img" aria-label={beat.visible_change}>
    <title>{beat.visible_change}</title><desc>{beat.static_explanation}</desc>
    {art&&<g data-authored-art="true" dangerouslySetInnerHTML={{__html:art.markup}}/>}
    {[...(spec.graphics||[])].sort((a,b)=>a.layer-b.layer).filter(p=>beat.graphics.includes(p.id)&&!art?.replaced.has(p.id)).map(part=><Mark key={part.id} part={part} change={changes.get(part.id)} progress={progress}/>) }
  </svg>;
}
