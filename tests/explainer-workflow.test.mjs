import {test} from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {cp, lstat, mkdir, mkdtemp, readFile, realpath, readdir, rm, symlink, writeFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join, resolve} from 'node:path';
import {createProject, projectOptions, projectStatus, studioPlan, loadNarrationPreference, parseNarrationPreference, studioEnvironment} from '../plugins/inside-explain/skills/explain-visually/scripts/project.mjs';
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

const paidPreference = {schema_version: 1, provider_name: 'elevenlabs', model_id: 'eleven_v4',
  voice_id: 'EXAVITQu4vr4xnSDxMaL', budget_usd: 1, credential_source: 'macos-keychain'};

test('explicit local narration selection reaches the plan and receipt but does not enable speech for interactive mode', async t => {
  const root = await temporary(t);
  const video = await createProject(projectOptions(['init', 'selected', '--root', root, '--mode', 'video']), 'darwin', paidPreference);
  const data = JSON.parse(await readFile(join(video.project, 'explanation.json'), 'utf8'));
  assert.equal(data.costs.speech_budget_usd, 1);
  assert.equal(data.narration.provider_name, 'elevenlabs');
  assert.equal(data.narration.model_id, 'eleven_v4');
  const plan = await readFile(join(video.project, 'video/production/plan.yaml'), 'utf8');
  assert.match(plan, /narration_budget_usd: 1/);
  assert.match(plan, /provider_name: elevenlabs/);
  assert.doesNotMatch(plan, /macos-say/);
  assert.equal(data.costs.speech_charged_usd, null);
  const interactive = await createProject(projectOptions(['init', 'drawing', '--root', root]), 'darwin', paidPreference);
  const plain = JSON.parse(await readFile(join(interactive.project, 'explanation.json'), 'utf8'));
  assert.equal(plain.costs.speech_budget_usd, 0);
  assert.equal(plain.narration, null);
});

test('absent preferences keep free defaults; malformed or secret-containing preferences fail closed', async t => {
  const root = await temporary(t), file = join(root, 'narration.json');
  assert.equal(await loadNarrationPreference(file), null);
  await writeFile(file, JSON.stringify(paidPreference));
  assert.deepEqual(await loadNarrationPreference(file), paidPreference);
  for (const change of [{api_key: 'a-private-test-value'}, {model_id: 'untrusted-model'}, {budget_usd: 0},
    {budget_usd: 1000}, {budget_usd: '1'}, {voice_id: '../private'}, {credential_source: 'arbitrary-command'}]) {
    assert.throws(() => parseNarrationPreference({...paidPreference, ...change}), /Invalid local narration/);
  }
  await writeFile(file, '{invalid');
  await assert.rejects(loadNarrationPreference(file), /No fallback/);
});

test('Keychain credential is passed only through a copied environment and takes precedence over inherited credentials', () => {
  const inherited = {PATH: '/trusted/bin', ELEVENLABS_API_KEY: 'another-account-test-value'};
  let reads = 0;
  const child = studioEnvironment(paidPreference, inherited, 'darwin', () => {reads++; return 'selected-test-secret';});
  assert.equal(reads, 1);
  assert.equal(child.ELEVENLABS_API_KEY, 'selected-test-secret');
  assert.equal(inherited.ELEVENLABS_API_KEY, 'another-account-test-value');
  assert.equal(child.PATH, inherited.PATH);
  assert.throws(() => studioEnvironment(paidPreference, inherited, 'linux', () => {throw new Error('unreachable');}), /requires macOS Keychain/);
  assert.throws(() => studioEnvironment(paidPreference, {}, 'darwin', () => {throw new Error('sensitive raw diagnostic');}),
    error => error.message.includes('No paid call') && !error.message.includes('sensitive'));
});

test('CLI video init reads its local preference while interactive init ignores an invalid paid preference', async t => {
  const home = await temporary(t), root = join(home, 'outputs');
  const directory = join(home, '.config/inside-explain');
  await mkdir(directory, {recursive: true});
  const file = join(directory, 'narration.json');
  await writeFile(file, JSON.stringify(paidPreference));
  const helper = resolve('plugins/inside-explain/skills/explain-visually/scripts/project.mjs');
  const env = {...process.env, HOME: home};
  execFileSync(process.execPath, [helper, 'init', 'movie', '--mode', 'video', '--root', root], {env, stdio: 'pipe'});
  const data = JSON.parse(await readFile(join(root, 'movie/explanation.json'), 'utf8'));
  assert.equal(data.narration.provider_name, 'elevenlabs');
  await writeFile(file, '{invalid');
  execFileSync(process.execPath, [helper, 'init', 'drawing', '--root', root], {env, stdio: 'pipe'});
  assert.throws(() => execFileSync(process.execPath, [helper, 'init', 'rejected', '--mode', 'video', '--root', root], {env, stdio: 'pipe'}));
  await assert.rejects(lstat(join(root, 'rejected')), {code: 'ENOENT'});
});
