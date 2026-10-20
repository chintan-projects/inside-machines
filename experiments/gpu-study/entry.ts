import { mountLesson } from '../visual-studio/player.ts';
import { gpuLesson, type GpuArt } from './lesson.ts';
import { gpuNarration } from './narration.ts';

declare global {
  interface Window {
    Anatomy: { k: { ISO_CSS: string } };
    createGpuArt(anatomy: Window['Anatomy']): GpuArt;
    studioNarration: { readonly planId: string; readonly src: string };
  }
}

const root = document.getElementById('app');
if (!root) throw new Error('The local studio shell is missing');
try {
  const style = document.createElement('style'); style.textContent = window.Anatomy.k.ISO_CSS;
  document.head.append(style);
  if (window.studioNarration?.planId !== gpuNarration.id) throw new Error('Missing reviewed narration');
  mountLesson(root, { ...gpuLesson(window.createGpuArt(window.Anatomy)),
    narration: { ...gpuNarration, src: window.studioNarration.src } });
} catch {
  const error = document.createElement('p'); error.setAttribute('role', 'alert');
  error.textContent = 'This local explanation could not load. Reload the saved page or return to the vacuum example.';
  root.replaceChildren(error);
}
