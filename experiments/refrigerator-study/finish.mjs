/** Explicit inspected integration repairs; preserve the exact paid response. */
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
const dir=new URL('../../.vercel/claude-vacuum/private/',import.meta.url);
const original=await readFile(new URL('fridge-art-2.txt',dir),'utf8');
let code=original.trim().replace(/^\x60\x60\x60(?:js|javascript)?\s*\n/,'').replace(/\n\x60\x60\x60$/,'');
const changes=[];
function replace(before,after,reason){
  if(code.split(before).length!==2)throw new Error('Repair anchor mismatch: '+reason);
  code=code.replace(before,after);changes.push(reason);
}
replace('insetPlan({ x: CAB.x','k.insetPlan({ x: CAB.x','Qualify the documented kit helper; avoid an undefined global.');
replace('pts.push([560, 120, 0], [560, 300, 330], [300, 120, 30]);',
  'pts.push([700, 100, 0], [700, 300, 350], [100, 300, 0]);',
  'Include the exposed condenser and hot line in the actual projection bounds.');
replace('pipe(cap.slice(3),', 'pipe(cap,', 'Connect the full narrow-tube return to the liquid-line endpoint.');
replace('warm: [640, 266, 230]', 'warm: [640, 262, 234]', 'Put the warm-coil anchor on the actual tubing.');
replace('narrow: [500, 262, 70]', 'narrow: [440, 275, 40]', 'Put the narrow-tube anchor on its actual route.');
replace('.map(l => ({ text: l.text, x: Math.max(90, Math.min(630, l.x)), y: Math.max(35, Math.min(575, l.y)) }));',
  '.map(l => ({ text: l.text, x: Math.max(90, Math.min(630, l.x)), y: Math.max(35, Math.min(575, l.y)) })).map(l=>l.text==="Compressor"?{...l,x:600,y:465}:l.text==="Narrow tube"?{...l,x:210,y:545}:l);',
  'Separate the compressor and narrow-tube labels at actual phone size.');
replace("      const lab = (t, p, dx, dy) =>", `      const direction=(route,index,color)=>{const a=I(route[index]),b=I(route[index+1]);const x=(a[0]+b[0])/2,y=(a[1]+b[1])/2,angle=Math.atan2(b[1]-a[1],b[0]-a[0])*180/Math.PI;return '<g transform="translate('+x+' '+y+')rotate('+angle+')"><path d="M-7 -6L0 0L-7 6" fill="none" stroke="'+color+'" stroke-width="2.8" stroke-linecap="round"/></g>';};
      const directions=direction(coldPath,2,'#235b83')+direction(suction,1,'#235b83')+direction(discharge,0,'#88451d')+direction(liquid,1,'#88451d')+direction(cap,4,'#235b83');
      const lab = (t, p, dx, dy) =>`,
  'Add nonanimated refrigerant-direction chevrons on actual tube segments.');
replace('        svg, labels,', `        svg: svg + labels.map((l,i)=>{const q=I([A.cold,A.comp,A.warm,A.narrow][i]);return '<path d="M'+q[0]+' '+q[1]+'L'+l.x+' '+l.y+'" fill="none" stroke="#52616d" stroke-width="1.5"/><circle cx="'+q[0]+'" cy="'+q[1]+'" r="3" fill="white" stroke="#52616d"/>';}).join(''), labels,`,
  'Anchor every core HTML label with a short leader and terminal dot.');
replace('svg: svg + labels.map','svg: svg + directions + labels.map','Keep direction cues alongside anchored labels.');
replace('The open front is a drawing aid, not an open-door experiment.',
  'The open front is a drawing aid, not an open-door experiment. Thin chevrons show refrigerant direction; broad wavy arrows in the sections show heat.',
  'Declare the two flow encodings beside the physical drawing.');
const sha=s=>createHash('sha256').update(s).digest('hex');
await writeFile(new URL('fridge-art-2-reviewed.js',dir),code);
await writeFile(new URL('fridge-art-2-repairs.json',dir),JSON.stringify({original_sha256:sha(original),reviewed_sha256:sha(code),changes},null,2));
