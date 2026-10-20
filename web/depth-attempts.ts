/** Ephemeral owner intent tokens; repeating a transport request keeps its paid operation. */
export interface DepthIntent {
  readonly rootId:string;
  readonly role:'insight'|'model';
  readonly question:string;
}
export function depthIntentKey(intent:DepthIntent):string {
  return JSON.stringify([intent.rootId,intent.role,intent.question.trim()]);
}
export class DepthAttempts {
  private readonly operations=new Map<string,string>();
  private readonly createOperation:()=>string;
  constructor(createOperation:()=>string=()=>crypto.randomUUID()) {this.createOperation=createOperation;}
  operation(intent:DepthIntent,explicitNewAttempt=false):string {
    const key=depthIntentKey(intent);
    const prior=this.operations.get(key);
    if(prior&&!explicitNewAttempt)return prior;
    const operation=this.createOperation();
    this.operations.set(key,operation);
    return operation;
  }
}
