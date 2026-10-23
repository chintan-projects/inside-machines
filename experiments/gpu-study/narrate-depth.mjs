import {fileURLToPath} from 'node:url';
import {renderNarration} from '../visual-studio/render-narration.mjs';
import {coreNarration,memoryNarration,matrixNarration} from './depth-narration.ts';
const plans=[coreNarration,memoryNarration,matrixNarration], requested=process.argv[2];
if(requested&&!plans.some(p=>p.id===requested))throw new Error('Unknown trusted narration plan');
for(const plan of plans.filter(p=>!requested||p.id===requested)) {
  await renderNarration(plan,fileURLToPath(new URL(`../../.vercel/claude-vacuum/private/gpu-s3-audio/${plan.id}/`,import.meta.url)));
}
