import { mountLesson } from '../visual-studio/player.ts';
import { gpuLesson, type GpuArt } from './lesson.ts';

declare global {
  interface Window {
    Anatomy: { k: { ISO_CSS: string } };
    createGpuArt(anatomy: Window['Anatomy']): GpuArt;
  }
}

const root = document.getElementById('app');
if (!root) throw new Error('The local studio shell is missing');
try {
  const style = document.createElement('style'); style.textContent = window.Anatomy.k.ISO_CSS;
  document.head.append(style);
  mountLesson(root, gpuLesson(window.createGpuArt(window.Anatomy)));
} catch {
  const error = document.createElement('p'); error.setAttribute('role', 'alert');
  error.textContent = 'This local explanation could not load. Reload the saved page or return to the vacuum example.';
  root.replaceChildren(error);
}
