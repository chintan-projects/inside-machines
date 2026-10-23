import test from 'node:test';
import assert from 'node:assert/strict';
import { OwnerAttempts } from '../web/owner-attempts.ts';

test('owner request transport recovery keeps its funded operation until an explicit new attempt',()=>{
  let count=0;
  const attempts=new OwnerAttempts(()=>`synthetic-owner-${++count}`);
  const first=attempts.operation('topic-request-one');
  assert.equal(attempts.operation('topic-request-one'),first);
  assert.notEqual(attempts.operation('topic-request-two'),first);
  assert.equal(attempts.operation('topic-request-one'),first);
  const next=attempts.operation('topic-request-one',true);
  assert.notEqual(next,first);
  assert.equal(attempts.operation('topic-request-one'),next);
  assert.equal(count,3);
});
