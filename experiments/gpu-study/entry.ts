import { mountLesson } from '../visual-studio/player.ts';
import { mountPath } from '../visual-studio/path-player.ts';
import { gpuLesson, type GpuArt } from './lesson.ts';
import { stateAt } from './model.ts';
import { gpuNarration } from './narration.ts';
import { coreLesson, memoryLesson, matrixLesson, attachNarration } from './depth-lessons.ts';
import { coreNarration, memoryNarration, matrixNarration } from './depth-narration.ts';

declare global {
  interface Window {
    createGpuArt(anatomy: Window['Anatomy']): GpuArt;
  }
}
const root = document.getElementById('app');
if (!root) throw new Error('The local studio shell is missing');
try {
  const style = document.createElement('style'); style.textContent = window.Anatomy.k.ISO_CSS;
  document.head.append(style);
  const art = window.createGpuArt(window.Anatomy), parallel = gpuLesson(art);
  const board = parallel.render(stateAt(0, {}));
  const speech = (plan: typeof gpuNarration) => attachNarration(plan, window.studioNarrations);
  const embedded = { embedded: true };
  mountPath(root, window.studioPath, {
    'gpu-core-s3': host => mountLesson(host, coreLesson(board, speech(coreNarration)), embedded),
    'gpu-study-1': host => mountLesson(host, { ...parallel, title: 'How can many calculations happen together?',
      summary: 'Compare independent jobs with jobs that need the previous answer.',
      actions: parallel.actions.filter(a => a.id !== 'whole-gpu'), narration: speech(gpuNarration) }, embedded),
    'gpu-memory-s3': host => mountLesson(host, memoryLesson(speech(memoryNarration)), embedded),
    'gpu-matrix-s3': host => mountLesson(host, matrixLesson(speech(matrixNarration)), embedded),
  });
} catch {
  const error = document.createElement('p'); error.setAttribute('role', 'alert');
  error.textContent = 'This local explanation could not load. Reload the saved page or return to the vacuum example.';
  root.replaceChildren(error);
}
