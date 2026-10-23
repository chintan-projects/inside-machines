/** Authored lesson adapters; the one shared player owns navigation, controls and audio. */
import type { FrameState, Lesson, Narration, NarrationPlan, Source } from '../../../web/studio/contracts.ts';
import { refrigeratorCore, refrigeratorEnergy, refrigeratorPhase } from '../narration.ts';
import { cycleStateAt, energyStateAt, phaseStateAt } from './model.ts';
import { overview } from './artwork.ts';
import { coilSection, compressorSection, capillarySection, energySection, phaseSection } from './sections.ts';
export const sources:readonly Source[]=[
  {title:'GE Appliances: sealed-system operation',url:'https://products.geappliances.com/appliance/gea-support-search-content?contentId=16911',locator:'Steps 1–7: compressor, condenser, capillary, evaporator and sealed return.'},
  {title:'OpenStax College Physics 2e §15.5',url:'https://openstax.org/books/college-physics-2e/pages/15-5-applications-of-thermodynamics-heat-pumps-and-refrigerators',locator:'Opening balance Qh = Qc + W; Air Conditioners and Refrigerators.'},
  {title:'Danfoss: Refrigeration, an introduction to the basics',url:'https://assets.danfoss.com/documents/latest/49699/AX000086437108en-000202.pdf',locator:'§§2.5–2.8 phase change, latent heat, superheat and diagrams; §§3.1–3.6 cooling circuit.'},
];
const scope='Generic vapor-compression refrigerator in an exposed teaching layout. Coils, fans and compressor designs vary. The front and tube sections are drawing cuts, not an open-door experiment or a real refrigerant leak. Thin chevrons mean material direction; broad arrows mean heat/work. Attention order does not turn other jobs off. Defrost, thermostat control, capacity and repair are outside scope. Energy units are an accounting example. Technical, actual-device and beginner acceptance remain pending for R2.';
function base(id:string,title:string,summary:string,plan:NarrationPlan,narrations:Readonly<Record<string,Narration>>) {
  const narration=narrations[plan.id];
  if(narration&&(narration.id!==plan.id||JSON.stringify(narration.cues)!==JSON.stringify(plan.cues)||narration.duration!==plan.duration)) {
    throw new Error('Refrigerator narration does not match the authored cue plan');
  }
  return {id,title,summary,duration:plan.duration,sources,scope,...(narration?{narration}:{})};
}
export function createCore(narrations:Readonly<Record<string,Narration>>={}):Lesson<ReturnType<typeof cycleStateAt>> {
  return {...base('refrigerator-r2-core','How does a refrigerator keep food cold?',
    'Follow heat out of the food cabinet, through a sealed loop and into the kitchen.',refrigeratorCore,narrations),
    defaultControls:{power:'on'},stateAt:cycleStateAt,
    render:s=>s.focus==='inside'?coilSection(s,false):s.focus==='compressor'?compressorSection(s):
      s.focus==='outside'?coilSection(s,true):s.focus==='restrictor'?capillarySection(s):overview(s),
    actions:[{id:'follow-loop',label:'Follow the heat',start:10,end:104,still:27,controls:{power:'on'}},
      {id:'compressor-section',label:'See the moving mechanism',start:34,end:49,still:36.9,controls:{power:'on'}},
      {id:'whole-fridge',label:'Put it all together',start:77,end:104,still:84,controls:{power:'on'}}],
    controls:[{key:'power',label:'Compare sustained pumping',options:[{value:'on',label:'Compressor running'},{value:'off',label:'Compressor stopped'}]}],
    controlsVisible:()=>true,controlValues:s=>({power:s.running?'on':'off'}),
    controlRestart:controls=>({id:'power-comparison',label:'',start:34,end:49,still:36.9,controls}),
    takeawayVisible:s=>s.time>=77,takeaway:'It moves heat. The cold coil takes it in, electrical work keeps the loop going, and the warm coil releases heat into the room.',
    prediction:{prompt:'Could leaving the refrigerator door open cool the whole kitchen?',
      choices:['Yes: cold air would come out','No: the warm side returns heat too'],
      answer:'Both sides now exchange heat with the same room. The warm side returns the heat removed plus electrical work. A cool draft is not whole-room cooling.',
      revealAction:{id:'trace-heat-out',label:'',start:49,end:63,still:55}},
    transfer:{prompt:'Imagine the warm coil could no longer transfer heat to its surroundings. Why would sustained cooling be impaired?',
      choices:['The heat has nowhere to leave the loop','The cold coil could store incoming heat forever'],
      answer:'Incoming heat and work cannot accumulate forever in sustained operation. The warm side needs somewhere to reject them. This is a thought experiment, not an instruction to obstruct a real coil.'},
  };
}
export function createEnergy(narrations:Readonly<Record<string,Narration>>={}):Lesson<ReturnType<typeof energyStateAt>> {
  return {...base('refrigerator-r2-energy','Could an open fridge cool the kitchen?',
    'Count what leaves, what enters and which room receives it.',refrigeratorEnergy,narrations),
    defaultControls:{door:'auto'},stateAt:energyStateAt,render:energySection,
    actions:[{id:'closed-door',label:'Keep cabinet air separate',start:10,end:24,still:17,controls:{door:'closed'}},
      {id:'open-door',label:'Use the same room air',start:24,end:38,still:30,controls:{door:'open'}}],
    controls:[{key:'door',label:'Which air supplies the cold side?',options:[{value:'closed',label:'Cabinet air'},{value:'open',label:'Same room air'}]}],
    controlsVisible:s=>s.time>=10,controlValues:s=>({door:s.open?'open':'closed'}),
    controlRestart:controls=>({id:'door-comparison',label:'',start:24,end:38,still:30,controls}),
    takeawayVisible:s=>s.time>=24,takeaway:'If both sides exchange heat with one room, the work added leaves that room with more energy.',
    prediction:{prompt:'If the door stays open in a closed kitchen, will the whole room cool?',
      choices:['Yes, because cold air comes out','No, the warm side returns heat and added work'],
      answer:'In this example, 3 units leave the room and 4 return. The extra 1 comes from electrical work. A local cool patch is not net cooling.',
      revealAction:{id:'open-balance',label:'',start:24,end:38,still:30,controls:{door:'open'}}},
    transfer:{prompt:'What changes if the warm coil rejects heat outside the kitchen instead?',
      choices:['The kitchen can lose net heat in principle','A heat pump must warm the space it cools'],
      answer:'The kitchen boundary now includes heat removal but excludes heat rejection. In principle this can cool the kitchen; the example does not predict capacity or efficiency.'},
  };
}
export function createPhase(narrations:Readonly<Record<string,Narration>>={}):Lesson<ReturnType<typeof phaseStateAt>> {
  return {...base('refrigerator-r2-phase','How can a cold liquid boil?',
    'Compare the same fluid and cold temperature under two pressures.',refrigeratorPhase,narrations),
    defaultControls:{pressure:'auto'},stateAt:phaseStateAt,render:phaseSection,
    actions:[{id:'lower-pressure',label:'Try lower pressure',start:11,end:24,still:16,controls:{pressure:'lower'}},
      {id:'higher-pressure',label:'Compare higher pressure',start:24,end:37,still:29,controls:{pressure:'higher'}}],
    controls:[{key:'pressure',label:'Same fluid and chosen temperature',options:[{value:'lower',label:'Lower pressure'},{value:'higher',label:'Higher pressure'}]}],
    controlsVisible:()=>true,controlValues:s=>({pressure:s.pressure}),
    controlRestart:controls=>({id:'pressure-comparison',label:'',start:11,end:24,still:16,controls}),
    takeawayVisible:s=>s.time>=24,takeaway:'Boiling depends on fluid and pressure. A cold liquid can boil while taking in heat from warmer cabinet air.',
    prediction:{prompt:'Does boiling always mean a liquid is hot compared with the room?',
      choices:['Yes: boiling always means very hot','No: fluid and pressure set the boiling point'],
      answer:'The chosen cold temperature is at the lower-pressure boiling point and below the higher-pressure one. Cold relative to the room does not rule out boiling.',
      revealAction:{id:'cold-boiling',label:'',start:11,end:24,still:16}},
    transfer:{prompt:'A tube contains only vapor, with no liquid left. Can heat still enter it by evaporating more liquid there?',
      choices:['There is no liquid to evaporate; the vapor can still warm','The gas can keep changing into more gas'],
      answer:'Evaporation needs liquid. Vapor alone cannot absorb heat through that liquid-to-vapor change, though it can still take in heat and warm.'},
  };
}
export function createRefrigeratorR2Lessons(narrations:Readonly<Record<string,Narration>>={}):readonly Lesson<FrameState>[] {
  return [createCore(narrations),createEnergy(narrations),createPhase(narrations)];
}
