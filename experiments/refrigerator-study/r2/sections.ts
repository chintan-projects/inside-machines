/** Independent physical working sections; all outcomes come from imported model state. */
import type { Scene } from '../../../web/studio/contracts.ts';
import type { CycleState, PhaseState, EnergyState } from '../model.ts';
import { mechanismPoints } from './model.ts';
import { k, type Point, type Part, addSolid, addTube, partsSvg, metal, dark, blue,
  copper, scene, leader, heatArrow, text, path, cold, hot, work, chevron, fitRegion } from './geometry.ts';

const coilProjection=k.fitProjection([[0,0,0],[560,160,210]],720,470,{pad:85,azimuth:66,elevation:23});
/** Sectioned tube walls and their actual ports remain visible around the fluid. */
function passage(warm:boolean):string {
  const parts:Part[]=[],p=coilProjection;
  const slab=(x:number,y:number,w:number,d:number,z:number,h:number,mat=metal)=>
    addSolid(parts,[x+w/2,y+d/2,z+h/2],k.slabOf({x,y,w,d,r:3},z,h,p,4,.5),p,mat);
  slab(50,40,460,96,72,9);slab(50,40,460,9,81,73);
  slab(50,127,460,9,81,28); // Cut front wall keeps the working passage exposed.
  slab(50,40,12,96,81,73);slab(498,40,12,96,81,73);
  slab(62,49,436,78,81,18,blue);
  addTube(parts,[[0,88,114],[50,88,114]],23,p,warm?copper:blue);
  addTube(parts,[[510,88,114],[560,88,114]],23,p,warm?copper:blue);
  for(const x of [84,476])slab(x,28,8,120,61,11,dark); // Actual tube support saddles.
  return partsSvg(parts);
}
const coldPassage=passage(false),warmPassage=passage(true);
const coilRoute:Point[]=[[4,88,120],[556,88,120]];
function fluidMarks(warm:boolean):string {
  const p=coilProjection;
  return [warm?[110,170,230,290]:[300,360,420,470]].flatMap(xs=>xs.map((x,i)=>{
    const at=k.iso([x,90,117+i%2*13],p);
    return `<ellipse cx="${at[0]}" cy="${at[1]}" rx="12" ry="9" fill="#fffdf5" stroke="${warm?hot:cold}" stroke-width="2"/>`;
  })).join('');
}
export function coilSection(s:CycleState,warm:boolean):Scene {
  const p=coilProjection,id=warm?'r2-condenser':'r2-evaporator';
  const wall=k.iso([290,44,151],p),left=k.iso([15,88,114],p),right=k.iso([545,88,114],p);
  const labels=[{text:warm?'Warm coil':'Cold coil',x:360,y:59},
    {text:warm?'Vapor in':'Liquid in',x:123,y:360},{text:warm?'Liquid out':'Vapor out',x:594,y:360}];
  const heat=warm?heatArrow(`M${wall[0]} ${wall[1]}Q${wall[0]-35} ${wall[1]-28} ${wall[0]} ${wall[1]-66}`,'r2-coil-heat'):
    heatArrow(`M${wall[0]} ${wall[1]-72}Q${wall[0]-35} ${wall[1]-44} ${wall[0]} ${wall[1]-8}`,'r2-coil-heat');
  let svg=(warm?warmPassage:coldPassage)+`<g data-phase-marks>${fluidMarks(warm)}</g>`+
    text(360,105,warm?'Cooler kitchen air':'Warmer cabinet air',32)+
    leader(labels[0]!,wall)+leader(labels[1]!,left)+leader(labels[2]!,right)+
    (s.running?heat:'')+text(525,153,warm?'Heat out':'Heat in',32,hot)+
    text(360,426,'Metal wall separates air from refrigerant',30)+
    chevron(coilRoute,p,0,warm?hot:cold,'data-coil-flow');
  if(!s.running)svg+=text(360,460,'Pumping stopped · brief residual heat transfer omitted',25);
  const a=k.iso(coilRoute[0]!,p),b=k.iso(coilRoute[1]!,p),angle=Math.atan2(b[1]-a[1],b[0]-a[0])*180/Math.PI;
  return {...scene(svg,
    'A sectioned passage with its tube wall, inlet, outlet and surrounding air. '+
    (warm?'Hotter vapor gives heat to kitchen air and condenses.':'Heat from cabinet air enters colder fluid; liquid evaporates as it carries energy away.')+
    ' Phase regions and material speed are illustrative, not a simulated liquid interface. The cutaway removes part of the wall, not the seal in a real appliance.',
    (warm?'Vapor enters a copper condenser passage; heat crosses the metal wall into cooler kitchen air; liquid leaves.':
      'Liquid enters a blue evaporator passage; heat from warmer cabinet air crosses the metal wall; liquid becomes vapor and leaves.'),id+'-'+s.running,labels,480),
    attributes:[{selector:'[data-coil-flow]',name:'transform',value:`translate(${a[0]+(b[0]-a[0])*s.progress} ${a[1]+(b[1]-a[1])*s.progress})rotate(${angle})`},
      {selector:'[data-phase-marks]',name:'opacity',value:warm||s.time>=22?'1':'0'},
      {selector:'[data-coil-flow]',name:'opacity',value:s.running?'1':'0'}]};
}

const compressorBounds=[...k.boxCorners({x:-81,y:-48,w:162,d:96,r:0},85,334),
  ...k.boxCorners({x:-100,y:-64,w:200,d:128,r:0},-82,-50),
  ...k.boxCorners({x:-167,y:-12,w:334,d:24,r:0},282,306)];
const compressorProjection=fitRegion(compressorBounds,{x:70,y:108,width:580,height:356},60,19);
const cp=compressorProjection;
function compressorHousing():string {
  const parts:Part[]=[];
  const slab=(x:number,y:number,w:number,d:number,z:number,h:number,mat=metal)=>
    addSolid(parts,[x+w/2,y+d/2,z+h/2],k.slabOf({x,y,w,d,r:4},z,h,cp,5,.5),cp,mat);
  slab(-100,-64,200,128,-70,20,dark);
  for(const x of [-82,82])for(const y of [-46,46])addSolid(parts,[x,y,-70],k.cylinder(x,y,8,-82,12,cp,16),cp,dark);
  slab(-81,-48,162,10,85,225); // Back of the cut cylinder.
  slab(-81,-38,14,84,85,225);slab(67,-38,14,84,85,225);
  slab(-81,-48,162,96,310,18); // Cylinder head and real valve seats.
  slab(-81,36,162,10,85,38); // Front cut exposes piston, cylinder and chamber.
  slab(-68,-34,136,68,-48,55,dark);
  addTube(parts,[[-155,0,294],[-97,0,294],[-67,0,294]],12,cp,blue);
  addTube(parts,[[67,0,294],[97,0,294],[155,0,294]],12,cp,copper);
  for(const x of [-56,56])slab(x-9,-40,18,80,328,6,dark);
  // A wheel in the actual crank plane; two parallel faces reveal its thickness.
  const wheel=(y:number):Point[]=>Array.from({length:49},(_,i)=>{
    const angle=i/48*Math.PI*2;return [52*Math.cos(angle),y,52*Math.sin(angle)] as Point;
  });
  const front=wheel(8).map(point=>k.iso(point,cp)),back=wheel(-8).map(point=>k.iso(point,cp));
  const wheelSvg=`<path d="${k.pathOf([...front,...back.slice().reverse()],true)}" fill="#788e97" stroke="#64777e"/>`+
    `<path d="${k.pathOf(front,true)}" fill="#c2ced0" stroke="#64777e" stroke-width="2"/>`;
  return partsSvg(parts)+wheelSvg;
}
const housing=compressorHousing();
const pistonReference=k.iso([0,0,150],cp);
const pistonSvg=partsSvg([{
  depth:0,svg:(()=>{const parts:Part[]=[];addSolid(parts,[0,0,150],
    k.slabOf({x:-66,y:-36,w:132,d:72,r:2},140,20,cp,4,.6),cp,metal);return partsSvg(parts);})(),
}]);
export function compressorSection(s:CycleState):Scene {
  const {crank,piston}=mechanismPoints(s),pin=k.iso(piston,cp),crankPin=k.iso(crank,cp),center=k.iso([0,0,0],cp);
  const state=!s.running?'Stopped':s.intakeOpen?'Draw vapor in':s.outletOpen?'Push vapor out':'Squeeze trapped vapor';
  const labels=[{text:'Piston',x:561,y:262},{text:'Motor + crank',x:535,y:442},
    {text:'Vapor in',x:116,y:88},{text:'Vapor out',x:594,y:88}];
  const top=k.iso([-66,0,308],cp),camera=k.cameraOf(cp),height=308-piston[2]-10;
  const gasTransform=`matrix(${camera.sinA*camera.k} ${camera.cosA*camera.sinE*camera.k} 0 ${camera.cosE*camera.k*height/200} ${top[0]} ${top[1]})`;
  const gas=`<g data-gas><rect x="0" y="0" width="132" height="200" fill="#e9bd95" opacity=".65"/></g>`;
  const marks=Array.from({length:6},(_,i)=>`<circle data-vapor-mark-${i} r="5.5" fill="#fff5e3" stroke="#a27654" stroke-width="1.6"/>`).join('');
  const rod='<g data-rod><path d="M0 0L0 150" stroke="#627b85" stroke-width="15" stroke-linecap="round"/><path d="M0 0L0 150" stroke="#bdcbce" stroke-width="6" stroke-linecap="round"/></g>';
  const crankArm='<g data-crank><path d="M0 0L0 50" stroke="#5c7480" stroke-width="13" stroke-linecap="round"/></g>';
  const inlet=k.iso([-67,0,294],cp),outlet=k.iso([67,0,294],cp);
  const valves=`<g data-inlet>${path([[inlet[0],inlet[1]-14],[inlet[0],inlet[1]+14]],cold,6)}</g>`+
    `<g data-outlet>${path([[outlet[0],outlet[1]-14],[outlet[0],outlet[1]+14]],hot,6)}</g>`;
  const pistonLeader='<g data-piston-leader><path d="M0 0L0 1" fill="none" stroke="#64777e" stroke-width="1.6" vector-effect="non-scaling-stroke"/></g><circle data-piston-target r="3" fill="#fffdf4" stroke="#64777e"/>';
  let svg=text(360,40,'Inside one piston compressor',32)+housing+gas+marks+crankArm+rod+
    `<g data-piston>${pistonSvg}</g><circle data-crank-pin r="7" fill="#405a67" stroke="#fffdf5" stroke-width="2"/>`+valves+
    pistonLeader+leader(labels[1]!,center)+
    leader(labels[2]!,k.iso([-145,0,294],cp))+leader(labels[3]!,k.iso([145,0,294],cp))+
    text(360,515,state,34)+text(148,448,'Electrical work',29,work);
  if(s.running)svg+=heatArrow(`M135 413L${center[0]-45} ${center[1]+15}`,'r2-motor-work',work);
  if(s.intakeOpen)svg+=chevron([[-155,0,294],[-67,0,294]],cp,.8,cold,'');
  if(s.outletOpen)svg+=chevron([[67,0,294],[155,0,294]],cp,.8,hot,'');
  return {...scene(svg,
    'One reciprocating design, with a sectioned cylinder, valves and motor. The fixed-length rod transfers crank motion to the piston. Chamber size and qualitative valve timing follow that motion. Dots identify vapor, not a particle inventory; pressure and temperature are not numerically simulated. Other compressor designs exist.',
    'A supported compressor housing with its cylinder opened. Motor and crank move a fixed-length rod and piston. '+state+'. The inlet and outlet never open together in this model.',
    'refrigerator-r2-compressor-'+state,labels,550),attributes:[
    {selector:'[data-piston]',name:'transform',value:`translate(0 ${pin[1]-pistonReference[1]})`},
    ...Array.from({length:6},(_,i)=>{const mark=k.iso([i%2?-34:34,0,piston[2]+10+height*(.2+Math.floor(i/2)*.28)],cp);
      return {selector:`[data-vapor-mark-${i}]`,name:'transform' as const,value:`translate(${mark[0]} ${mark[1]})`};}),
    {selector:'[data-piston-leader]',name:'transform',value:`matrix(1 0 ${k.iso([62,0,piston[2]],cp)[0]-labels[0]!.x} ${pin[1]-labels[0]!.y} ${labels[0]!.x} ${labels[0]!.y})`},
    {selector:'[data-piston-target]',name:'transform',value:`translate(${k.iso([62,0,piston[2]],cp)[0]} ${pin[1]})`},
    {selector:'[data-gas]',name:'transform',value:gasTransform},
    {selector:'[data-rod]',name:'transform',value:`matrix(1 0 ${(crankPin[0]-pin[0])/150} ${(crankPin[1]-pin[1])/150} ${pin[0]} ${pin[1]})`},
    {selector:'[data-crank]',name:'transform',value:`matrix(1 0 ${(crankPin[0]-center[0])/50} ${(crankPin[1]-center[1])/50} ${center[0]} ${center[1]})`},
    {selector:'[data-crank-pin]',name:'transform',value:`translate(${crankPin[0]} ${crankPin[1]})`},
    {selector:'[data-inlet]',name:'transform',value:`rotate(${s.intakeOpen?38:0} ${inlet[0]} ${inlet[1]-14})`},
    {selector:'[data-outlet]',name:'transform',value:`rotate(${s.outletOpen?-38:0} ${outlet[0]} ${outlet[1]-14})`},
  ]};
}

const capProjection=k.fitProjection([[0,0,0],[560,100,120]],720,370,{pad:70,azimuth:73,elevation:24});
function capillaryBody():string {
  const p=capProjection,parts:Part[]=[];
  for(const [x,w,mat] of [[20,135,copper],[405,135,blue]] as const) {
    addSolid(parts,[x+w/2,50,40],k.slabOf({x,y:18,w,d:64,r:10},30,12,p,5),p,mat);
    addSolid(parts,[x+w/2,21,65],k.slabOf({x,y:18,w,d:8,r:2},42,44,p,4),p,metal);
    addSolid(parts,[x+w/2,79,50],k.slabOf({x,y:74,w,d:8,r:2},42,14,p,4),p,metal);
  }
  addTube(parts,[[155,50,56],[405,50,56]],7,p,metal);
  for(const x of [205,355])addSolid(parts,[x,50,28],k.slabOf({x:x-7,y:22,w:14,d:56,r:3},16,20,p,4),p,dark);
  return partsSvg(parts);
}
const capBody=capillaryBody(),capRoute:Point[]=[[45,50,63],[515,50,63]];
export function capillarySection(s:CycleState):Scene {
  const p=capProjection,labels=[{text:'Narrow tube',x:360,y:78},
    {text:'Liquid in',x:131,y:307},{text:'Cold mixture out',x:561,y:307}];
  const a=k.iso(capRoute[0]!,p),b=k.iso(capRoute[1]!,p),angle=Math.atan2(b[1]-a[1],b[0]-a[0])*180/Math.PI;
  const outlet=k.iso([460,50,66],p);
  const svg=capBody+leader(labels[0]!,k.iso([285,50,63],p))+leader(labels[1]!,a)+leader(labels[2]!,b)+
    text(154,129,'Higher pressure',31,hot)+text(562,129,'Lower pressure',31,cold)+
    `<ellipse cx="${outlet[0]}" cy="${outlet[1]-4}" rx="10" ry="8" fill="#fffdf5" stroke="${cold}" stroke-width="2"/>`+
    chevron(capRoute,p,0,cold,'data-cap-flow')+text(360,382,'Restricted flow sustains the pressure difference',29);
  return {...scene(svg,
    'An enlarged, sectioned inlet and outlet with the narrow passage between them. Throttling reduces pressure; some liquid flashes into vapor using energy from the fluid. No heat absorption from the room is claimed in this tube. Proportions and flow speed are illustrative.',
    'Liquid enters from the higher-pressure side, flows through a narrow tube and leaves as a colder liquid-vapor mixture on the lower-pressure side. The tube is supported and connected at both ends.',
    'refrigerator-r2-capillary-'+s.running,labels,420),attributes:[
      {selector:'[data-cap-flow]',name:'transform',value:`translate(${a[0]+(b[0]-a[0])*s.progress} ${a[1]+(b[1]-a[1])*s.progress})rotate(${angle})`},
      {selector:'[data-cap-flow]',name:'opacity',value:s.running?'1':'0'},
    ]};
}

/** Same physical passage, with a separately declared qualitative pressure comparison. */
export function phaseSection(s:PhaseState):Scene {
  const revealed=s.time>=11,wall=k.iso([290,44,151],coilProjection);
  const labels=[{text:'Cold coil',x:360,y:59},{text:'Metal wall',x:570,y:330},
    {text:'Cabinet air',x:124,y:158}];
  const boiling=revealed&&s.canBoil;
  const svg=coldPassage+(boiling?`<g data-phase-bubbles>${fluidMarks(false)}</g>`:'')+
    text(360,108,'Same fluid · same chosen cold temperature',28)+
    leader(labels[0]!,wall)+leader(labels[1]!,k.iso([465,131,99],coilProjection))+
    leader(labels[2]!,k.iso([130,40,205],coilProjection))+
    (revealed?heatArrow(`M${wall[0]} ${wall[1]-72}Q${wall[0]-35} ${wall[1]-44} ${wall[0]} ${wall[1]-8}`,'r2-phase-heat')+
      `<g data-phase-heat>${path([[-7,-8],[0,0],[7,-8]],hot,3)}</g>`:'')+
    text(360,398,!revealed?'Must a boiling liquid be hot?':s.canBoil?'Lower pressure · liquid can boil here':'Higher pressure · liquid stays liquid',32)+
    text(360,449,!revealed?'Predict, then compare the two cases':s.canBoil?'Incoming heat helps liquid become vapor':'Heat can still enter and warm the liquid',28);
  const result=scene(svg,
    'An exposed metal tube in warmer cabinet air. The chosen fluid temperature is at the lower-pressure boiling point and below the higher-pressure one. These are assumed conditions, not a pressure-change transient. Phase marks are illustrative; no temperature or pressure readings are invented.',
    !revealed?'A cold liquid-filled tube in cabinet air. The opening question is whether boiling always means hot.':
      s.canBoil?'Lower pressure permits boiling at the chosen cold temperature; heat enters through the tube wall.':
        'At the same chosen temperature, the higher-pressure case stays liquid. Heat can still enter and warm it.',
    'refrigerator-r2-phase-'+revealed+'-'+s.pressure,labels,480);
  return {...result,attributes:revealed?[
    ...(boiling?[{selector:'[data-phase-bubbles]',name:'transform' as const,value:`translate(0 ${-(s.time%2)*5})`}]:[]),
    {selector:'[data-phase-heat]',name:'transform',value:`translate(${wall[0]} ${wall[1]-65+(s.time%2)/2*55})`},
  ]:[]};
}

/** Deliberately an energy accounting view, not a simulated compressor or temperature model. */
export function energySection(s:EnergyState):Scene {
  const b=s.balance,p=k.fitProjection([[0,0,0],[500,140,230]],720,390,{pad:78,azimuth:68,elevation:20}),parts:Part[]=[];
  const slab=(x:number,w:number,z:number,h:number,mat:string)=>addSolid(parts,[x+w/2,70,z+h/2],
    k.slabOf({x,y:18,w,d:104,r:7},z,h,p,5,.8),p,mat);
  slab(10,190,10,12,metal);slab(10,190,22,140,blue);
  slab(310,180,10,12,metal);slab(310,180,22,140,copper);
  const left=k.iso([106,70,160],p),right=k.iso([400,70,160],p);
  const labels=[{text:s.open?'Room · cold side':'Cabinet · cold side',x:164,y:86},{text:'Room · warm side',x:553,y:86}];
  let svg=text(360,37,s.open?'Both sides exchange heat with one room':'Cabinet and kitchen are separate',30)+
    partsSvg(parts)+leader(labels[0]!,left)+leader(labels[1]!,right)+
    heatArrow(`M${left[0]+24} ${left[1]+45}L340 310`,'r2-energy-out',cold)+
    heatArrow(`M385 310L${right[0]-12} ${right[1]+45}`,'r2-energy-in',hot)+
    text(360,345,'Cooling loop',32)+heatArrow('M360 414V365','r2-energy-work',work)+text(530,409,'Electrical work',29,work);
  if(s.showNumbers)svg+=text(150,365,`${b.removed} units removed`,30,cold)+
    text(576,365,`${b.released} released`,30,hot)+text(312,408,`${b.work}`,30,work)+
    text(360,482,s.open?`${b.released} − ${b.removed} = ${b.sameRoomNet} added to room`:
      `${b.removed} removed + ${b.work} work = ${b.released} released`,32);
  if(s.open)svg+=path([[50,110],[50,455],[670,455],[670,110]],hot,2,'stroke-dasharray="9 7"');
  const routes=[[[left[0]+24,left[1]+45],[340,310]],[[385,310],[right[0]-12,right[1]+45]],[[360,414],[360,365]]] as const;
  svg+=routes.map((_,i)=>`<g data-energy-flow-${i}>${path([[-7,-6],[0,0],[-7,6]],[cold,hot,work][i]!,3)}</g>`).join('');
  const result=scene(svg,
    'Reservoir blocks stand for two places exchanging energy; they are not appliance cutaways. Fixed illustrative energy units, not watts or measured performance. Opening a real door changes heat load; this comparison holds the numbers fixed. Passive heat leakage is omitted.',
    !s.showNumbers?'A separate cabinet and room exchange heat through a cooling loop; electrical work enters the loop.':
      s.open?`Both sides exchange heat with one room. ${b.released} units returned minus ${b.removed} removed leaves ${b.sameRoomNet} added.`:
        `${b.removed} units leave the cabinet, ${b.work} unit of work enters the loop, and ${b.released} units enter the kitchen.`,
    'refrigerator-r2-energy-'+s.open+'-'+s.showNumbers,labels,530);
  return {...result,attributes:routes.map(([a,b],i)=>({selector:`[data-energy-flow-${i}]`,name:'transform' as const,
    value:`translate(${a[0]+(b[0]-a[0])*(s.time%3)/3} ${a[1]+(b[1]-a[1])*(s.time%3)/3})rotate(${Math.atan2(b[1]-a[1],b[0]-a[0])*180/Math.PI})`}))};
}
