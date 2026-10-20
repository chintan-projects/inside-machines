/** Browser media transport, independent of any lesson's causal rules. */
import type { Narration, NarrationAssets, NarrationCue, NarrationPlan } from './contracts.ts';

/** Bind an immutable cue plan to the matching, build-verified embedded track. */
export function attachNarration(plan: NarrationPlan, assets: NarrationAssets): Narration {
  const asset = assets[plan.id];
  if (asset?.planId !== plan.id) throw new Error('Missing reviewed node narration');
  return { ...plan, src: asset.src };
}

export type AudioStatus = 'idle' | 'starting' | 'playing' | 'waiting' | 'paused' | 'ended' | 'error';
export interface MediaPort extends EventTarget {
  currentTime: number;
  muted: boolean;
  readonly paused: boolean;
  readonly ended: boolean;
  play(): Promise<void>;
  pause(): void;
}

/** Validate authored cue boundaries before creating a media player or speech file. */
export function validateNarration(plan: NarrationPlan): void {
  if (!plan.id || !Number.isFinite(plan.duration) || plan.duration <= 0 || !plan.cues.length) {
    throw new Error('Invalid narration plan');
  }
  let end = 0;
  for (const cue of plan.cues) {
    if (cue.start !== end || !Number.isFinite(cue.end) || cue.end <= cue.start || !cue.text.trim() ||
        !Number.isFinite(cue.still) || cue.still < cue.start || cue.still >= cue.end) {
      throw new Error('Narration cues must cover the story with reviewed still poses');
    }
    end = cue.end;
  }
  if (end !== plan.duration) throw new Error('Narration duration mismatch');
}

/** Shared boundary semantics: a cue changes at its start, including after seeking. */
export function cueAt(plan: NarrationPlan, time: number): NarrationCue {
  return plan.cues.find(cue => time >= cue.start && time < cue.end) ??
    (time <= 0 ? plan.cues[0] : plan.cues[plan.cues.length - 1]);
}

/** Own playback intent, including delayed play() promises after pause/reset. */
export class NarrationTransport {
  status: AudioStatus = 'idle';
  private revision = 0;
  private wanted = false;
  private readonly media: MediaPort;
  readonly duration: number;
  private readonly changed: () => void;
  constructor(media: MediaPort, duration: number, changed: () => void) {
    this.media = media; this.duration = duration; this.changed = changed;
    media.addEventListener('playing', () => {
      if (!this.wanted) { media.pause(); return; }
      this.setStatus('playing');
    });
    media.addEventListener('waiting', () => { if (this.wanted) this.setStatus('waiting'); });
    media.addEventListener('pause', () => {
      // A queued pause event from an earlier seek must not cancel a newer play.
      if (this.wanted && media.paused) { this.wanted = false; this.revision++; this.setStatus(this.atEnd ? 'ended' : 'paused'); }
    });
    media.addEventListener('ended', () => this.finish());
    media.addEventListener('timeupdate', () => { if (this.atEnd) this.finish(); });
    media.addEventListener('error', () => {
      this.wanted = false; this.revision++; media.pause(); this.setStatus('error');
    });
  }
  get time(): number { return Math.max(0, Math.min(this.duration, this.media.currentTime)); }
  get muted(): boolean { return this.media.muted; }
  private get atEnd(): boolean { return this.media.ended || this.time >= this.duration; }
  private setStatus(status: AudioStatus): void { this.status = status; this.changed(); }
  /** Call directly in a click/keyboard handler to preserve browser user activation. */
  async play(): Promise<void> {
    const revision = ++this.revision;
    this.wanted = true; this.setStatus('starting');
    try {
      await this.media.play();
      if (revision !== this.revision) { if (!this.wanted) this.media.pause(); return; }
      this.setStatus('playing');
    } catch {
      if (revision !== this.revision) return;
      this.wanted = false; this.media.pause(); this.setStatus('error');
    }
  }
  pause(): void {
    this.wanted = false; this.revision++; this.media.pause();
    this.setStatus(this.atEnd ? 'ended' : 'paused');
  }
  seek(time: number): void {
    this.pause();
    this.media.currentTime = Number.isFinite(time) ? Math.max(0, Math.min(this.duration, time)) : 0;
    this.setStatus(this.atEnd ? 'ended' : 'paused');
  }
  reset(): void { this.seek(0); this.setStatus('idle'); }
  setMuted(muted: boolean): void { this.media.muted = muted; this.changed(); }
  toggleMute(): void { this.setMuted(!this.media.muted); }
  private finish(): void {
    this.wanted = false; this.revision++; this.media.pause(); this.setStatus('ended');
  }
}
