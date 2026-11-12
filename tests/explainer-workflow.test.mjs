import {test} from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {cp, lstat, mkdir, mkdtemp, readFile, realpath, readdir, rm, symlink, writeFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join, resolve} from 'node:path';
import {createProject, projectOptions, projectStatus, studioPlan} from '../plugins/inside-explain/skills/explain-visually/scripts/project.mjs';
import {installSkill, skillSource} from '../scripts/install-explainer-skill.mjs';
import {packagePlugin} from '../scripts/package-explainer-plugin.mjs';

async function temporary(t) {
  const dir = await mkdtemp(join(tmpdir(), 'inside-explain-test-'));
  t.after(() => rm(dir, {recursive: true, force: true}));
  return dir;
}

test('project init refuses path traversal and unsupported modes before writing', () => {
  for (const slug of ['../elsewhere', '/absolute', '.', 'a/b', 'A']) {
    assert.throws(() => projectOptions(['init', slug]));
  }
  assert.throws(() => projectOptions(['init', 'safe', '--mode', 'automatic-paid-video']));
  assert.throws(() => projectOptions(['init', 'safe', '--root']));
});

test('a saved project has zero speech budget and a coherent continuation status', async t => {
  const root = await temporary(t);
  const options = projectOptions(['init', 'gpu', '--root', root, '--mode', 'both', '--topic', 'Why wait for an input?']);
  const result = await createProject(options, 'darwin');
  const data = JSON.parse(await readFile(join(result.project, 'explanation.json'), 'utf8'));
  assert.equal(data.costs.speech_budget_usd, 0);
  assert.equal(data.authoring.invoice_verified, false);
  const status = await projectStatus(result.project);
  assert.equal(status.interactive_html_present, false);
  assert.deepEqual(status.delivered_video_files, []);
  await writeFile(join(result.project, 'interactive', 'index.html'), '<!doctype html><p>Local content</p>');
  assert.equal((await projectStatus(result.project)).interactive_html_present, true);
  assert.equal((await projectStatus(result.project)).review.learning, 'not_run');
  const production = join(result.project, 'video', 'production');
  const plan = await readFile(join(production, 'plan.yaml'), 'utf8');
  assert.match(plan, /provider_name: macos-say/);
  const source = plan.match(/sources:\n  - (.+)/)?.[1];
  assert.ok(source, 'Studio requires a source, including in the initial skeleton.');
  assert.equal(await realpath(resolve(production, source)), await realpath(join(result.project, 'CLAIMS.md')));
  await writeFile(join(result.project, 'CLAIMS.md'), 'A revised shared source claim');
  assert.equal(await readFile(resolve(production, source), 'utf8'), 'A revised shared source claim');
});

test('repeated init preserves existing work rather than silently replacing it', async t => {
  const root = await temporary(t);
  const options = projectOptions(['init', 'saved', '--root', root]);
  await createProject(options);
  const path = join(root, 'saved', 'BRIEF.md');
  await writeFile(path, 'An existing personal explanation');
  await assert.rejects(createProject(options), /already exists/);
  assert.equal(await readFile(path, 'utf8'), 'An existing personal explanation');
});

test('topics remain data, and non-Mac plans never silently choose paid speech', async t => {
  const root = await temporary(t);
  const sentinel = join(root, 'should-not-exist');
  const topic = `A: "quote"\n$(touch ${sentinel})`;
  const options = projectOptions(['init', 'quoted', '--root', root, '--mode', 'video', '--topic', topic]);
  await createProject(options, 'linux');
  assert.equal(JSON.parse(await readFile(join(root, 'quoted', 'explanation.json'), 'utf8')).question, topic);
  await assert.rejects(lstat(sentinel), {code: 'ENOENT'});
  const plan = studioPlan(topic, 'linux');
  assert.match(plan, /narration: null/);
  assert.doesNotMatch(plan, /provider_name: (openai|elevenlabs|voai)/);
});

test('status rejects a tampered output path outside the local project', async t => {
  const root = await temporary(t);
  const result = await createProject(projectOptions(['init', 'scope', '--root', root]));
  const file = join(result.project, 'explanation.json');
  const data = JSON.parse(await readFile(file, 'utf8'));
  data.outputs.interactive = '../../private.html';
  await writeFile(file, JSON.stringify(data));
  await assert.rejects(projectStatus(result.project), /escapes/);
});

test('installer preflight preserves custom skills and unrelated configuration', async t => {
  const home = await temporary(t);
  const custom = join(home, '.claude', 'skills', 'explain-visually');
  await mkdir(custom, {recursive: true});
  await writeFile(join(custom, 'SKILL.md'), 'My custom workflow');
  await assert.rejects(installSkill({home, codexHome: null}), /preserved/);
  await assert.rejects(lstat(join(home, '.agents/skills/explain-visually')), {code: 'ENOENT'});
  assert.equal(await readFile(join(custom, 'SKILL.md'), 'utf8'), 'My custom workflow');
  await assert.rejects(lstat(join(home, '.claude/settings.json')), {code: 'ENOENT'});
});

test('installer backs up outside discovery roots, shares canonical content and is idempotent', async t => {
  const home = await temporary(t);
  const old = join(home, '.codex', 'skills', 'explain-visually');
  await mkdir(old, {recursive: true}); await writeFile(join(old, 'SKILL.md'), 'Old skill');
  const installed = await installSkill({home, codexHome: null, replace: true});
  assert.equal(await readFile(join(installed.targets[0].backup, 'SKILL.md'), 'utf8'), 'Old skill');
  assert.ok(installed.targets[0].backup.startsWith(join(home, '.local', 'state')));
  assert.equal(await realpath(old), await realpath(skillSource));
  assert.equal(await realpath(join(home, '.claude/skills/explain-visually')), await realpath(skillSource));
  const again = await installSkill({home, codexHome: null});
  assert.ok(again.targets.every(item => item.action === 'unchanged'));
  assert.equal((await installSkill({home, codexHome: null, check: true})).installed, true);
});

test('install check is read-only and does not create discovery directories', async t => {
  const home = await temporary(t);
  assert.equal((await installSkill({home, codexHome: null, check: true})).installed, false);
  assert.deepEqual(await readdir(home), []);
});

test('release ZIP contains working resources and excludes experiment media and account files', async t => {
  const root = await temporary(t);
  const output = join(root, 'release.zip');
  await packagePlugin({output});
  const entries = execFileSync('unzip', ['-Z1', output], {encoding: 'utf8'}).split('\n');
  assert.ok(entries.includes('skills/explain-visually/scripts/project.mjs'));
  assert.ok(entries.includes('skills/explain-visually/references/video.md'));
  assert.ok(entries.includes('LICENSE'));
  assert.ok(entries.every(name => !/\.mp4$|\.env|claude-stream|auth\.json|^experiments\//.test(name)));
  await assert.rejects(packagePlugin({output}), /already exists/);
});

test('release builder refuses a secret-like unexpected file and symlink inside skills', async t => {
  const root = await temporary(t);
  const source = join(root, 'plugin');
  await cp(resolve('plugins/inside-explain'), source, {recursive: true});
  const bad = join(source, 'skills/explain-visually/references/credentials.json');
  await writeFile(bad, '{"private":"not a real credential"}');
  await assert.rejects(packagePlugin({source, output: join(root, 'bad.zip')}), /Unexpected/);
  await rm(bad);
  await symlink(join(root, 'outside'), bad);
  await assert.rejects(packagePlugin({source, output: join(root, 'bad.zip')}), /symlinks/);
});
