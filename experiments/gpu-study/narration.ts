/** One reviewed script for local speech, captions and reduced-motion tour poses. */
import type { NarrationPlan } from '../visual-studio/contracts.ts';

export const gpuNarration: NarrationPlan = {
  id: 'gpu-s2-narration-1', duration: 42,
  cues: [
    { start: 0, end: 6, still: 2,
      text: 'This is a graphics processing unit. Its chip calculates; nearby memory holds data.' },
    { start: 6, end: 9.5, still: 6.75,
      text: 'Four lanes. Four jobs can run at once.' },
    { start: 9.5, end: 14.5, still: 10,
      text: 'Each pixel has its own input. No job needs another job’s answer.' },
    { start: 14.5, end: 20, still: 16,
      text: 'Eight results, in two toy rounds. These are teaching rounds, not real GPU timing.' },
    { start: 20, end: 25, still: 22.25,
      text: 'Now each job needs the previous answer. Extra lanes must wait.' },
    { start: 25, end: 31, still: 27.25,
      text: 'One answer unlocks the next job. More lanes cannot remove these links.' },
    { start: 31, end: 36, still: 33,
      text: 'The chain takes eight rounds, even with four lanes available.' },
    { start: 36, end: 42, still: 38,
      text: 'A GPU shines when many similar jobs have inputs ready. The chip computes; memory holds data.' },
  ],
};
