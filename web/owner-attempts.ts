/** One funded intent keeps its operation across uncertain transport responses. */
export class OwnerAttempts {
  private readonly operations=new Map<string,string>();
  private readonly createOperation:()=>string;
  constructor(createOperation:()=>string=()=>crypto.randomUUID()) {this.createOperation=createOperation;}
  operation(intent:string,explicitNewAttempt=false):string {
    const prior=this.operations.get(intent);
    if(prior&&!explicitNewAttempt)return prior;
    const operation=this.createOperation();
    this.operations.set(intent,operation);
    return operation;
  }
}
