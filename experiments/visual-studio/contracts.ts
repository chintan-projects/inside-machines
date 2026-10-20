/** Local, trusted lesson authoring contract. Not a public catalog schema. */
export interface Label { readonly text: string; readonly x: number; readonly y: number }
export interface Scene {
  readonly svg: string;
  readonly labels: readonly Label[];
  readonly caption: string;
  readonly alt: string;
  readonly viewport?: { readonly x: number; readonly y: number; readonly width: number; readonly height: number };
  /** Stable structure identity; changes when text, topology or material changes. */
  readonly contentKey?: string;
  /** Trusted renderer updates within an unchanged structure, never domain rules. */
  readonly attributes?: readonly { readonly selector: string; readonly name: 'width' | 'opacity' | 'transform'; readonly value: string }[];
}
export interface FrameState {
  readonly time: number;
  readonly beatId: string;
  readonly description: string;
}
export type Controls = Readonly<Record<string, string>>;
export interface Action {
  readonly id: string;
  readonly label: string;
  readonly start: number;
  readonly end: number;
  readonly still?: number;
  readonly controls?: Controls;
}
export interface Choice { readonly value: string; readonly label: string }
export interface Control {
  readonly key: string;
  readonly label: string;
  readonly options: readonly Choice[];
  readonly advanced?: boolean;
}
export interface Question {
  readonly prompt: string;
  readonly choices: readonly string[];
  readonly answer: string;
  readonly revealAction?: Action;
}
export interface Source {
  readonly title: string;
  readonly url: string;
  readonly locator: string;
}
export interface NarrationCue {
  readonly start: number;
  readonly end: number;
  readonly text: string;
  /** Reviewed scene pose for this cue when reduced motion is requested. */
  readonly still: number;
}
export interface NarrationPlan {
  readonly id: string;
  readonly duration: number;
  readonly cues: readonly NarrationCue[];
}
export interface Narration extends NarrationPlan {
  readonly src: string;
}
export interface Lesson<T extends FrameState> {
  readonly id: string;
  readonly title: string;
  readonly summary: string;
  readonly duration: number;
  readonly defaultControls: Controls;
  readonly actions: readonly Action[];
  readonly controls: readonly Control[];
  readonly prediction: Question;
  readonly transfer: Question;
  readonly takeaway: string;
  readonly scope: string;
  readonly sources: readonly Source[];
  readonly narration?: Narration;
  stateAt(time: number, controls: Controls): T;
  render(state: T): Scene;
  controlsVisible(state: T): boolean;
  controlValues(state: T): Controls;
  takeawayVisible(state: T): boolean;
  controlRestart(controls: Controls): Action;
}
export interface StudioAPI {
  seek(time: number): void;
  play(): void;
  pause(): void;
  reset(): void;
  setControl(key: string, value: string): void;
  setMuted(muted: boolean): void;
  getState(): FrameState & { readonly playing: boolean; readonly controls: Controls;
    readonly narrated: boolean; readonly audioStatus: string; readonly muted: boolean };
}

declare global {
  interface Window { lessonStudio: StudioAPI; seek(time: number): void }
}
