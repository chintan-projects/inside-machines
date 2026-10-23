/** Source-bound native artwork. Unknown revisions preserve their original media. */
import registry from '../../native/registry.json';
import publishedSpecs from '../../native/specs.json';
import { nativeDefinitions } from '../../native/definitions';
import type { NativeDefinition } from '../../native/definitions';
import type { NativeSpec } from './native-contracts';
import type { FrameState, Lesson } from './contracts';

let definitions:readonly NativeDefinition[]|undefined;
interface RegistryEntry {id:string;fingerprint:string;lessons:string[]}
const entries=registry.renderers as readonly RegistryEntry[];
// Canonical strings retain Python number/Unicode serialization for build-time SHA checks.
const specs=publishedSpecs as unknown as Readonly<Record<string,string>>;
const stable=(value:unknown):string=>JSON.stringify(value,(_key,item:unknown)=>
  item&&typeof item==='object'&&!Array.isArray(item)
    ? Object.fromEntries(Object.entries(item).sort(([a],[b])=>a.localeCompare(b))) : item);

export function nativeLesson(spec:NativeSpec,source:string,videoReady:boolean):Lesson<FrameState>|undefined {
  const entry=entries.find(item=>item.id===spec.renderer.id);
  if(!entry || entry.fingerprint!==spec.renderer.fingerprint || !entry.lessons.includes(spec.canonical))return undefined;
  definitions??=nativeDefinitions();
  const definition=definitions.find(item=>item.spec.canonical===spec.canonical && item.spec.renderer.id===entry.id);
  const expected:unknown=specs[spec.canonical]?JSON.parse(specs[spec.canonical]):undefined;
  if(!definition || !expected || stable(expected)!==stable(spec))return undefined;
  const lesson=definition.lesson;
  return {...lesson,narration:videoReady?{id:`${lesson.id}-bound-media`,src:source,duration:lesson.duration,
    cues:spec.stages.map(stage=>({start:stage.start,end:stage.end,still:stage.still,text:stage.narration}))}:undefined};
}
