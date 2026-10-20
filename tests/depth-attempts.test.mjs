import test from 'node:test';
import assert from 'node:assert/strict';
import { DepthAttempts } from '../web/depth-attempts.ts';

test('a response lost after admission reuses the same funded operation',()=>{
  let count=0;
  const attempts=new DepthAttempts(()=>`synthetic-operation-${++count}`);
  const intent={rootId:'system-core',role:'insight',question:'Why does this relationship change the output?'};
  const admitted=attempts.operation(intent);
  assert.equal(attempts.operation(intent),admitted);
  assert.equal(attempts.operation({...intent,question:` ${intent.question} `}),admitted);
  assert.equal(count,1);
  assert.notEqual(attempts.operation(intent,true),admitted);
  assert.equal(count,2);
});
test('returning to the same question retains its attempt across other root and depth selections',()=>{
  let count=0;
  const attempts=new DepthAttempts(()=>`synthetic-operation-${++count}`);
  const intent={rootId:'system-core',role:'insight',question:'Why does this relationship change the output?'};
  const first=attempts.operation(intent);
  const otherRoot=attempts.operation({...intent,rootId:'another-core'});
  const otherRole=attempts.operation({...intent,role:'model'});
  const otherQuestion=attempts.operation({...intent,question:'How does this equation constrain the result?'});
  assert.equal(new Set([first,otherRoot,otherRole,otherQuestion]).size,4);
  assert.equal(attempts.operation(intent),first);
  assert.equal(count,4);
});
