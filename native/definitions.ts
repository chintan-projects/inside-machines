/** Finite trusted factories; no paths or executable modules are accepted from API data. */
import type { FrameState, Lesson } from '../web/studio/contracts';
import type { NativeSpec } from '../web/studio/native-contracts';
import { refrigeratorR2Definitions, refrigeratorR2Path } from '../experiments/refrigerator-study/r2/index';
import { createGpuMemoryR1Definition } from './gpu-memory-r1';

export interface NativeDefinition { readonly lesson:Lesson<FrameState>; readonly spec:NativeSpec }
export const nativeSuggestedPath=refrigeratorR2Path;
export const rendererEntries=[
  {id:'refrigerator-native-r2',entry:'experiments/refrigerator-study/r2/index.ts'},
  {id:'gpu-memory-native-r1',entry:'native/gpu-memory-r1.ts'},
] as const;

export function nativeDefinitions():readonly NativeDefinition[] {
  const gpu=createGpuMemoryR1Definition();
  return [...refrigeratorR2Definitions(),{lesson:gpu.lesson,
    spec:{...gpu.metadata,renderer:{id:'gpu-memory-native-r1',fingerprint:''}}}];
}
