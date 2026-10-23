/** Exact toy scheduler. Its rounds are teaching units, never hardware time. */
import type { Controls, FrameState } from '../visual-studio/contracts.ts';

export interface Job {
  readonly id: string;
  readonly input: number | null;
  readonly output: number | null;
  readonly status: 'ready' | 'waiting' | 'running' | 'done';
  readonly lane: number | null;
  readonly prerequisite: string | null;
}
export interface Lane {
  readonly index: number;
  readonly enabled: boolean;
  readonly jobId: string | null;
}
export interface Schedule {
  readonly mode: 'independent' | 'chain';
  readonly laneCount: 1 | 4;
  readonly dataReady: boolean;
  readonly round: number;
  readonly totalRounds: number;
  readonly progress: number;
  readonly jobs: readonly Job[];
  readonly lanes: readonly Lane[];
}
export interface GpuState extends FrameState, Schedule {
  readonly view: 'board' | 'work';
  readonly completed: number;
}

const IDS = [...'ABCDEFGH'];
const finite = (n: number): number => Number.isFinite(n) ? n : 0;

/** Complete only jobs whose prerequisites existed before a round started. */
export function schedule(
  mode: Schedule['mode'], laneCount: 1 | 4, dataReady: boolean, position: number,
): Schedule {
  if (!['independent', 'chain'].includes(mode) || ![1, 4].includes(laneCount)) {
    throw new Error('Unsupported toy scheduler input');
  }
  const totalRounds = mode === 'chain' ? 8 : Math.ceil(8 / laneCount);
  const at = dataReady ? Math.max(0, Math.min(totalRounds, finite(position))) : 0;
  const done = new Map<string, number>();
  const ready = (): string[] => dataReady ? IDS.filter((id, i) =>
    !done.has(id) && (mode === 'independent' || i === 0 || done.has(IDS[i - 1])),
  ).slice(0, laneCount) : [];
  const input = (id: string): number | null => {
    const i = IDS.indexOf(id);
    return !dataReady ? null : mode === 'independent' ? i : i === 0 ? 0 : done.get(IDS[i - 1]) ?? null;
  };
  for (let round = 0; round < Math.floor(at); round++) {
    const batch = ready().map(id => ({ id, input: input(id) }));
    for (const job of batch) {
      if (job.input === null) throw new Error('A running job requires an input');
      done.set(job.id, job.input + 1);
    }
  }
  const active = ready();
  const jobs: Job[] = IDS.map((id, i) => {
    const lane = active.indexOf(id);
    const value = input(id);
    return {
      id, input: value, output: done.get(id) ?? null,
      status: done.has(id) ? 'done' : lane >= 0 ? 'running' : value === null ? 'waiting' : 'ready',
      lane: lane >= 0 ? lane : null,
      prerequisite: mode === 'chain' && i > 0 ? IDS[i - 1] : null,
    };
  });
  return {
    mode, laneCount, dataReady, round: Math.floor(at), totalRounds,
    progress: at === totalRounds ? 1 : at % 1,
    jobs, lanes: Array.from({ length: 4 }, (_, i) => ({ index: i, enabled: i < laneCount, jobId: active[i] ?? null })),
  };
}

/** Story order selects attention; this pure state owns every causal outcome. */
export function stateAt(time: number, controls: Controls): GpuState {
  const t = Math.max(0, Math.min(42, finite(time)));
  const view = t < 6 || t >= 36 ? 'board' : 'work';
  const mode = controls.work === 'chain' ? 'chain' : controls.work === 'independent' ? 'independent' :
    t >= 20 ? 'chain' : 'independent';
  const laneCount = controls.lanes === '1' ? 1 : 4;
  const start = t < 20 ? 6 : 20;
  const pose = schedule(mode, laneCount, controls.data !== 'held', Math.max(0, (t - start) / 1.5));
  const completed = pose.jobs.filter(j => j.status === 'done').length;
  const description = view === 'board'
    ? t < 6 ? 'The chip does the calculations. Nearby memory holds the data. Try one tiny picture.'
      : 'Many similar jobs can run together—when their inputs are ready. The chip computes; memory holds the data.'
    : !pose.dataReady ? 'The inputs are held back. Available lanes wait: no input means no calculation.'
      : mode === 'chain' ? completed === 8
        ? 'All eight results are ready. This chain needed eight toy rounds even with four available lanes.'
        : `Job ${pose.jobs.find(j => j.status === 'running')?.id ?? 'A'} can start. Later jobs need the previous answer, so the other lanes wait.`
      : completed === 8 ? `Eight results, ${pose.totalRounds} toy rounds. Each pixel had its own input; no job needed another job’s answer.`
        : `${laneCount === 4 ? 'Four jobs' : 'One job'} can run now. Each adds 1 to its own input.`;
  return { ...pose, time: t, view, completed, beatId: view === 'board' ? t < 6 ? 'orient' : 'whole' : mode,
    description };
}
