/** Concept-specific lesson data. Every node mounts in the same shared player. */
import type { FrameState, Lesson, Narration, Scene } from '../visual-studio/contracts.ts';
export { attachNarration } from '../visual-studio/narration.ts';
import { coreNarration, memoryNarration, matrixNarration } from './depth-narration.ts';
import { coreStateAt, feedStateAt, matrixStateAt } from './depth-model.ts';
import { coreScene, feedScene, matrixScene } from './depth-scenes.ts';

const sources = [{ title: 'NVIDIA CUDA Programming Guide: Programming Model',
  url: 'https://docs.nvidia.com/cuda/cuda-programming-guide/01-introduction/programming-model.html',
  locator: '§1.2.1 host/device and launch; §1.2.2 resources; §1.2.3 data and memory. CUDA example; hardware varies.' }];
const scope = 'A generic discrete-GPU teaching example, not a particular graphics card or a speed benchmark. Eight toy brightness values are 0–7; adding 1 or 2 stays within our illustrative 0–10 shade scale. Four slots are not actual GPU cores/warps. Attention order does not imply that real memory movement and computation cannot overlap. Sources support the stated principles, not a certification of this drawing. Local draft: independent technical, actual-phone and beginner reviews remain pending.';
function base<T extends FrameState>(id: string, title: string, summary: string, narration: Narration): Pick<Lesson<T>,
  'id' | 'title' | 'summary' | 'duration' | 'narration' | 'sources' | 'scope'> {
  return { id, title, summary, duration: narration.duration, narration, sources, scope };
}
export function coreLesson(board: Scene, narration: Narration): Lesson<ReturnType<typeof coreStateAt>> {
  return { ...base('gpu-core-s3', 'What does a GPU actually do?', 'Follow one complete job: make a tiny picture brighter.', narration),
    defaultControls: { add: '1' }, stateAt: coreStateAt, render: s => coreScene(s, board),
    actions: [
      { id: 'trace-calculation', label: 'Explore the calculation', start: 46, end: 73.9, still: 58 },
      { id: 'see-result', label: 'Compare input and result', start: 62, end: 73.9, still: 68 },
    ],
    controls: [{ key: 'add', label: 'Change the instruction', options: [
      { value: '1', label: 'Add 1' }, { value: '2', label: 'Add 2' },
    ] }],
    controlsVisible: s => s.phase === 'compute' || s.phase === 'result',
    controlValues: s => ({ add: String(s.increment) }), takeawayVisible: s => s.time >= 62,
    controlRestart: controls => ({ id: 'core-experiment', label: '', start: 62, end: 73.9, still: 68, controls }),
    takeaway: 'The program chooses the operation. Memory holds the data. The GPU calculates results that another part of the program can use.',
    prediction: { prompt: 'Does the GPU decide on its own that this picture should become brighter?',
      choices: ['It chooses the change', 'A program specifies the work'],
      answer: 'A program specifies the work and inputs. The GPU executes the calculation; it does not invent the image-editing goal.',
      revealAction: { id: 'request-work', label: '', start: 22, end: 34, still: 27 } },
    transfer: { prompt: 'Keep the same input picture but change the instruction from add 1 to add 2. What must happen before the stored output changes?',
      choices: ['The memory label alone changes the picture', 'Run the new operation and store its results'],
      answer: 'The new calculation must run on the input values and its new results must be stored. Changing only a label does no computation.' },
  };
}
export function memoryLesson(narration: Narration): Lesson<ReturnType<typeof feedStateAt>> {
  return { ...base('gpu-memory-s3', 'What if the data is not ready?', 'Keep four calculation slots. Change only the supply of ready inputs.', narration),
    defaultControls: { supply: 'auto' }, stateAt: feedStateAt, render: feedScene,
    actions: [
      { id: 'one-input', label: 'Supply one input', start: 10, end: 22, still: 14.5, controls: { supply: '1' } },
      { id: 'four-inputs', label: 'Supply four inputs', start: 10, end: 22, still: 10.75, controls: { supply: '4' } },
    ],
    controls: [{ key: 'supply', label: 'Ready inputs per ideal round', options: [
      { value: '1', label: 'One input' }, { value: '4', label: 'Four inputs' },
    ] }],
    controlsVisible: s => s.time >= 10, controlValues: s => ({ supply: String(s.supply) }),
    takeawayVisible: s => s.time >= 34,
    controlRestart: controls => ({ id: 'supply-experiment', label: '', start: 10, end: 22, still: 10.75, controls }),
    takeaway: 'Calculation capacity is useful when both work and inputs are ready. Data supply can limit how much of that capacity is used.',
    prediction: { prompt: 'Four slots are free, but only one new input is supplied each round. Can all four do useful work in this model?',
      choices: ['Yes, because the slots are free', 'Only one has an input'],
      answer: 'Only one receives an input. The other three wait. This toy model explicitly supplies then computes each round; it is not a hardware timing model.',
      revealAction: { id: 'missing-inputs', label: '', start: 10, end: 22, still: 14.5, controls: { supply: '1' } } },
    transfer: { prompt: 'Suppose we add four more slots but still supply only one input per round. What changes the limit?',
      choices: ['The extra empty slots remove the limit', 'More ready data or less data movement is needed'],
      answer: 'The supply remains one useful input per round in this declared model. More slots alone do not increase it. Real performance also depends on reuse, overlap and other constraints.' },
  };
}
export function matrixLesson(narration: Narration): Lesson<ReturnType<typeof matrixStateAt>> {
  return { ...base('gpu-matrix-s3', 'How do small calculations become a matrix multiplication?', 'Build one answer from a row and a column. Then see the larger pattern.', narration),
    scope: 'An exact 2×2 mathematical example, not a real model’s weights, GPU execution trace, language-model explanation or performance measurement. Each output is the sum of the two row/column products. Availability and execution constraints still apply. Attention Is All You Need is the original Transformer, not proof of every GPT architecture. Human technical and beginner review remain pending.',
    sources: [...sources, { title: 'Attention Is All You Need', url: 'https://arxiv.org/html/1706.03762v7',
      locator: '§3.2.1 equation 1: matrix products in attention; §3.3 equation 2: feed-forward transformations. Our 2×2 numbers are independently declared toy data.' }],
    defaultControls: { cell: '0', weight: 'original' }, stateAt: matrixStateAt, render: matrixScene,
    actions: [{ id: 'build-output', label: 'Build one output', start: 10, end: 44, still: 39 },
      { id: 'show-outputs', label: 'See all four outputs', start: 44, end: 58, still: 50 }],
    controls: [
      { key: 'cell', label: 'Inspect an output (row, column)', options: [
        { value: '0', label: '(1, 1)' }, { value: '1', label: '(1, 2)' },
        { value: '2', label: '(2, 1)' }, { value: '3', label: '(2, 2)' },
      ] },
      { key: 'weight', label: 'Change one input in B', options: [
        { value: 'original', label: 'Original B' }, { value: 'changed', label: 'Top-right: 0 becomes 1' },
      ] },
    ],
    controlsVisible: s => s.time >= 10,
    controlValues: s => ({ cell: String(s.row * 2 + s.column), weight: s.changed ? 'changed' : 'original' }),
    takeawayVisible: s => s.time >= 44,
    controlRestart: controls => ({ id: 'matrix-experiment', label: '', start: 44, end: 58, still: 50, controls }),
    takeaway: 'One output combines one row with one column. Many outputs can be computed from the same inputs without needing each other’s answers.',
    prediction: { prompt: 'Must the top-left output be finished before the bottom-right output can be calculated?',
      choices: ['Yes, outputs form a chain', 'No, each uses input rows and columns'],
      answer: 'Each output uses a row of A and a column of B. It does not need another output. That creates independent work, subject to available resources and data.',
      revealAction: { id: 'independent-outputs', label: '', start: 44, end: 58, still: 50 } },
    transfer: { prompt: 'Change only the top-right entry of B from 0 to 1. Which output column can change, and why?',
      choices: ['Every output must change', 'Only column 2 uses that changed entry'],
      answer: 'Only column 2 of C uses column 2 of B. Its values change from 4 and 8 to 5 and 11; column 1 stays 4 and 10. Each changed value follows its row/column products.' },
  };
}
export const depthPlans = [coreNarration, memoryNarration, matrixNarration];
