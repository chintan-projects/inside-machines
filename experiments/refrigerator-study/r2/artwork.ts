/** Trusted native R2 cabinet. R1 paid output is retained separately, never executed. */
import type { ArtPose } from '../model.ts';
import type { Scene, Label } from '../../../web/studio/contracts.ts';
import { k, type Point, type Part, addSolid, addTube, partsSvg, cream, dark, glass,
  food, blue, copper, metal, scene, leader, chevron, heatArrow, text, hot, cold, work } from './geometry.ts';

const cabinet={x:100,y:110,w:290,d:176,r:8};
const inner={x:128,y:138,w:234,d:136,r:4};
const bounds=[...k.boxCorners(cabinet,0,340),[700,290,350],[80,110,0]] as Point[];
const projection=k.fitProjection(bounds,720,560,{pad:64,azimuth:38,elevation:24});
const rows=(levels:readonly number[],left:number,right:number,y:number):Point[] =>
  levels.flatMap((z,i):Point[]=>i%2?[[right,y,z],[left,y,z]]:[[left,y,z],[right,y,z]]);
const coldCoil=rows([275,248,221,194,167],150,340,151);
const warmCoil=rows([292,263,234,205,176,147,118],580,675,258);
const suction:Point[]=[coldCoil.at(-1)!,[340,151,95],[405,151,72],[465,175,72]];
const discharge:Point[]=[[515,175,112],[515,175,334],[580,258,334],warmCoil[0]!];
const liquid:Point[]=[warmCoil.at(-1)!,[675,258,62],[550,258,42],[486,258,42]];
const capillary:Point[]=[[486,258,42],[405,258,42],[150,258,42],[150,151,42],coldCoil[0]!];
/** Exported geometry lets a source review check actual port/route continuity. */
export const refrigeratorRoutes={coldCoil,suction,discharge,warmCoil,liquid,capillary} as const;
const anchors:Record<string,Point>={
  'Cold coil':[335,151,248],Compressor:[490,175,105],
  'Warm coil':[675,258,234],'Narrow tube':[350,258,42],'Insulated cabinet':[105,260,160],
};
const labels:readonly Label[]=[
  {text:'Cold coil',x:144,y:187},{text:'Warm coil',x:568,y:58},
  {text:'Compressor',x:595,y:427},{text:'Narrow tube',x:244,y:517},
  {text:'Insulated cabinet',x:118,y:414},
  {text:'Electrical work',x:582,y:540},
];
function buildCabinet():string {
  const parts:Part[]=[];
  const slab=(at:Point,plan:k.Plan,z:number,height:number,mat=cream,detail='')=>
    addSolid(parts,at,k.slabOf(plan,z,height,projection,5,.8),projection,mat,detail);
  const cylinder=(x:number,y:number,radius:number,z:number,height:number,mat=metal)=>
    addSolid(parts,[x,y,z+height/2],k.cylinder(x,y,radius,z,height,projection,24,.6),projection,mat);
  for(const x of [122,368])for(const y of [132,264])cylinder(x,y,9,0,14,dark);
  slab([245,198,25],cabinet,14,24);
  slab([245,198,41],{...inner,y:125,d:147},38,6,glass);
  slab([245,125,180],{...cabinet,d:28},44,275);
  // Thick exposed wall includes insulation and outer/inner skins; front is a drawing cut.
  slab([114,200,180],{...cabinet,y:138,w:28,d:148},44,275);
  // The near side is sectioned too: keep its sill and rear support, expose the working coil.
  slab([376,200,65],{...cabinet,x:362,y:138,w:28,d:148},44,42);
  slab([376,146,202],{...cabinet,x:362,y:138,w:28,d:16},86,233);
  slab([245,198,329],cabinet,319,21);
  slab([245,281,180],{x:100,y:280,w:14,d:6,r:1},44,275,metal);
  slab([380,281,180],{x:376,y:280,w:14,d:6,r:1},44,275,metal);
  for(const z of [108,253])cylinder(386,281,4,z,25,dark);
  for(const z of [125,213]) {
    slab([245,208,z],inner,z,5,glass);
    for(const x of [133,357])slab([x,220,z-3],{x,y:210,w:5,d:25,r:1},z-4,4,metal);
  }
  cylinder(183,230,23,130,38,food);cylinder(183,230,25,168,4,cream);
  slab([288,215,234],{x:262,y:190,w:54,d:46,r:7},218,30,food);
  slab([288,215,250],{x:260,y:188,w:58,d:50,r:7},248,4,cream);
  for(const x of [470,530])for(const y of [158,208])cylinder(x,y,6,0,12,dark);
  const compressor={x:455,y:142,w:90,d:76,r:28};
  slab([500,180,61],compressor,12,100,dark,k.lineSvg(k.sideSeam(compressor,70,projection,10),{tone:'lo'}));
  slab([535,192,115],{x:526,y:183,w:22,d:24,r:3},112,9,metal);
  for(const x of [578,675])slab([x,258,178],{x:x-3,y:263,w:6,d:10,r:1},28,274,dark);
  for(const z of [30,302])slab([625,258,z],{x:575,y:253,w:105,d:8,r:2},z,5,metal);
  // Every visible refrigerant line lands on an actual shell port or adjacent tube.
  addTube(parts,coldCoil,5.2,projection,blue);
  addTube(parts,suction,4.8,projection,blue);
  addTube(parts,discharge,4.8,projection,copper);
  addTube(parts,warmCoil,6,projection,copper);
  addTube(parts,liquid,4.6,projection,copper);
  addTube(parts,capillary,2.4,projection,blue);
  for(const endpoint of [[465,175,72],[515,175,112]] as Point[]) {
    cylinder(endpoint[0],endpoint[1],7,endpoint[2]-3,6,metal);
  }
  addTube(parts,[[539,195,114],[560,195,98],[560,220,12],[615,220,12]],3.5,projection,dark);
  slab([626,220,12],{x:612,y:210,w:28,d:22,r:5},6,12,dark);
  for(const y of [214,225])slab([645,y,12],{x:640,y,w:13,d:3,r:0},8,8,metal);
  return partsSvg(parts);
}
const cabinetSvg=buildCabinet();
const materialRoutes=[coldCoil,suction,discharge,warmCoil,capillary] as const;
const routeColors=[cold,cold,hot,hot,cold];
const startPoints=materialRoutes.map(route=>k.iso(route[0]!,projection));
const heatIn=k.iso([255,151,221],projection),heatOut=k.iso([680,258,234],projection);
/** Cached geometry, incremental cues: playback does not rebuild the solids every frame. */
export function overview(s:ArtPose):Scene {
  const directions=materialRoutes.map((route,i)=>chevron(route,projection,0,routeColors[i]!,`data-route-${i}`)).join('');
  const leaders=labels.map(label=>leader(label,k.iso(label.text==='Electrical work'?[540,195,114]:anchors[label.text]!,projection))).join('');
  const heat=s.running?heatArrow(`M${heatIn[0]-100} ${heatIn[1]+28}Q${heatIn[0]-55} ${heatIn[1]-8} ${heatIn[0]-8} ${heatIn[1]}`,'r2-heat-in')+
    heatArrow(`M${heatOut[0]+8} ${heatOut[1]}Q${heatOut[0]+70} ${heatOut[1]-18} ${heatOut[0]+54} ${heatOut[1]-66}`,'r2-heat-out')+
    text(heatOut[0]+38,heatOut[1]-90,'Heat out',30,hot):'';
  const electrical=k.iso([540,195,114],projection);
  const workInput=heatArrow(`M${electrical[0]+85} ${electrical[1]+66}L${electrical[0]+10} ${electrical[1]+10}`,'r2-work',work);
  const drawing=scene(cabinetSvg+leaders+directions+heat+(s.running?workInput:''),
    'Exposed teaching layout. The open front and near wall are drawing cuts, not the door-open experiment. Thin chevrons follow sealed refrigerant; broad arrows mean heat or electrical work. Real coil positions vary. '+
    (s.running?'The jobs happen together; the story only changes your focus.':'Stopped comparison: sustained pumping is off. Brief remaining heat transfer is omitted.'),
    'A thick-walled refrigerator cabinet with shelves and food. Its blue inside coil connects through sealed tubing to a supported compressor, copper outside coil and narrow return tube. '+(s.running?'Heat enters the inside coil, electrical work enters the compressor and heat leaves the outside coil.':'The compressor is stopped; sustained pumping and its heat/work arrows are absent. Residual heat transfer is omitted.'),
    'refrigerator-r2-whole-'+s.running,labels,560);
  const cues=materialRoutes.map((route,i)=>{
    const segment=Math.min(route.length-2,Math.floor(s.progress*(route.length-1)));
    const f=s.progress*(route.length-1)-segment,a=k.iso(route[segment]!,projection),b=k.iso(route[segment+1]!,projection);
    const angle=Math.atan2(b[1]-a[1],b[0]-a[0])*180/Math.PI;
    const x=a[0]+(b[0]-a[0])*f,y=a[1]+(b[1]-a[1])*f;
    return {selector:`[data-route-${i}]`,name:'transform' as const,value:`translate(${s.running?x:startPoints[i]![0]} ${s.running?y:startPoints[i]![1]})rotate(${angle})`};
  });
  return {...drawing,attributes:[...cues,...materialRoutes.map((_,i)=>({selector:`[data-route-${i}]`,name:'opacity' as const,value:s.running?'1':'0'}))]};
}
