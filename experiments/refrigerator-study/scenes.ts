/** Trusted artwork adapters. All causal decisions and energy arithmetic come from model.ts. */
import type { Scene } from '../visual-studio/contracts.ts';
import { escape } from '../visual-studio/drawing.ts';
import type { ArtPose, CycleState, EnergyState, PhaseState } from './model.ts';
export interface RefrigeratorArt {
  overview(pose: ArtPose): Pick<Scene, 'svg' | 'labels' | 'caption' | 'alt'>;
}
const cold = '#22668e', hot = '#9e4a21', ink = '#182431';
const label = (x: number, y: number, value: string | number, size = 28, color = ink): string =>
  '<text x="'+x+'" y="'+y+'" text-anchor="middle" font-family="system-ui,sans-serif" font-size="'+size+'" fill="'+color+'">'+escape(value)+'</text>';
const rect = (x: number, y: number, w: number, h: number, color: string, stroke = '#9caab7', r = 12): string =>
  '<rect x="'+x+'" y="'+y+'" width="'+w+'" height="'+h+'" rx="'+r+'" fill="'+color+'" stroke="'+stroke+'" stroke-width="2"/>';
const line = (d: string, color: string, width = 4, extra = ''): string =>
  '<path d="'+d+'" stroke="'+color+'" stroke-width="'+width+'" fill="none" stroke-linecap="round" stroke-linejoin="round" '+extra+'/>';
function plate(svg: string, caption: string, alt: string, key: string): Scene {
  return { svg, labels: [], caption, alt, contentKey: key, viewport: { x: 0, y: 0, width: 720, height: 620 } };
}
const defs = (id: string): string => '<defs><linearGradient id="'+id+'-metal" x2="0" y2="1"><stop stop-color="#d3dce4"/><stop offset=".45" stop-color="#f8fafc"/><stop offset="1" stop-color="#97a8b7"/></linearGradient><marker id="'+id+'-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="context-stroke"/></marker></defs>';
const arrow = (d: string, color: string, id: string, width = 4): string => line(d,color,width,'marker-end="url(#'+id+'-arrow)"');

/** Own working passage and surroundings: never a crop at whole-machine coordinates. */
function coilSection(s: CycleState, warm: boolean): Scene {
  const id = warm ? 'fridge-warm' : 'fridge-cold', color = warm ? hot : cold;
  let svg = defs(id) + rect(48,92,624,426,warm?'#fff4e9':'#edf5fc','#c5d0da',18) +
    label(360,64,warm?'Outside coil · condenser':'Inside coil · evaporator',32) +
    label(360,142,warm?'Kitchen air':'Cabinet air',30) +
    rect(90,228,540,146,'url(#'+id+'-metal)','#72899b',35) +
    rect(106,249,508,104,'#e7f2fb',color,22);
  // The region/phase indication is illustrative, not a simulated liquid interface.
  svg += rect(warm?392:114,284,warm?210:208,60,'#79b6d8',color,8);
  for (const x of warm ? [150,210,275,330] : [355,410,465,535]) {
    svg += '<ellipse cx="'+x+'" cy="278" rx="17" ry="13" fill="#fff" stroke="'+color+'" stroke-width="2"/>';
  }
  svg += arrow('M138 303H575',color,id) +
    label(170,425,warm?'Vapor in':'Liquid in',28,color) +
    label(548,425,warm?'Liquid out':'Vapor out',28,color) +
    label(360,488,'Refrigerant stays inside the tube',28);
  const heatPath = warm ? 'M355 260C325 235 388 218 355 190L355 170' : 'M355 170C325 195 388 212 355 240L355 267';
  svg += arrow(heatPath,hot,id,7) + label(535,195,warm?'Heat out':'Heat in',28,hot);
  svg += '<g data-fluid-cue transform="translate(0 0)"><path d="M151 318l13 8-13 8" fill="none" stroke="'+color+'" stroke-width="4"/></g>';
  const result = plate(svg,
    (warm ? 'Hot vapor gives heat to cooler room air and condenses. ' : 'The warmer cabinet gives heat through the tube wall to colder, low-pressure refrigerant. ') +
    'Illustrative passage/phase regions, not bubble kinetics or measured flow. Broad arrows mean heat; thin arrows mean refrigerant direction.',
    (warm ? 'A metal outside-coil section: vapor enters left, liquid leaves right, heat goes through the wall into kitchen air.'
      : 'An internal-coil section in cabinet air: liquid enters, mixed liquid and vapor fill the passage, vapor leaves; heat enters through the tube wall.'),id+'-'+s.running);
  return { ...result, attributes: [{ selector:'[data-fluid-cue]',name:'transform',value:'translate('+(s.running?s.progress*370:0)+' 0)' }] };
}
/** A physically constrained crank/rod/piston example, with inlet/outlet and motor context. */
function compressorSection(s: CycleState): Scene {
  const id='fridge-compressor', pin=s.pistonPinY, top=pin-15, gasHeight=top-148;
  const stage=!s.running?'Stopped':s.intakeOpen?'Draw vapor in':s.outletOpen?'Discharge vapor':'Squeeze trapped vapor';
  const angle=Math.atan2(-(s.crankX-360),s.crankY-pin)*180/Math.PI;
  let svg=defs(id)+label(360,45,'Inside one compressor design',32)+
    rect(198,112,324,420,'#e7edf2','#65798d',32)+rect(230,145,260,238,'#fff','#65798d',4)+
    '<g data-gas transform="scale(1 1)">'+rect(241,148,238,200,'#f7e4d6','#c7a58d',0)+'</g>'+
    rect(210,384,300,150,'#cbd6df','#65798d',16)+
    '<circle cx="360" cy="460" r="58" fill="url(#'+id+'-metal)" stroke="#65798d" stroke-width="3"/>'+
    '<g data-crank><path d="M360 460V410" stroke="#596e80" stroke-width="15" stroke-linecap="round"/></g>'+
    '<g data-rod><path d="M0 0V150" stroke="#798c9c" stroke-width="17" stroke-linecap="round"/><path d="M0 0V150" stroke="#d9e2e9" stroke-width="7"/></g>'+
    '<g data-piston>'+rect(230,-15,260,30,'url(#'+id+'-metal)','#4d6479',3)+label(420,8,'Piston',28)+
    '<circle cx="360" cy="0" r="7" fill="#506c82"/></g>'+
    '<circle data-crank-pin r="8" fill="#52697b" stroke="#fff" stroke-width="2"/>'+
    rect(90,165,146,44,'#e2f0fa',cold,5)+rect(484,165,146,44,'#f8e7da',hot,5)+
    '<g data-intake>'+line('M239 164V204','#456b84',6)+'</g>'+
    '<g data-outlet>'+line('M482 164V204','#906347',6)+'</g>'+
    label(132,114,'Vapor in',28,cold)+label(588,114,'Vapor out',28,hot)+
    label(360,584,stage,30)+label(570,485,'Motor',28)+line('M520 480H495','#65798d',2);
  if(s.running&&s.intakeOpen)svg+=arrow('M110 187H280',cold,id);
  if(s.running&&s.outletOpen)svg+=arrow('M440 187H610',hot,id);
  const result=plate(svg,
    'One reciprocating-compressor design; real refrigerator compressors vary. Rod length stays fixed as the crank moves the piston. Valves are a qualitative timing illustration, not a pressure simulation. Motor work drives the cycle.',
    'A sectioned cylinder with gas above a labeled moving piston, a fixed-length connecting rod and motor crank below. '+stage+'.',
    id+'-'+stage);
  return { ...result, attributes: [
    {selector:'[data-piston]',name:'transform',value:'translate(0 '+pin+')'},
    {selector:'[data-gas]',name:'transform',value:'translate(0 148)scale(1 '+gasHeight/200+')translate(0 -148)'},
    {selector:'[data-crank]',name:'transform',value:'rotate('+(s.running?s.progress*360:90)+' 360 460)'},
    {selector:'[data-rod]',name:'transform',value:'translate(360 '+pin+')rotate('+angle+')'},
    {selector:'[data-crank-pin]',name:'transform',value:'translate('+s.crankX+' '+s.crankY+')'},
    {selector:'[data-intake]',name:'transform',value:'rotate('+(s.intakeOpen?35:0)+' 239 164)'},
    {selector:'[data-outlet]',name:'transform',value:'rotate('+(s.outletOpen?-35:0)+' 482 164)'},
  ] };
}
function restrictorSection(): Scene {
  const id='fridge-capillary';
  return plate(defs(id)+label(360,60,'The narrow tube · capillary',32)+
    rect(36,125,648,372,'#f1f5f8','#c7d0db',18)+label(176,175,'High-pressure side',28,hot)+label(540,175,'Low-pressure side',28,cold)+
    rect(76,242,150,100,'#e8cbb2',hot,14)+rect(226,280,262,24,'#cbd8e1','#607789',4)+
    rect(488,242,156,100,'#deeffb',cold,14)+arrow('M100 292H615',cold,id)+
    '<circle cx="545" cy="270" r="12" fill="white" stroke="'+cold+'"/><circle cx="588" cy="308" r="16" fill="white" stroke="'+cold+'"/>'+
    label(150,402,'Liquid',28,hot)+label(540,402,'Liquid + vapor',28,cold)+label(360,465,'Restricted flow sustains a pressure drop',28),
    'Enlarged schematic passage, not real pipe proportions. Throttling lowers pressure; some liquid flashes using its own energy, leaving a colder mixture. Heat is absorbed from the cabinet farther along the evaporator.',
    'A thick-walled narrow tube connects a high-pressure liquid passage to a low-pressure mixed liquid/vapor passage. Flow direction is left to right.',id);
}
export function cycleRenderer(art: RefrigeratorArt): (s: CycleState) => Scene {
  const cache=new Map<string,Scene>();
  return s=>{
    if(s.focus==='inside')return coilSection(s,false);
    if(s.focus==='compressor')return compressorSection(s);
    if(s.focus==='outside')return coilSection(s,true);
    if(s.focus==='restrictor')return restrictorSection();
    const key='fridge-overview-'+s.focus+'-'+s.running;
    let scene=cache.get(key);
    if(!scene){scene={...art.overview(s),contentKey:key};cache.set(key,scene);}
    return scene;
  };
}
/** The same declared balance drives every readout; the renderer performs no energy arithmetic. */
export function energyScene(s: EnergyState): Scene {
  const id='fridge-energy',b=s.balance;
  let svg=defs(id)+label(360,50,s.open?'One room supplies AND receives heat':'Keep the cabinet and room separate',30)+
    rect(38,100,644,426,s.open?'#fff4e9':'#f1f5f8','#aab8c4',20)+
    rect(65,135,260,222,'#e5f1fb',cold,14)+rect(418,135,236,222,'#fbe9db',hot,14)+
    label(195,185,s.open?'Room · cold side':'Cabinet',30,cold)+label(536,185,'Room · warm side',28,hot)+
    rect(260,268,200,130,'#fff','#7f94a6',16)+label(360,320,'Cooling loop',28)+
    arrow('M195 260V293H258',cold,id,6)+arrow('M462 293H540V260',hot,id,6)+
    arrow('M360 476V400',ink,id,6)+label(360,511,'Electrical work',28);
  if(s.showNumbers){
    svg+=label(190,240,b.removed+' units out',30,cold)+label(535,240,b.released+' units in',30,hot)+
      label(460,449,b.work+' unit',30)+label(360,575,s.open?b.released+' − '+b.removed+' = '+b.sameRoomNet+' added to room':b.removed+' removed + '+b.work+' work = '+b.released+' released',30);
  }
  if(s.open)svg+=line('M62 114H657',hot,3,'stroke-dasharray="10 7"')+label(360,88,'Door open: same surrounding air',28,hot);
  return plate(svg,'Fixed illustrative energy units, not watts, temperature or measured performance. Opening a real door changes heat load and operation; this comparison holds the example values fixed. Closed-cabinet passive heat leakage is omitted.',
    !s.showNumbers?'Cabinet and room are shown as separate heat sources and sinks connected through a cooling loop. Energy values are not revealed yet.':
    s.open?'Both sides exchange heat with one room. '+b.released+' example units released minus '+b.removed+' removed leaves '+b.sameRoomNet+' added.'
      :'Cabinet loses '+b.removed+' example units; work adds '+b.work+'; the warm side releases '+b.released+'.',id+'-'+s.open+'-'+s.showNumbers);
}
export function phaseScene(s: PhaseState): Scene {
  const id='fridge-phase',color=s.canBoil?cold:hot;
  if(s.time<11)return plate(defs(id)+label(360,64,'A cold tube inside a refrigerator',32)+
    rect(62,110,596,390,'#edf5fc','#aab8c4',20)+label(360,166,'Cabinet air',30)+
    rect(120,245,480,150,'url(#'+id+'-metal)','#708598',32)+rect(140,266,440,108,'#afd5eb',cold,18)+
    label(360,451,'What would let liquid boil here?',28)+label(360,558,'Choose a case or watch to find out',28),
    'Opening question. The liquid-to-vapor result is concealed until playback or a pressure-case action. This is a qualitative section with surrounding cabinet air, not a refrigerant simulation.',
    'A cold tube containing liquid in cabinet air. The opening view asks what conditions allow boiling; the result has not been revealed.',id+'-question');
  let svg=defs(id)+label(360,50,'Same fluid. Same chosen cold temperature.',28)+
    rect(62,96,596,414,'#edf5fc','#aab8c4',20)+label(360,145,'Warmer cabinet air',30)+
    rect(120,242,480,150,'url(#'+id+'-metal)','#708598',32)+rect(140,264,440,108,'#afd5eb',cold,18)+
    arrow('M360 170C320 200 400 216 360 250L360 286',hot,id,7)+label(530,205,'Heat in',28,hot)+
    label(360,445,s.pressure==='lower'?'Lower pressure · can boil here':'Higher pressure · liquid here',28,color)+
    label(360,555,s.canBoil?'Liquid becomes vapor as heat enters':'Liquid can still absorb heat and warm',28,color);
  if(s.canBoil)for(const [x,y,r] of [[200,300,18],[285,326,22],[390,296,25],[495,325,19]]){
    svg+='<circle cx="'+x+'" cy="'+y+'" r="'+r+'" fill="#fff" stroke="'+cold+'" stroke-width="2"/>';
  }
  return plate(svg,'Qualitative comparison: the chosen fluid temperature is at the lower-pressure boiling point and below the higher-pressure one. No real pressures, temperature values, bubble simulation or pressure-change transient is claimed. The tube wall separates air from refrigerant.',
    s.canBoil?'At the chosen cold temperature and lower pressure, the liquid boils as heat enters through its tube wall.'
      :'At the same chosen temperature and higher pressure, this fluid remains liquid; heat may still enter and warm it.',id+'-'+s.pressure);
}
