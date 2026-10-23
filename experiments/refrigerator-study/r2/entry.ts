/** Local review entry. Hosted application imports the same trusted factory. */
import { mountLesson } from '../../../web/studio/player.ts';
import { mountPath } from '../../../web/studio/path-player.ts';
import { createRefrigeratorR2Lessons, refrigeratorR2Path } from './index.ts';
import type { Narration } from '../../../web/studio/contracts.ts';
declare global { interface Window { refrigeratorR2Narrations?:Readonly<Record<string,Narration>> } }
const host=document.getElementById('app');
if(!host)throw new Error('Missing local refrigerator review shell');
const lessons=createRefrigeratorR2Lessons(window.refrigeratorR2Narrations);
mountPath(host,refrigeratorR2Path,Object.fromEntries(lessons.map(lesson=>[
  lesson.id,(root:HTMLElement)=>mountLesson(root,lesson,{embedded:true,predictionFirst:true}),
])));
