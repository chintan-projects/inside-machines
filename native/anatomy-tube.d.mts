/** Additive Inside Machines typing boundary; the upstream runtime stays unchanged. */
import type { Point3, Projection, Tone } from '../vendor/anatomy/kit/iso-kit.ts';
export interface TubePiece {
  mid:Point3; body:string; shine:string; shade:string; edges:string;
  points:Point3[]; radii:number[]; ends:boolean[]; from:number; to:number;
  rings:{d:string;alpha:number}[]; ringTone:string; wide:boolean;
}
export function tubePieces(points:Point3[], radius:number, projection:Projection,
  options?:{maxLength?:number;spacing?:number;caps?:boolean;stripes?:'auto'|boolean}):TubePiece[];
export function tubeSvg(piece:TubePiece, options?:{tone?:Tone}):string;
