/** Trusted public factory boundary. No global factory, generated response or private file. */
export { createRefrigeratorR2Lessons } from './lessons.ts';
export { refrigeratorR2Definitions, refrigeratorR2Metadata } from './metadata.ts';
import originalPath from '../path.json' with {type:'json'};
export const refrigeratorR2Path={...originalPath,id:'refrigerator-r2',
  nodes:originalPath.nodes.map(node=>({...node,lesson_id:node.lesson_id.replace('refrigerator-r1-','refrigerator-r2-')}))};
