import {fileURLToPath} from 'node:url';
import {renderNarration} from '../visual-studio/render-narration.mjs';
import {refrigeratorNarrations} from './narration.ts';
const requested=process.argv[2];
if(requested&&!refrigeratorNarrations.some(p=>p.id===requested))throw new Error('Unknown trusted narration plan');
for(const plan of refrigeratorNarrations.filter(p=>!requested||p.id===requested)) {
  await renderNarration(plan,fileURLToPath(new URL(`../../.vercel/claude-vacuum/private/refrigerator-r1-audio/${plan.id}/`,import.meta.url)));
}
