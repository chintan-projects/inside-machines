export interface LessonProgress { seconds: number; selected: string; speed: number; mode: 'explore' | 'watch' }
export function progressKey(user: string, lesson: string): string { return `inside.progress.${user}.${lesson}.v1`; }
export function readProgress(key: string, total: number, ids: string[]): LessonProgress {
  const fallback: LessonProgress = { seconds:0, selected:ids[0], speed:1, mode:'explore' };
  try {
    const raw: unknown = JSON.parse(localStorage.getItem(key) || 'null');
    if (!raw || typeof raw !== 'object') return fallback;
    return {
      seconds:'seconds' in raw && typeof raw.seconds === 'number' && Number.isFinite(raw.seconds) ? Math.max(0, Math.min(total, raw.seconds)) : 0,
      selected:'selected' in raw && typeof raw.selected === 'string' && ids.includes(raw.selected) ? raw.selected : ids[0],
      speed:'speed' in raw && typeof raw.speed === 'number' && [.5,1,2].includes(raw.speed) ? raw.speed : 1,
      mode:'mode' in raw && raw.mode === 'watch' ? 'watch' : 'explore',
    };
  } catch { return fallback; }
}
