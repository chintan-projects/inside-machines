import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {excludedUploadSources} from '../scripts/check-deployment-sources.mjs';

test('upload traversal rejects a pruned directory even when the child file is explicitly included',()=>{
  const rules='vendor/anatomy/*\n!vendor/anatomy/kit/\n!vendor/anatomy/kit/**\n';
  assert.deepEqual(excludedUploadSources(rules,['vendor/anatomy/kit/iso-kit.ts']),[
    {file:'vendor/anatomy/kit/iso-kit.ts',blockedAt:'vendor/anatomy/kit'},
  ]);
});
test('actual upload rules include every registered native source while excluding private inputs',()=>{
  const rules=readFileSync('.vercelignore','utf8');
  const registry=JSON.parse(readFileSync('native/registry.json','utf8'));
  const sources=registry.renderers.flatMap(entry=>entry.sources.map(source=>source.path));
  assert.deepEqual(excludedUploadSources(rules,[...sources,'vendor/anatomy/LICENSE']),[]);
  for(const path of ['.env.local','.data/inside.sqlite3','.vercel/native-production/target-production.env','vendor/anatomy/.git/config'])
    assert.equal(excludedUploadSources(rules,[path]).length,1,path);
});
