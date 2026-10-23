/** Actual Anatomy solids/tubes. This module contains geometry, never cooling rules. */
import * as k from '../../../vendor/anatomy/kit/iso-kit.ts';
import { tubePieces, tubeSvg } from '#anatomy-tube';
import { escape } from '../../../web/studio/drawing.ts';
import type { Label, Scene } from '../../../web/studio/contracts.ts';
export { k };
export type Point = k.Point3;
export const cold='#286c93', hot='#a24f2e', ink='#2f3c42', work='#77603b';
export const material=(paper:string, top:string, shades:readonly string[]):string =>
  `--anatomy-paper:${paper};--anatomy-hi:${ink};--anatomy-top:${top};`+
  shades.map((shade,i)=>`--anatomy-shade-${i}:${shade};`).join('');
export const cream=material('#efeee6','#fffdf3',['#e8e5d9','#dcd8c9','#d0cbb9','#c3bda8']);
export const metal=material('#a4b1b4','#e7eeed',['#c1cdce','#a9b8bb','#899fa5','#708b93']);
export const dark=material('#52636a','#798b92',['#5f737b','#4a616a','#3d535d','#2b434f']);
export const glass=material('#dcebed','#f1f9f6',['#d4e5e5','#c1d9db','#a8c8cf','#92b4be']);
export const food=material('#d9c8a3','#f1dfb9',['#d5be91','#c6ac7b','#b69c6d','#a08759']);
export const blue=material('#6fa8bc','#c1e4ea',['#8cbdca','#6da6b9','#548ca6','#3d748f']);
export const copper=material('#bf8862','#e9bd8d',['#c99b76','#b5805d','#a26c4a','#8d593d']);
export interface Part { depth:number; svg:string }
/** Fit true world extrema into a reserved drawing region, leaving text outside it. */
export function fitRegion(points:Point[],region:{x:number;y:number;width:number;height:number},azimuth:number,elevation:number):k.Projection {
  const projection=k.fitProjection(points,region.width,region.height,{pad:8,azimuth,elevation});
  return {...projection,origin:[projection.origin[0]+region.x,projection.origin[1]+region.y]};
}
export function group(svg:string, mat:string, extra=''):string {
  const palette=Object.fromEntries(mat.split(';').filter(Boolean).map(declaration=>declaration.split(':')));
  const colors:Record<string,string>={'iso-fill':palette['--anatomy-paper']!,
    'iso-top':palette['--anatomy-top']!,'tb-body':palette['--anatomy-shade-2']!,
    'tb-shine':palette['--anatomy-top']!,'tb-shade':palette['--anatomy-shade-0']!};
  // Explicit values make the same trusted solids portable to resvg, static SVG and video.
  const flattened=svg.replace(/<path\b([^>]*?)\/>/g,(whole:string,attributes:string)=>{
    const cls=/class="([^"]+)"/.exec(attributes)?.[1]??'';
    const shade=/data-shade="(\d)"/.exec(attributes)?.[1];
    const fill=shade?palette['--anatomy-shade-'+shade]:colors[cls];
    if(fill)return `<path${attributes} style="fill:${fill};stroke:none"/>`;
    if(cls.includes('iso-line')||cls.includes('tb-ring')) {
      const tone=/data-tone="([^"]+)"/.exec(attributes)?.[1]??'lo';
      const stroke=({hi:ink,mid:'#75848a',lo:'#a4b0b3',faint:'#c8d2d1'} as Record<string,string>)[tone]??ink;
      return `<path${attributes} style="fill:none;stroke:${stroke};stroke-width:1;stroke-linecap:round;stroke-linejoin:round"/>`;
    }
    return whole;
  });
  return `<g ${extra}>${flattened}</g>`;
}
export function addSolid(parts:Part[], at:Point, paths:k.SolidPaths, projection:k.Projection,
  mat=cream, detail='', extra=''):void {
  parts.push({depth:k.depthOf(at,projection),svg:group(k.solidSvg(paths,{tone:'mid',inner:detail}),mat,extra)});
}
/** Tubes have physical radius, caps and depth-sorted spans, not thick flat strokes. */
export function addTube(parts:Part[], route:readonly Point[], radius:number, projection:k.Projection, mat:string):void {
  for(const piece of tubePieces([...route],radius,projection,{maxLength:28,spacing:4,caps:true})) {
    parts.push({depth:k.depthOf(piece.mid,projection),svg:group(tubeSvg(piece,{tone:'mid'}),mat)});
  }
}
export function partsSvg(parts:readonly Part[]):string {
  return [...parts].sort((a,b)=>a.depth-b.depth).map(part=>part.svg).join('');
}
export function text(x:number,y:number,value:string,size=32,color=ink):string {
  return `<text x="${x}" y="${y}" text-anchor="middle" font-family="Inter,system-ui,sans-serif" font-size="${size}" fill="${color}">${escape(value)}</text>`;
}
export function path(points:readonly k.Flat[],color=ink,width=3,extra=''):string {
  return `<path d="${k.pathOf([...points])}" fill="none" stroke="${color}" stroke-width="${width}" stroke-linecap="round" stroke-linejoin="round" ${extra}/>`;
}
export const css='.fridge-r2 text{font-weight:500}.fridge-r2 .iso-line{vector-effect:non-scaling-stroke}';
export function scene(svg:string,caption:string,alt:string,key:string,labels:readonly Label[]=[],height=600):Scene {
  const xml=svg.replace(/\s(data-[a-z0-9-]+)(?=[\s>])/g,' $1=""');
  return {svg:`<style>${css}</style><g class="fridge-r2">${xml}</g>`,caption,alt,labels,
    viewport:{x:0,y:0,width:720,height},contentKey:key};
}
export function leader(label:Label, at:k.Flat):string {
  const elbow:k.Flat=[label.x,at[1]];
  return path([at,elbow,[label.x,label.y]],'#64777e',1.6)+
    `<circle cx="${at[0]}" cy="${at[1]}" r="3" fill="#fffdf4" stroke="#64777e"/>`;
}
/** Thin moving chevrons mean material direction; their speed is deliberately qualitative. */
export function chevron(route:readonly Point[],projection:k.Projection,position:number,color:string,attribute:string):string {
  const segment=Math.min(route.length-2,Math.floor(position*(route.length-1)));
  const fraction=position*(route.length-1)-segment;
  const a=k.iso(route[segment]!,projection),b=k.iso(route[segment+1]!,projection);
  const x=a[0]+(b[0]-a[0])*fraction,y=a[1]+(b[1]-a[1])*fraction;
  const angle=Math.atan2(b[1]-a[1],b[0]-a[0])*180/Math.PI;
  return `<g ${attribute} transform="translate(${x} ${y})rotate(${angle})"><path d="M-8 -6L0 0L-8 6" fill="none" stroke="${color}" stroke-width="3.5"/></g>`;
}
export function heatArrow(d:string,id:string,color=hot):string {
  const values=(d.match(/-?\d+(?:\.\d+)?/g)??[]).map(Number);
  const x=values.at(-2)!,y=values.at(-1)!,dx=x-values.at(-4)!,dy=y-values.at(-3)!;
  const length=Math.hypot(dx,dy)||1,ux=dx/length,uy=dy/length;
  const points:k.Flat[]=[[x,y],[x-ux*17-uy*10,y-uy*17+ux*10],[x-ux*17+uy*10,y-uy*17-ux*10]];
  return `<g id="${id}"><path d="${d}" fill="none" stroke="${color}" stroke-width="7" stroke-linecap="round"/>`+
    `<path d="${k.pathOf(points,true)}" fill="${color}"/></g>`;
}
