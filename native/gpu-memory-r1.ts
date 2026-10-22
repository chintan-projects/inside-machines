/** Existing memory insight through the same trusted adapter; not a new whole-GPU core. */
import { memoryLesson } from '../experiments/gpu-study/depth-lessons';
import { memoryNarration } from '../experiments/gpu-study/depth-narration';
import type { FrameState, Lesson, Narration } from '../web/studio/contracts';
import type { NativeSpec } from '../web/studio/native-contracts';

export type NativeAuthoringMetadata = Omit<NativeSpec, 'renderer'>;

export function createGpuMemoryR1Definition(narrations:Readonly<Record<string,Narration>>={}):
  {readonly lesson:Lesson<FrameState>;readonly metadata:NativeAuthoringMetadata} {
  const original=memoryLesson(narrations[memoryNarration.id]??{...memoryNarration,src:''});
  const scope=original.scope+' This standalone insight preserves the existing eight-job/four-slot model. '+
    'It is not a complete GPU introduction. A playback round takes 1.5 seconds solely for visibility; '+
    'neither rounds nor elapsed playback are GPU clock cycles, measured bandwidth or speedup.';
  const render:typeof original.render=state=>{
    const source=original.render(state);
    const scene={...source,svg:source.svg.replaceAll(' data-studio-progress ',' data-studio-progress="" ')};
    if(state.working.length)return scene;
    return {...scene,attributes:scene.attributes?.filter(update=>
      update.selector!=='[data-studio-progress]'||update.name!=='width')};
  };
  const lesson:Lesson<FrameState>={...original,id:'gpu-memory-native-r1',scope,render};
  const ids=memoryNarration.cues.map(cue=>`${memoryNarration.id}-${cue.start}`);
  const titles=['Keep the same work','One ready input','Four ready inputs','What the model omits','Capacity needs data'];
  const incoming=['Eight input values and four available slots','One new input supplied each ideal round',
    'The same eight inputs and four available slots','Completed toy calculations','Available calculation capacity'];
  const outgoing=['The input supply is the variable to compare','One useful slot; other slots wait without inputs',
    'Up to four inputs can be calculated in the same ideal round','Real hardware overlap and caches remain outside this model',
    'Useful work requires both an instruction and its ready operands'];
  const claims=[
    {id:'ready-input',statement:'A calculation needs its required input values to be ready before it can usefully execute.',source:0,
      locator:'Programming Model §§1.2.1–1.2.3: execution resources and data/memory; dependency inference.',
      scope:'inference' as const,limitation:'The authored model supplies data before each round; this is not a universal GPU scheduling or timing model.'},
    {id:'same-capacity',statement:'Keeping the same execution capacity does not guarantee the same amount of useful work when data readiness changes.',source:0,
      locator:'Programming Model §§1.2.2–1.2.3: resources and data/memory; bounded inference illustrated by the source-bound toy model.',
      scope:'inference' as const,limitation:'One/four inputs, four slots and eight jobs are declared illustrative values, not hardware specifications or measured speed.'},
    {id:'real-limits',statement:'The toy supply-then-compute sequence omits real memory organization, scheduling and overlapping activity.',source:0,
      locator:'Programming Model §§1.2.1–1.2.3; scope boundaries of this authored discrete-GPU example.',
      scope:'generic' as const,limitation:'CUDA is one documented example. Architecture and memory behavior vary; no universal performance guarantee is claimed.'},
  ];
  const metadata:NativeAuthoringMetadata={
    version:3,spec_version:'native-studio-1',canonical:lesson.id,title:'Why GPU work can wait for inputs',
    aliases:['gpu-memory-input-supply','gpu work waiting for inputs'],family:'Generic GPU data-readiness insight',
    question:lesson.title,summary:lesson.summary,big_idea:lesson.takeaway,category:'Technology',accent:'#35645b',
    assumptions:[scope,'The exact toy arithmetic is input + 1 for eight inputs 0–7. Four slots remain available. '+
      'A round supplies either one or four ready inputs, then computes them; the model omits caches and transfer overlap.'],
    sources:lesson.sources.map(source=>({title:source.title,url:source.url,supports:source.locator})),
    components:[
      {id:'input-memory',name:'Input memory',description:'The eight fixed input values waiting for delivery to a calculation.',label:'Inputs waiting in memory'},
      {id:'calculation-slots',name:'Calculation slots',description:'Four available toy execution slots; a slot without a ready input cannot calculate that job.',label:'Four slots remain available'},
      {id:'output-memory',name:'Completed results',description:'Stored outputs from completed input-plus-one toy calculations.',label:'Completed results'},
    ],
    stages:memoryNarration.cues.map((cue,i)=>({
      id:ids[i],kind:i===1||i===2?'causal':i===4?'recombine':'orientation',
      start:cue.start,end:cue.end,still:cue.still,title:titles[i],explanation:cue.text,narration:cue.text,
      duration:cue.end-cue.start,parts:['input-memory','calculation-slots','output-memory'],
      cause:i===3?'This explicit scope boundary prevents an illustrative round from being mistaken for hardware timing.':
        'Only work with ready input values can use a calculation slot; completed outputs are stored.',
      input_state:incoming[i],output_state:outgoing[i],focus:i===0?'input-memory':i===4?'output-memory':'calculation-slots',
      source_indices:[0],claims:[i===3?'real-limits':i===2||i===4?'same-capacity':'ready-input'],
    })),
    questions:[
      {question:'Why do three slots wait in the one-input case?',answer:'Only one ready input is supplied in each declared round. An available slot cannot calculate a job without its required input.',stage:1,part:'calculation-slots'},
      {question:'What changes when four inputs become ready?',answer:'The same four slots can work on four separate ready values in one ideal round. The operation remains input plus one; no new hardware is added.',stage:2,part:'input-memory'},
      {question:'Are these rounds real GPU clock cycles?',answer:'No. The rounds and their playback durations are declared teaching choices. Actual caches, scheduling, overlapping transfers and architecture are outside this toy timing model.',stage:3,part:'output-memory'},
    ],
    prediction:lesson.prediction.prompt,prediction_answer:lesson.prediction.answer,
    teaching:{goal:'Explain why an available calculation slot still needs ready data, and predict whether extra empty slots solve a data-supply limit.',
      misconception:'Available calculation capacity alone guarantees useful parallel work even when required inputs are missing.',
      core:['input-memory','calculation-slots','output-memory'],operation:'sequential',
      operation_note:'The authored model supplies inputs and then calculates each ideal round. Real GPUs can overlap work and memory activity; cue order teaches attention rather than hardware timing.',
      invariants:['Four calculation slots remain available in both conditions.','Each stored result equals its fixed input plus one.',
        'Missing inputs cannot be calculated; all eight identities and inputs remain the same across comparisons.'],claims,
      prediction:{prompt:lesson.prediction.prompt,choices:[...lesson.prediction.choices],correct:1,
        explanation:lesson.prediction.answer,reasoning:['A useful calculation needs its input.','Empty capacity does not supply missing data.'],
        misconception:'Four free slots guarantee four useful calculations without four ready inputs.'},
      transfer:{prompt:lesson.transfer.prompt,choices:[...lesson.transfer.choices],correct:1,
        explanation:lesson.transfer.answer,reasoning:['The data supply remains one input per ideal round.','Extra empty slots do not change this declared supply limit.'],
        misconception:'Adding calculation slots automatically creates ready data.'},
      teach_back:'Point to an idle slot and explain what it still needs before it can calculate a job.',
      teach_back_reasoning:['Identify the required ready input.','Connect that missing input to waiting despite available capacity.'],
      scenarios:[
        {id:'one-ready-input',label:'One input per ideal round',kind:'computed',controls:{supply:'1'},cue_id:ids[1],
          outcome:'At this fixed checkpoint, three results are stored and one slot has a ready job.',
          explanation:'The exact authored model has completed three supply-then-compute rounds. Only one new input is delivered per round; other available slots have no ready job.',claims:['ready-input','same-capacity']},
        {id:'four-ready-inputs',label:'Four inputs per ideal round',kind:'computed',controls:{supply:'4'},cue_id:ids[1],
          outcome:'At the same checkpoint, all eight toy results are stored and the slots are idle.',
          explanation:'Two ideal rounds suffice for eight inputs when four are supplied per round. The completed slots are now idle; this illustrates the declared model, not measured GPU performance.',claims:['ready-input','same-capacity']},
      ]},
    controls:lesson.controls.map(control=>({...control,options:control.options.map(option=>({...option}))})),
    default_controls:{...lesson.defaultControls},actions:lesson.actions.map(action=>({...action,still:action.still??action.start,
      controls:{...action.controls}})),
  };
  return {lesson,metadata};
}
