import type { LessonProgress } from '../progress';

/** An idle tab must never overwrite another tab's newer lesson checkpoint. */
export function progressWriter(write: (id: string, progress: LessonProgress) => void): {
  restored(id: string, seconds: number): void;
  save(id: string, progress: LessonProgress): boolean;
} {
  const clocks = new Map<string, number>();
  return {
    restored(id, seconds) { clocks.set(id, seconds); },
    save(id, progress) {
      if (clocks.get(id) === progress.seconds) return false;
      write(id, progress); clocks.set(id, progress.seconds); return true;
    },
  };
}
