/** The hosted app adapts validated CE-1 data to the same D1 player as local studies. */
import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import type { Lesson as StoredLesson, LessonSpec } from '../contracts';
import { Graphic } from '../teaching/Graphic';
import { scenarioFor, teachingAt } from '../teaching/state';
import { acSceneHash } from '../teaching/Context';
import { hasSectionArtwork } from '../teaching/Sections';
import type { Action, Controls, FrameState, Lesson, Narration, Question } from './contracts';

interface CausalFrame extends FrameState { readonly scenario?: string; readonly stage: number }
export function rendererAvailable(spec: LessonSpec): boolean {
  const teaching = spec.teaching;
  if (!teaching) return false;
  if (teaching.renderer === 'declarative') return true;
  if (teaching.renderer === 'ac-cutaway-v2') return teaching.renderer_fingerprint === acSceneHash;
  return teaching.renderer === 'authored-sections-v1' && hasSectionArtwork(spec);
}
export function chapterStarts(spec: LessonSpec): number[] {
  let elapsed = 0;
  return spec.stages.map(stage => { const start = elapsed; elapsed += stage.duration; return start; });
}
export function adaptLesson(record: StoredLesson, mediaUrl: string): Lesson<CausalFrame> {
  const { spec } = record, teaching = spec.teaching;
  if (spec.version !== 2 || !teaching || !spec.graphics?.length) throw new Error('Missing validated teaching data');
  if (!rendererAvailable(spec)) throw new Error('The exact renderer for this historical revision is unavailable.');
  const starts = chapterStarts(spec), total = spec.stages.reduce((n,s) => n+s.duration,0);
  const action = (index: number, scenario?: string): Action => ({
    id: `chapter-${index}${scenario ? '-'+scenario : ''}`, label: spec.stages[index].title,
    start: starts[index], end: starts[index]+spec.stages[index].duration,
    still: starts[index]+spec.stages[index].duration*.72, controls: { scenario: scenario ?? 'auto' },
  });
  const assessment = (value: typeof teaching.prediction): Question => ({
    prompt:value.prompt, choices:value.choices, answer:value.explanation,
  });
  const narration: Narration | undefined = record.video_ready ? {
    id: record.id+'-narration', src:mediaUrl, duration:total,
    cues:spec.stages.map((stage,i) => ({start:starts[i],end:starts[i]+stage.duration,
      still:starts[i]+stage.duration*.72,text:stage.narration})),
  } : undefined;
  return {
    id:record.id, title:spec.question, summary:spec.big_idea, duration:total,
    defaultControls:{scenario:'auto'}, actions:spec.stages.map((_,i)=>action(i)),
    controls:teaching.scenarios.length ? [{key:'scenario',label:'Compare a condition',
      options:teaching.scenarios.map(s=>({value:s.id,label:s.label}))}] : [],
    prediction:assessment(teaching.prediction),transfer:assessment(teaching.transfer),
    takeaway:spec.big_idea,scope:[spec.family,...spec.assumptions,teaching.operation_note].join(' '),
    sources:spec.sources.map((s,i)=>({title:s.title,url:s.url,
      locator:teaching.claims.filter(c=>c.source===i).map(c=>c.locator).join(' · ') || s.supports})),
    narration,
    stateAt(time:number,controls:Controls):CausalFrame {
      const t=Math.max(0,Math.min(total,Number.isFinite(time)?time:0)),[beat]=teachingAt(spec,t);
      const explicit=teaching.scenarios.find(s=>s.id===controls.scenario&&s.beat===beat.id);
      const normal=scenarioFor(spec,beat),selected=explicit??normal;
      const comparing=selected&&selected.id!==normal?.id;
      return {time:t,beatId:beat.id,stage:beat.stage,scenario:selected?.id,
        description:comparing ? selected.outcome+'. '+selected.explanation : spec.stages[beat.stage].narration};
    },
    render(state) {
      const svg=renderToStaticMarkup(createElement(Graphic,{spec,seconds:state.time,scenario:state.scenario}),{identifierPrefix:record.id});
      const [beat]=teachingAt(spec,state.time);
      return {svg:svg.replace(/^<svg[^>]*>/,'').replace(/<\/svg>$/,''),labels:[],
        viewport:{x:0,y:0,width:900,height:540},alt:beat.visible_change,
        caption: `Comes in: ${spec.stages[beat.stage].input_state ?? 'See the scene'}. Leaves: ${spec.stages[beat.stage].output_state ?? 'See the scene'}. `+
          (state.scenario ? teaching.scenarios.find(s => s.id === state.scenario)!.explanation : 'Qualitative model; motion shows a relationship, not a measured rate.')};
    },
    controlsVisible:()=>teaching.scenarios.length>0,
    controlValues:state=>({scenario:state.scenario ?? 'auto'}),
    takeawayVisible:state=>state.time>=starts[starts.length-1],
    controlRestart(controls) {
      const scenario=teaching.scenarios.find(s=>s.id===controls.scenario);
      if(!scenario) throw new Error('Unsupported reviewed condition');
      return action(teaching.beats.findIndex(b=>b.id===scenario.beat),scenario.id);
    },
  };
}
