/** Reviewed-scope content for three nodes; shared player owns all UI and audio behavior. */
import type { FrameState, Lesson, Narration } from '../visual-studio/contracts.ts';
import { cycleStateAt, energyStateAt, phaseStateAt } from './model.ts';
import { cycleRenderer, energyScene, phaseScene, type RefrigeratorArt } from './scenes.ts';
const sources = [
  { title: 'GE Appliances: sealed-system operation', url: 'https://products.geappliances.com/appliance/gea-support-search-content?contentId=16911',
    locator: 'Steps 1–7: compression, heat rejection, capillary, evaporation and return. R1–R3.' },
  { title: 'OpenStax College Physics 2e §15.5', url: 'https://openstax.org/books/college-physics-2e/pages/15-5-applications-of-thermodynamics-heat-pumps-and-refrigerators',
    locator: 'Opening energy balance Qh = Qc + W; Air Conditioners and Refrigerators. R4; same-room result R5 is an inference.' },
  { title: 'Danfoss: Refrigeration, an introduction to the basics', url: 'https://assets.danfoss.com/documents/latest/49699/AX000086437108en-000202.pdf',
    locator: '§2.6 latent heat; §2.7 vapor warming; §2.8 pressure/boiling diagram; §§3.1–3.6 circuit; §6.3 capillary. R2/R3/R6/R7; not one particular appliance.' },
];
const scope = 'Generic vapor-compression cooling loop with exposed teaching layout; real coils, fans and compressors vary. Refrigerant stays in sealed tubes. The cutaway opening is a drawing aid. Heat and refrigerant arrows have different shapes. Attention order does not turn other components off. Defrost/control-system design and repair are outside scope. Numerical energy units are a declared example, not temperature, watts or measured performance. Local draft; independent technical, actual-phone and beginner review remain pending.';
function base<T extends FrameState>(id: string, title: string, summary: string, narration: Narration): Pick<Lesson<T>,
  'id' | 'title' | 'summary' | 'duration' | 'narration' | 'sources' | 'scope'> {
  return { id, title, summary, duration: narration.duration, narration, sources, scope };
}
export function coreLesson(art: RefrigeratorArt, narration: Narration): Lesson<ReturnType<typeof cycleStateAt>> {
  return { ...base('refrigerator-r1-core','How does a refrigerator keep food cold?','Follow heat from the cabinet into the kitchen.',narration),
    defaultControls: { power:'on' }, stateAt:cycleStateAt, render:cycleRenderer(art),
    actions:[
      {id:'follow-loop',label:'Follow the cooling loop',start:10,end:104,still:27,controls:{power:'on'}},
      {id:'inside-compressor',label:'Look inside the compressor',start:34,end:49,still:36.9,controls:{power:'on'}},
      {id:'whole-fridge',label:'Return to the whole fridge',start:77,end:104,still:84},
    ],
    controls:[{key:'power',label:'Compressor · steady comparison',options:[{value:'on',label:'Running'},{value:'off',label:'Stopped'}]}],
    controlsVisible:()=>true, controlValues:s=>({power:s.running?'on':'off'}),
    controlRestart:controls=>({id:'power-comparison',label:'',start:34,end:49,still:36.9,controls}),
    takeawayVisible:s=>s.time>=77, takeaway:'Cold inside, warm outside: the refrigerator transports heat, and electrical work keeps that process going.',
    prediction:{prompt:'Could leaving the refrigerator door open cool the whole kitchen?',
      choices:['Yes: cold air would come out','No: its warm side also releases heat'],
      answer:'Both sides now exchange heat with the same room. The warm side returns the heat removed plus added electrical work, so this does not cool the whole kitchen.',
      revealAction:{id:'where-heat-goes',label:'',start:49,end:63,still:55}},
    transfer:{prompt:'Imagine the outside coil could no longer pass heat to its surroundings. Why would sustained cooling be impaired?',
      choices:['The heat has nowhere to leave the cycle','The cold coil could simply store heat forever'],
      answer:'Sustained operation requires heat rejection. The loop cannot keep storing incoming heat and work indefinitely. This is a thought experiment, not an instruction to cover a real coil.'},
  };
}
export function energyLesson(narration: Narration): Lesson<ReturnType<typeof energyStateAt>> {
  return { ...base('refrigerator-r1-energy','Could an open fridge cool the kitchen?','Keep track of heat removed, work added and heat released.',narration),
    defaultControls:{door:'auto'}, stateAt:energyStateAt, render:energyScene,
    actions:[{id:'closed-door',label:'Keep the cabinet separate',start:10,end:24,still:17,controls:{door:'closed'}},
      {id:'open-door',label:'Open the door in the model',start:24,end:38,still:30,controls:{door:'open'}}],
    controls:[{key:'door',label:'Which air supplies the cold side?',options:[{value:'closed',label:'Cabinet air'},{value:'open',label:'Same room air'}]}],
    controlsVisible:s=>s.time>=10,controlValues:s=>({door:s.open?'open':'closed'}),
    controlRestart:controls=>({id:'door-comparison',label:'',start:24,end:38,still:30,controls}),
    takeawayVisible:s=>s.time>=24,takeaway:'When both sides exchange heat with the same room, the added work leaves the room with a net energy gain.',
    prediction:{prompt:'If you leave the door open in a closed kitchen, will the whole room be cooled?',
      choices:['Yes, because cold air comes out','No, the warm side also returns heat and added work'],
      answer:'In the example, 3 units are removed but 4 are released into the same room. The extra 1 comes from work. A local cool draft is not net room cooling.',
      revealAction:{id:'show-open-balance',label:'',start:24,end:38,still:30,controls:{door:'open'}}},
    transfer:{prompt:'Suppose the hot coil were placed outside the kitchen while the cold side drew heat from kitchen air. Could that arrangement cool the kitchen?',
      choices:['In principle yes: heat is released outside that room','No: every heat pump must warm the space it cools'],
      answer:'Yes in principle. The warm side now rejects heat and work outside the kitchen boundary. That is the relevant difference; this does not predict real appliance capacity or efficiency.'},
  };
}
export function phaseLesson(narration: Narration): Lesson<ReturnType<typeof phaseStateAt>> {
  return { ...base('refrigerator-r1-phase','How can a cold liquid boil?','Explore pressure and phase change without invented temperature readings.',narration),
    defaultControls:{pressure:'auto'}, stateAt:phaseStateAt,render:phaseScene,
    actions:[{id:'lower-pressure',label:'See the lower-pressure case',start:11,end:24,still:16,controls:{pressure:'lower'}},
      {id:'higher-pressure',label:'Compare higher pressure',start:24,end:37,still:29,controls:{pressure:'higher'}}],
    controls:[{key:'pressure',label:'Same fluid and chosen temperature',options:[{value:'lower',label:'Lower pressure'},{value:'higher',label:'Higher pressure'}]}],
    controlsVisible:()=>true,controlValues:s=>({pressure:s.pressure}),
    controlRestart:controls=>({id:'pressure-comparison',label:'',start:11,end:24,still:16,controls}),
    takeawayVisible:s=>s.time>=24,takeaway:'A cold liquid can boil when its boiling point is low enough. Taking in heat during phase change helps carry energy out of the cabinet.',
    prediction:{prompt:'Does boiling always require a fluid to be hot compared with the room?',
      choices:['Yes, boiling always means very hot','No, it depends on the fluid and its pressure'],
      answer:'Boiling depends on both the fluid and pressure. Our chosen cold temperature is at the lower-pressure boiling point and below the higher-pressure one.',
      revealAction:{id:'reveal-cold-boiling',label:'',start:11,end:24,still:16}},
    transfer:{prompt:'A different part of a cooling tube contains only vapor, with no liquid left. Can it still absorb heat by evaporating liquid there?',
      choices:['No liquid remains to evaporate; the vapor can still warm','Yes, the gas can keep turning into more gas'],
      answer:'Evaporation needs liquid. Vapor alone cannot keep absorbing energy through that liquid-to-vapor change, although it may still take in heat and warm. A real evaporator can include a vapor-warming region.'},
  };
}
