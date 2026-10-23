/** Additive authored artwork contract. Executable renderers come from trusted source. */
import type { LessonSpec, Stage } from '../contracts';
import type { Assessment, Claim } from '../teaching/contracts';
import type { Action, Control, Controls } from './contracts';

export interface NativeComponent { id:string; name:string; description:string; label:string }
export interface NativeStage extends Stage {
  id:string; start:number; end:number; still:number; focus:string;
  kind:'orientation'|'causal'|'recombine';
  input_state:string; output_state:string; source_indices:number[]; claims:string[];
}
export interface NativeScenario {
  id:string; label:string; kind:'qualitative'|'computed'; controls:Controls;
  cue_id:string; outcome:string; explanation:string; claims:string[];
}
export interface NativeSpec extends Omit<LessonSpec, 'version'|'parts'|'stages'|'teaching'|'graphics'> {
  version:3; spec_version:'native-studio-1'; renderer:{id:string; fingerprint:string};
  components:NativeComponent[]; stages:NativeStage[];
  controls:Control[]; default_controls:Controls; actions:Action[];
  teaching:{goal:string; misconception:string; core:string[];
    operation:'simultaneous'|'sequential'|'controlled'; operation_note:string;
    invariants:string[]; claims:Claim[]; prediction:Assessment; transfer:Assessment;
    teach_back:string; teach_back_reasoning:string[]; scenarios:NativeScenario[]};
}
export type StoredSpec = LessonSpec | NativeSpec;

export function componentIds(spec:StoredSpec):string[] {
  return (spec.version===3 ? spec.components : spec.parts).map(part=>part.id);
}
export function chapterIndex(spec:StoredSpec, time:number):number {
  const bounded=Number.isFinite(time)?Math.max(0,time):0;
  let elapsed=0;
  for(let i=0;i<spec.stages.length;i++) {
    elapsed+=spec.stages[i].duration;
    if(bounded<elapsed)return i;
  }
  return Math.max(0,spec.stages.length-1);
}
export function chapterStarts(spec:StoredSpec):number[] {
  let elapsed=0;
  return spec.stages.map(stage=>{const start=elapsed;elapsed+=stage.duration;return start;});
}
export function lessonDuration(spec:StoredSpec):number {
  return spec.stages.reduce((total,stage)=>total+stage.duration,0);
}
