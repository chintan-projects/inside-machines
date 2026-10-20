import {fileURLToPath} from 'node:url';
import {renderNarration} from '../visual-studio/render-narration.mjs';
import {gpuNarration} from './narration.ts';

await renderNarration(gpuNarration,fileURLToPath(new URL('../../.vercel/claude-vacuum/private/gpu-s2-audio/',import.meta.url)));
