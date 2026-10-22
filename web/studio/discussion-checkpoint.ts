import type { Answer } from '../contracts';
import type { StoredSpec } from './native-contracts';

/** Answers remain scoped to their exact lesson revision and valid stored checkpoints. */
export function discussionCheckpoint(spec: StoredSpec, answer: Answer): number | undefined {
  if (answer.stage !== null && Number.isInteger(answer.stage) && answer.stage >= 0 && answer.stage < spec.stages.length)
    return answer.stage;
  if (answer.part) {
    const focus = spec.stages.findIndex(stage => stage.focus === answer.part);
    if (focus >= 0) return focus;
    const included = spec.stages.findIndex(stage => stage.parts.includes(answer.part!));
    if (included >= 0) return included;
  }
  return undefined;
}
