/** Data-only semantic contract derived from the actual native lessons/cue plans. */
import type { FrameState, Lesson, Narration, NarrationPlan } from '../../../web/studio/contracts.ts';
import type { NativeSpec, NativeStage, NativeComponent, NativeScenario } from '../../../web/studio/native-contracts.ts';
import type { Claim, Assessment } from '../../../web/teaching/contracts.ts';
import { refrigeratorCore, refrigeratorEnergy, refrigeratorPhase } from '../narration.ts';
import { createRefrigeratorR2Lessons } from './lessons.ts';

const components:NativeComponent[]=[
  {id:'cold-coil',name:'Evaporator',label:'Cold coil',description:'The colder inside passage receives heat through its metal wall; refrigerant evaporates.'},
  {id:'compressor',name:'Compressor',label:'Compressor',description:'Motor work drives vapor from the low-pressure side toward the high-pressure side.'},
  {id:'warm-coil',name:'Condenser',label:'Warm coil',description:'Hotter refrigerant releases heat into the kitchen and condenses.'},
  {id:'capillary',name:'Capillary',label:'Narrow tube',description:'A restricted passage connects high-pressure liquid to the low-pressure side.'},
  {id:'cabinet',name:'Insulated cabinet',label:'Insulated cabinet',description:'Insulation slows heat returning from warmer surroundings; it does not remove heat.'},
  {id:'electrical-input',name:'Electrical input',label:'Electrical work',description:'Electrical work powers compression and ultimately adds to the rejected heat.'},
];
const claims:Claim[]=[
  {id:'r1',statement:'A refrigerator moves heat from its cabinet to its surroundings through a sealed vapor-compression circuit.',source:0,locator:'Sealed-system operation, steps 1–7',scope:'generic',limitation:'Generic exposed layout. Coils, fans and compressors vary; this is not a particular model or repair guide.'},
  {id:'r2',statement:'Heat enters colder refrigerant through the evaporator wall, and liquid evaporation takes in energy.',source:2,locator:'§§2.5–2.6 and §3.1',scope:'generic',limitation:'Phase regions are illustrative. A real evaporator may also warm vapor; bubble kinetics and temperatures are not simulated.'},
  {id:'r3',statement:'Compressor work raises vapor pressure and temperature so the outside coil can reject heat and condense vapor.',source:0,locator:'Steps 1–3',scope:'generic',limitation:'The piston is one possible design. Valve timing is qualitative, not derived from pressure or a compressor performance model.'},
  {id:'r4',statement:'The heat released equals the heat removed plus work added, for the declared steady energy balance.',source:1,locator:'§15.5 opening heat-pump balance Qh = Qc + W',scope:'generic',limitation:'The 3+1=4 units are an accounting example, not measured performance, watts, temperature or a predicted efficiency.'},
  {id:'r5',statement:'If both sides exchange heat with the same room, added work gives that room a net energy gain.',source:1,locator:'Inference from §15.5 balance, with the same room supplying both sides',scope:'inference',limitation:'A cool local draft is possible. Fixed example values omit altered load, transients, passive leakage and thermostat control.'},
  {id:'r6',statement:'The capillary restricts flow between high and low sides; some liquid flashes as pressure falls.',source:2,locator:'§§3.5–3.6; GE source steps 5–6 for the refrigerator capillary',scope:'generic',limitation:'Throttling is a qualitative change; no heat transfer, real dimensions or refrigerant-state calculation is assigned to this tube.'},
  {id:'r7',statement:'Boiling temperature depends on fluid and pressure; a cold liquid can boil while taking in heat.',source:2,locator:'§§2.5–2.8 and §3.1',scope:'generic',limitation:'The chosen temperature is assumed at the lower-pressure boiling point and below the higher-pressure one. No numerical pressures or transient are invented.'},
];
interface CueSemantics {title:string;focus:string;parts:string[];input:string;output:string;cause:string;claims:string[];kind:'orientation'|'causal'|'recombine'}
const coreCues:CueSemantics[]=[
  {title:'Move heat, do not erase it',focus:'cabinet',parts:['cabinet','cold-coil','warm-coil','compressor'],input:'Food cabinet contains heat; kitchen is warmer.',output:'A closed loop carries heat from the cabinet to the kitchen.',cause:'Colder and warmer parts exchange heat with different surroundings while electrical work drives the loop.',claims:['r1','r4'],kind:'orientation'},
  {title:'Heat crosses a real wall',focus:'cold-coil',parts:['cold-coil','cabinet'],input:'Cabinet air is warmer than fluid inside the sealed tube.',output:'Energy crosses the metal wall into the refrigerant.',cause:'The temperature difference drives heat through the wall; cabinet air never becomes refrigerant.',claims:['r2'],kind:'causal'},
  {title:'Cold liquid becomes vapor',focus:'cold-coil',parts:['cold-coil'],input:'Low-pressure cold liquid receives heat through the tube wall.',output:'Some liquid becomes vapor carrying energy away.',cause:'Liquid-to-vapor change takes in energy; low pressure permits boiling at a cold temperature.',claims:['r2','r7'],kind:'causal'},
  {title:'Work squeezes the vapor',focus:'compressor',parts:['compressor','electrical-input'],input:'Lower-pressure vapor and electrical work enter the compressor.',output:'Higher-pressure, hotter vapor leaves for the outside coil.',cause:'The motor turns a crank, its fixed-length rod moves a piston, and valves admit then discharge vapor.',claims:['r3'],kind:'causal'},
  {title:'Heat leaves into the kitchen',focus:'warm-coil',parts:['warm-coil'],input:'Hotter vapor enters a coil surrounded by cooler kitchen air.',output:'Heat leaves through metal and vapor condenses into liquid.',cause:'The vapor is now hotter than its surroundings; heat can flow outward.',claims:['r3','r4'],kind:'causal'},
  {title:'Restore the low-pressure side',focus:'capillary',parts:['capillary','cold-coil'],input:'Higher-pressure liquid reaches a narrow passage.',output:'A colder liquid-vapor mixture returns to the low-pressure coil.',cause:'Restricted flow sustains a pressure drop; some liquid flashes using energy from the fluid.',claims:['r6'],kind:'causal'},
  {title:'Four jobs, one running loop',focus:'cold-coil',parts:['cold-coil','compressor','warm-coil','capillary','electrical-input'],input:'Heat enters the cold side and work enters compression.',output:'Heat leaves the warm side and refrigerant returns through the narrow tube.',cause:'The narration changes attention; the connected parts perform these jobs together while the compressor runs.',claims:['r1','r4'],kind:'recombine'},
  {title:'Keep the heat outside',focus:'cabinet',parts:['cabinet','electrical-input','warm-coil'],input:'Warmer surroundings keep returning heat through the cabinet walls.',output:'Insulation slows entry; the powered loop removes heat and rejects heat plus work.',cause:'Insulation reduces heat leakage but cannot pump it away. Sustained cooling needs heat rejection.',claims:['r1','r4'],kind:'recombine'},
];
const energyCues:CueSemantics[]=[
  {title:'Choose the boundary',focus:'cabinet',parts:['cabinet','warm-coil','cooling-loop'],input:'Cabinet air supplies the cold side; kitchen receives the warm-side heat.',output:'The two spaces exchange different amounts of energy through a powered loop.',cause:'The boundary identifies which place loses heat and which receives it.',claims:['r4'],kind:'orientation'},
  {title:'Count every input',focus:'cooling-loop',parts:['cabinet','warm-coil','electrical-input','cooling-loop'],input:'The example removes 3 units and adds 1 unit of work.',output:'4 units leave the warm side.',cause:'Energy accounting requires rejected heat to include heat removed plus work.',claims:['r4'],kind:'causal'},
  {title:'Open the boundary in the model',focus:'cabinet',parts:['cabinet','warm-coil','cooling-loop'],input:'Both sides now exchange heat with one room.',output:'4 returned minus 3 removed leaves 1 unit added to the room.',cause:'The heat source and sink are now the same reservoir, so the work is the net addition.',claims:['r5'],kind:'causal'},
  {title:'Trace the extra energy',focus:'electrical-input',parts:['electrical-input','cooling-loop','warm-coil'],input:'Electrical work continues to enter the loop.',output:'The room gains energy even if a patch near the door feels cool.',cause:'A local cool draft and net whole-room cooling describe different boundaries.',claims:['r4','r5'],kind:'recombine'},
  {title:'Put the boundary back',focus:'cabinet',parts:['cabinet','warm-coil','electrical-input'],input:'A closed cabinet is separated from the surrounding kitchen.',output:'The cabinet can remain cooler while the kitchen receives heat plus work.',cause:'The powered loop transports energy across the cabinet boundary; the fixed units explain accounting only.',claims:['r4','r5'],kind:'recombine'},
];
const phaseCues:CueSemantics[]=[
  {title:'Must boiling mean hot?',focus:'cold-coil',parts:['cold-coil'],input:'A cold liquid sits in a sealed coil surrounded by warmer cabinet air.',output:'The opening view asks whether this liquid could boil.',cause:'The result is concealed until playback or choosing a pressure case.',claims:['r7'],kind:'orientation'},
  {title:'Boil at a cold temperature',focus:'cold-coil',parts:['cold-coil'],input:'The chosen fluid is at its lower-pressure boiling temperature and receives heat.',output:'Liquid becomes vapor while carrying energy away.',cause:'Low pressure lowers this fluid’s boiling temperature; entering heat supplies phase-change energy.',claims:['r2','r7'],kind:'causal'},
  {title:'Change the assumed pressure',focus:'cold-coil',parts:['cold-coil'],input:'The same fluid and temperature are compared at higher pressure.',output:'The fluid remains liquid; heat can still enter and warm it.',cause:'The chosen temperature is below the higher-pressure boiling point. No boiling does not mean no heat transfer.',claims:['r7'],kind:'causal'},
  {title:'Know the model’s limit',focus:'cold-coil',parts:['cold-coil'],input:'Two assumed conditions have been compared.',output:'No pressure-change transient or real boiling temperature is predicted.',cause:'The qualitative comparison isolates fluid, pressure and phase rather than simulating an appliance.',claims:['r7'],kind:'recombine'},
  {title:'Return to the cooling loop',focus:'cold-coil',parts:['cold-coil'],input:'Heat may enter liquid without phase change, or enter vapor and warm it.',output:'Boiling is one route for heat absorption; the full loop keeps restoring its conditions.',cause:'Phase change needs remaining liquid. Heating vapor cannot evaporate liquid that is no longer present.',claims:['r2','r7'],kind:'recombine'},
];
function stages(plan:NarrationPlan,semantics:readonly CueSemantics[]):NativeStage[] {
  if(plan.cues.length!==semantics.length)throw new Error('Refrigerator cue semantics do not match the authored narration');
  return plan.cues.map((cue,i)=>{
    const info=semantics[i]!;
    return {id:plan.id+'-'+cue.start,kind:info.kind,start:cue.start,end:cue.end,still:cue.still,
      title:info.title,explanation:cue.text,narration:cue.text,duration:cue.end-cue.start,
      parts:info.parts,focus:info.focus,input_state:info.input,output_state:info.output,cause:info.cause,
      claims:info.claims,source_indices:[...new Set(claims.filter(claim=>info.claims.includes(claim.id)).map(claim=>claim.source))]};
  });
}
const plans=[refrigeratorCore,refrigeratorEnergy,refrigeratorPhase];
const semantics=[coreCues,energyCues,phaseCues];
const goals=[
  'Trace cabinet heat, compressor work and warm-side rejection through the sealed loop; explain why both sides in one room do not cool that room.',
  'Use a declared energy balance and the room boundary to reason about an open refrigerator.',
  'Explain cold boiling with fluid and pressure, and distinguish no boiling from no heat transfer.',
];
const teachBack=[
  ['Explain where heat from the food goes. What does electricity add, and why is the back warm?',
    ['Heat crosses from cabinet air into colder refrigerant.','Compressor work maintains the loop and adds energy.','The warm side releases heat removed plus work into the room.']],
  ['Why can an open refrigerator feel cold nearby while adding net energy to the kitchen?',
    ['Both sides exchange energy with the same room.','Heat released includes heat removed plus electrical work.','The work is the net addition; a local cool patch is not whole-room cooling.']],
  ['How could a liquid boil while colder than the room, and can heat enter without boiling?',
    ['Boiling temperature depends on fluid and pressure.','At the assumed lower pressure the cold liquid can boil as heat enters.','At higher pressure it can remain liquid and warm; vapor can warm too.']],
] as const;
const reasoning=[
  [['Same room supplies and receives heat.','The warm side also releases the work added.'],['Sustained operation cannot store incoming heat and work forever.','The warm side needs a heat sink.']],
  [['3 units removed and 4 returned is a net gain of 1.','Work accounts for the difference.'],['Rejecting heat outside changes the kitchen boundary.','Cooling in principle does not establish real capacity.']],
  [['Fluid and pressure determine a boiling point.','Cold relative to a room does not prevent boiling.'],['Evaporation requires liquid.','Vapor can still absorb heat and warm.']],
];
function assessment(lesson:Lesson<FrameState>,index:number,transfer:boolean):Assessment {
  const question=transfer?lesson.transfer:lesson.prediction;
  return {prompt:question.prompt,choices:[...question.choices],correct:transfer?0:1,
    explanation:question.answer,reasoning:[...reasoning[index]![transfer?1:0]!],
    misconception:index===2?'Boiling always means hot, or no boiling means no heat transfer.':
      'Cold felt in one place means the whole surrounding room loses heat.'};
}
function scenarios(index:number):NativeScenario[] {
  if(index===0)return [
    {id:'running-compressor',label:'Compressor running',kind:'qualitative',controls:{power:'on'},cue_id:refrigeratorCore.id+'-34',outcome:'Crank and piston move; inlet and outlet open in separate parts of the cycle.',explanation:'Motor work drives the fixed-length rod and piston; valve timing is illustrative.',claims:['r3']},
    {id:'stopped-compressor',label:'Compressor stopped',kind:'qualitative',controls:{power:'off'},cue_id:refrigeratorCore.id+'-34',outcome:'The mechanism stays still and sustained pumping stops.',explanation:'Remaining cold fluid could absorb heat briefly; this steady comparison omits that transient.',claims:['r1','r3']},
  ];
  if(index===1)return [
    {id:'separate-cabinet',label:'Cabinet air',kind:'computed',controls:{door:'closed'},cue_id:refrigeratorEnergy.id+'-24',outcome:'3 removed from cabinet, 1 work added, 4 released to kitchen.',explanation:'The 3+1=4 balance is illustrative accounting, not measured performance.',claims:['r4']},
    {id:'same-room',label:'Same room air',kind:'computed',controls:{door:'open'},cue_id:refrigeratorEnergy.id+'-24',outcome:'4 returned − 3 removed = 1 added to the same room.',explanation:'Both sides now exchange with one reservoir; the work is the net addition.',claims:['r4','r5']},
  ];
  return [
    {id:'low-pressure',label:'Lower pressure',kind:'qualitative',controls:{pressure:'lower'},cue_id:refrigeratorPhase.id+'-11',outcome:'Liquid can boil at the chosen cold temperature while heat enters.',explanation:'The temperature is assumed at this fluid’s lower-pressure boiling point.',claims:['r7']},
    {id:'high-pressure',label:'Higher pressure',kind:'qualitative',controls:{pressure:'higher'},cue_id:refrigeratorPhase.id+'-11',outcome:'Liquid remains liquid at the same chosen temperature and can still take in heat.',explanation:'The chosen temperature is below the higher-pressure boiling point. This is not a pressure transient.',claims:['r7']},
  ];
}
function specification(lesson:Lesson<FrameState>,index:number):NativeSpec {
  const nodeComponents=index===1?[
    {id:'cabinet',name:'Cold-side reservoir',label:'Cold side',description:'Cabinet air supplies the cold side, or the same room supplies it in the open-door comparison.'},
    {id:'warm-coil',name:'Warm-side reservoir',label:'Room · warm side',description:'Kitchen air receives rejected heat from the warm side.'},
    components.find(component=>component.id==='electrical-input')!,
    {id:'cooling-loop',name:'Cooling loop',label:'Cooling loop',description:'The powered cycle receives removed heat and work, then rejects their sum.'},
  ]:index===2?[components[0]!,
    {id:'tube-wall',name:'Metal tube wall',label:'Metal wall',description:'The solid metal separates warmer cabinet air from sealed refrigerant and conducts heat into it.'},
    {id:'cabinet-air',name:'Cabinet air',label:'Cabinet air',description:'Warmer surrounding air supplies heat through the tube wall while remaining outside the sealed passage.'},
  ]:components;
  const authoredStages=stages(plans[index]!,semantics[index]!);
  const referencedClaims=new Set(authoredStages.flatMap(stage=>stage.claims));
  const prediction=assessment(lesson,index,false),transfer=assessment(lesson,index,true);
  return {version:3,spec_version:'native-studio-1',renderer:{id:'refrigerator-native-r2',fingerprint:''},
    title:lesson.title,canonical:lesson.id,aliases:index===0?['fridge','refrigerator','how does a fridge work']:
      index===1?['fridge energy balance','why is the back of the fridge warm']:['cold boiling','refrigerator phase change'],
    family:'vapor-compression',question:lesson.title,summary:lesson.summary,big_idea:lesson.takeaway,
    category:'Kitchen',accent:'#286c93',
    assumptions:[lesson.scope],sources:lesson.sources.map(source=>({title:source.title,url:source.url,supports:source.locator})),
    components:nodeComponents.map(component=>({...component})),stages:authoredStages,
    controls:[...lesson.controls],default_controls:lesson.defaultControls,actions:[...lesson.actions],
    prediction:prediction.prompt,prediction_answer:prediction.explanation,
    questions:[{question:lesson.prediction.prompt,answer:lesson.prediction.answer,stage:0,part:nodeComponents[0]!.id},
      {question:lesson.transfer.prompt,answer:lesson.transfer.answer,stage:authoredStages.length-1,part:nodeComponents[0]!.id},
      {question:'What is this model leaving out?',answer:lesson.scope,stage:authoredStages.length-1,part:nodeComponents[0]!.id}],
    teaching:{goal:goals[index]!,misconception:prediction.misconception,core:nodeComponents.map(component=>component.id),
      operation:index===0?'simultaneous':'controlled',operation_note:index===0?
        'The stages direct attention to connected jobs that happen together while pumping runs.':'Controls compare explicitly assumed cases; they do not simulate a physical transient.',
      invariants:['Refrigerant remains separate from surrounding air.','Labels and captions describe the same versioned state as the mechanism.',
        'Energy released includes removed heat plus work; no units imply measured performance.'],
      claims:claims.filter(claim=>referencedClaims.has(claim.id)).map(claim=>({...claim})),prediction,transfer,
      teach_back:teachBack[index]![0],teach_back_reasoning:[...teachBack[index]![1]],scenarios:scenarios(index)},
  };
}
export function refrigeratorR2Definitions(narrations:Readonly<Record<string,Narration>>={}):readonly {lesson:Lesson<FrameState>;spec:NativeSpec}[] {
  return createRefrigeratorR2Lessons(narrations).map((lesson,index)=>({lesson,spec:specification(lesson,index)}));
}
export const refrigeratorR2Metadata=refrigeratorR2Definitions().map(definition=>definition.spec);
