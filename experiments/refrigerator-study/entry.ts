import { mountLesson } from '../visual-studio/player.ts';
import { mountPath } from '../visual-studio/path-player.ts';
import { attachNarration } from '../visual-studio/narration.ts';
import { refrigeratorCore, refrigeratorEnergy, refrigeratorPhase } from './narration.ts';
import { coreLesson, energyLesson, phaseLesson } from './lessons.ts';
import type { RefrigeratorArt } from './scenes.ts';
declare global {
  interface Window { createRefrigeratorArt(anatomy: Window['Anatomy']): RefrigeratorArt }
}
const root=document.getElementById('app');
if(!root)throw new Error('The local studio shell is missing');
try {
  const style=document.createElement('style');style.textContent=window.Anatomy.k.ISO_CSS;document.head.append(style);
  const art=window.createRefrigeratorArt(window.Anatomy), options={embedded:true,predictionFirst:true};
  mountPath(root,window.studioPath,{
    'refrigerator-r1-core':host=>mountLesson(host,coreLesson(art,attachNarration(refrigeratorCore,window.studioNarrations)),options),
    'refrigerator-r1-energy':host=>mountLesson(host,energyLesson(attachNarration(refrigeratorEnergy,window.studioNarrations)),options),
    'refrigerator-r1-phase':host=>mountLesson(host,phaseLesson(attachNarration(refrigeratorPhase,window.studioNarrations)),options),
  });
} catch {
  const message=document.createElement('p');message.setAttribute('role','alert');
  message.textContent='This local explanation could not load. Reload the saved page or return to the GPU example.';
  root.replaceChildren(message);
}
