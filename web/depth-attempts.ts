/** Ephemeral owner intent tokens; repeating a transport request keeps its paid operation. */
import { OwnerAttempts } from './owner-attempts.ts';
export interface DepthIntent {
  readonly rootId:string;
  readonly role:'insight'|'model';
  readonly question:string;
}
export function depthIntentKey(intent:DepthIntent):string {
  return JSON.stringify([intent.rootId,intent.role,intent.question.trim()]);
}
export class DepthAttempts {
  private readonly attempts:OwnerAttempts;
  constructor(createOperation:()=>string=()=>crypto.randomUUID()) {this.attempts=new OwnerAttempts(createOperation);}
  operation(intent:DepthIntent,explicitNewAttempt=false):string {
    return this.attempts.operation(depthIntentKey(intent),explicitNewAttempt);
  }
}
