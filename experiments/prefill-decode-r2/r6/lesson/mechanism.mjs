// A declared untrained teaching calculator: two causal reading layers,
// scalar Q/K/V, simplified positive-part sharing and a one-unit local update.
// No layer norm, positional encoding, learned meaning or measured timings.
export const INPUTS=Object.freeze({The:1,sky:2,is:1.5,blue:-2,and:.5});
export const RULES=Object.freeze({query:.5,key:.25,value:.8,local:.5});
export const PROMPT=Object.freeze(['The','sky','is']);
export const CANDIDATES=Object.freeze([{word:'blue',weight:1},{word:'and',weight:-1}]);
export function score(result){
 const candidates=CANDIDATES.map(c=>({...c,score:c.weight*result}));
 return {candidates,word:candidates.reduce((a,b)=>b.score>a.score?b:a).word};
}
// Teaching rule only: one base part plus each match’s positive part.
// Actual transformer softmax uses exponentials; this preserves the data-flow graph.
export function sharing(matches){
 if(!Array.isArray(matches)||!matches.length||matches.some(x=>!Number.isFinite(x)||Math.abs(x)>=4))throw new RangeError('Use bounded finite toy matches.');
 const positiveMatches=matches.map(x=>Math.max(0,x)),parts=positiveMatches.map(x=>1+x),total=parts.reduce((a,b)=>a+b,0);
 return {positiveMatches,parts,total,shares:parts.map(x=>x/total)};
}
export function run({tokens=PROMPT,choices=2,cache=true}={}){
 if(!Array.isArray(tokens)||!tokens.length||tokens.some(x=>!Object.hasOwn(INPUTS,x)))throw new RangeError('Use known toy pieces.');
 if(!Number.isSafeInteger(choices)||choices<1||choices>16||typeof cache!=='boolean')throw new RangeError('Use 1–16 choices and a Boolean cache.');
 const text=[...tokens],passes=[],picks=[];let store=[[],[]];
 for(let step=0;step<choices;step++){
  if(step){text.push(picks.at(-1));if(!cache)store=[[],[]];}
  const positions=step&&cache?[text.length-1]:text.map((_,i)=>i);
  let inputs=positions.map(i=>INPUTS[text[i]]);const traces=positions.map(position=>({position,word:text[position],layers:[]}));
  for(let layer=0;layer<2;layer++){
   positions.forEach((position,i)=>{store[layer][position]={key:RULES.key*inputs[i],value:RULES.value*inputs[i]};});
   inputs=positions.map((position,i)=>{
    const input=inputs[i],query=RULES.query*input;
    const sources=store[layer].slice(0,position+1).map((kv,j)=>({word:text[j],position:j,...kv}));
    // All share arithmetic is exposed in the core; no numerical lookup is hidden.
    const matches=sources.map(s=>query*s.key),{positiveMatches,parts,total,shares}=sharing(matches);
    const contributions=sources.map((s,j)=>s.value*shares[j]);
    const blend=contributions.reduce((a,b)=>a+b,0),mixed=input+blend;
    const positive=Math.max(0,mixed),adjustment=RULES.local*positive,output=mixed+adjustment;
    traces[i].layers.push({layer,position,word:text[position],input,query,...store[layer][position],sources,matches,positiveMatches,parts,total,shares,contributions,blend,mixed,positive,adjustment,output});
    return output;
   });
  }
  const result=inputs.at(-1),selection=score(result);picks.push(selection.word);
  passes.push({text:[...text],positions:[...positions],traces,result,selection,cache:store.map(row=>row.map(kv=>({...kv}))),preparedPerLayer:[positions.length,positions.length]});
 }
 return {picks,passes};
}
export const KEPT=run();
export const CLEARED=run({cache:false});
export const format=(x,digits=3)=>Number(x).toFixed(digits);

/** Read an exact checkpoint, including an earlier position retained by the cache. */
export function traceAt(run,pass,position,layer){
 const entry=run.passes[pass].traces.find(x=>x.position===position)??run.passes[0].traces.find(x=>x.position===position);
 if(!entry||!entry.layers[layer])throw new RangeError('Unknown teaching checkpoint.');
 return entry.layers[layer];
}
export function context(b){
 const pass=b.pass??0,position=b.position??(pass?3:2),layer=b.layer??0;
 return {pass,position,layer,t:traceAt(KEPT,pass,position,layer),s:b.source_index};
}
