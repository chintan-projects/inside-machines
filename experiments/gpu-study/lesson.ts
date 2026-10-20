/** GPU-specific teaching/scene adapter; the player does not know GPU rules. */
import type { Controls, Label, Lesson } from '../visual-studio/contracts.ts';
import { stateAt, type GpuState, type Schedule } from './model.ts';

export interface ArtScene { readonly svg: string; readonly labels: readonly Label[]; readonly caption: string }
export interface GpuArt { board(): ArtScene; work(pose: Schedule): ArtScene }

/** Generated/local artwork crosses a validated, limited scene boundary. */
function checked(scene: ArtScene): ArtScene {
  if (typeof scene?.svg !== 'string' || scene.svg.length > 400000 || !Array.isArray(scene.labels) ||
      typeof scene.caption !== 'string' || /<(script|foreignObject|iframe)\b|\bon\w+\s*=/i.test(scene.svg) ||
      scene.labels.some(l => typeof l.text !== 'string' || !Number.isFinite(l.x) || !Number.isFinite(l.y) ||
        l.x < 0 || l.x > 720 || l.y < 0 || l.y > 620)) throw new Error('Unsupported local art output');
  return scene;
}

/** The art is a manually reviewed local spike, never a production renderer plugin. */
export function gpuLesson(art: GpuArt): Lesson<GpuState> {
  const board = checked(art.board());
  return {
    id: 'gpu-study-1', title: 'How does a GPU work?',
    summary: 'One chip, lots of little jobs. Start with just eight pixels.', duration: 42,
    defaultControls: { lanes: '4', work: 'auto', data: 'ready' },
    actions: [
      { id: 'run-pixels', label: 'Run eight pixels', start: 6, end: 18, still: 6.75, controls: { lanes: '4', work: 'independent', data: 'ready' } },
      { id: 'make-chain', label: 'Make the jobs depend', start: 20, end: 34, still: 22.25, controls: { lanes: '4', work: 'chain', data: 'ready' } },
      { id: 'whole-gpu', label: 'See the whole GPU', start: 36, end: 42, controls: { data: 'ready' } },
    ],
    controls: [
      { key: 'lanes', label: 'Available teaching lanes', options: [{ value: '1', label: 'One lane' }, { value: '4', label: 'Four lanes' }] },
      { key: 'work', label: 'Where does each input come from?', options: [
        { value: 'independent', label: 'Its own pixel' }, { value: 'chain', label: 'Previous answer' },
      ] },
      { key: 'data', label: 'Input availability', advanced: true, options: [
        { value: 'ready', label: 'Inputs ready' }, { value: 'held', label: 'Hold back inputs' },
      ] },
    ],
    stateAt,
    render(state: GpuState) {
      const scene = state.view === 'board' ? board : checked(art.work(state));
      return { ...scene,
        contentKey: state.view === 'board' ? 'gpu-board-1' :
          JSON.stringify([state.mode, state.laneCount, state.dataReady, state.round]),
        attributes: state.view === 'work'
          ? [{ selector: '[data-progress]', name: 'width', value: String(500 * state.progress) }] : [],
        viewport: state.view === 'board' ? { x: 0, y: 100, width: 720, height: 420 } : undefined,
        caption: state.view === 'board' ? board.caption : !state.dataReady
          ? 'Logical view · inputs held back · no job has started.'
          : `Logical view · ${state.completed === 8 ? `${state.totalRounds} rounds complete` : `toy round ${state.round + 1} of ${state.totalRounds}`} · ${state.completed}/8 results ready. Each job takes one ideal round; this is not hardware timing.`,
        alt: state.view === 'board' ? 'A generic graphics board with GPU chip, surrounding memory and connector, with the cooler omitted.'
          : `${state.description} ${state.jobs.map(j => `${j.id}: ${j.status}${j.output === null ? '' : `, result ${j.output}`}`).join('; ')}.`,
      };
    },
    controlsVisible: state => state.view === 'work',
    controlValues: state => ({ lanes: String(state.laneCount), work: state.mode, data: state.dataReady ? 'ready' : 'held' }),
    takeawayVisible: state => state.beatId === 'chain' || state.beatId === 'whole',
    controlRestart(controls: Controls) {
      const start = controls.work === 'chain' ? 20 : 6;
      return { id: 'experiment', label: '', start, end: start + 13, still: start + (start === 20 ? 2.25 : .75), controls };
    },
    takeaway: 'A GPU shines when many similar jobs have inputs ready. More lanes cannot make a missing answer arrive sooner.',
    prediction: {
      prompt: 'Four lanes let four independent jobs run at once. Must more lanes also help when each job needs the previous answer?',
      choices: ['More lanes must always help', 'It depends on which answers are ready'],
      answer: 'Only the first job is ready. Its answer unlocks the next one. The other lanes cannot skip that dependency, so this chain still needs eight toy rounds.',
      revealAction: { id: 'predict-chain', label: '', start: 20, end: 33, still: 22.25, controls: { lanes: '4', work: 'chain', data: 'ready' } },
    },
    transfer: {
      prompt: 'Imagine two separate chains of four jobs. Each chain needs its own previous answer. Could all four lanes stay busy?',
      choices: ['Yes, four lanes means four jobs', 'Only two jobs can be ready together'],
      answer: 'At most two: one ready job from each chain. Each next job waits for its own predecessor. Extra lanes cannot remove those links.',
    },
    scope: 'A generic board and an exact toy dependency model. Eight scalar “pixel values” each receive +1; independent inputs are 0–7, while a chain starts at 0 and uses each previous answer. One job takes one ideal round. Real GPUs have instruction groups, memory traffic, scheduling and many other constraints omitted here. Lane counts and viewing seconds are not die layout, core counts, GPU clock cycles or a speed benchmark. CUDA is one vendor’s model, not a universal GPU specification. Local teaching draft; independent technical, actual-device and beginner-learning reviews remain pending.',
    sources: [{ title: 'NVIDIA CUDA Programming Guide: Programming Model',
      url: 'https://docs.nvidia.com/cuda/cuda-programming-guide/01-introduction/programming-model.html',
      locator: '§1.2.1 kernel launch; §1.2.2 hardware/resources; §1.2.3 data and memory. Prerequisite/round results come from the declared toy graph.' }],
  };
}
