/** Local project scaffolding, inspection and explicit Studio execution. Only Studio narration may call a paid speech API. */
import {execFileSync} from 'node:child_process';
import {randomUUID} from 'node:crypto';
import {access, mkdir, mkdtemp, readFile, readdir, rename, rm, stat, writeFile} from 'node:fs/promises';
import {homedir, platform} from 'node:os';
import {isAbsolute, join, relative, resolve} from 'node:path';
import {pathToFileURL} from 'node:url';

const modes = new Set(['interactive', 'video', 'both']);
const help = `Explain Visually projects (init/status/doctor make no model/API calls)
  init <slug> [--topic "question"] [--mode interactive|video|both] [--root DIR]
  status <project-directory>
  doctor
  studio <command> [args...] (runs Studio; narrate may use the configured paid voice)
Default root: .explainers/ in the current workspace. Existing projects are never replaced.
The video budget covers speech only; host-model usage and account billing are separate.`;

async function exists(path) {
  try { await access(path); return true; }
  catch (error) { if (error.code === 'ENOENT') return false; throw error; }
}

export function projectOptions(args) {
  const [command, ...rest] = args;
  if (!command || command === '--help' || command === '-h') return {command: 'help'};
  if (command === 'doctor' && !rest.length) return {command};
  if (command === 'studio' && rest.length) return {command, args: rest};
  if (command === 'status' && rest.length === 1) return {command, path: resolve(rest[0])};
  if (command !== 'init') throw new Error('Use init, status, doctor, studio or --help.');
  const slug = rest.shift();
  if (!slug || !/^[a-z0-9][a-z0-9-]{0,62}$/.test(slug)) {
    throw new Error('Use a slug of 1–63 lowercase letters, digits and hyphens; no paths.');
  }
  const options = {command, slug, mode: 'interactive', topic: '', root: resolve('.explainers')};
  const seen = new Set();
  while (rest.length) {
    const key = rest.shift();
    if (!['--topic', '--mode', '--root'].includes(key) || seen.has(key)) {
      throw new Error('Unknown or repeated init option. See --help.');
    }
    seen.add(key);
    const value = rest.shift();
    if (!value || value.startsWith('--')) throw new Error('Each init option needs a value.');
    options[key.slice(2)] = key === '--root' ? resolve(value) : value;
  }
  if (!modes.has(options.mode)) throw new Error('Mode must be interactive, video or both.');
  if (options.topic.length > 4000) throw new Error('Keep the question below 4,000 characters.');
  return options;
}

export const narrationPreferencePath = join(homedir(), '.config', 'inside-explain', 'narration.json');

export function parseNarrationPreference(value) {
  const fields = ['schema_version', 'provider_name', 'model_id', 'voice_id', 'budget_usd', 'credential_source'];
  const models = ['eleven_v4', 'eleven_v4_turbo', 'eleven_multilingual_v2', 'eleven_v3'];
  if (!value || typeof value !== 'object' || Array.isArray(value)
    || Object.keys(value).some(key => !fields.includes(key)) || value.schema_version !== 1
    || value.provider_name !== 'elevenlabs' || !models.includes(value.model_id)
    || typeof value.voice_id !== 'string' || !/^[A-Za-z0-9_-]{20,64}$/.test(value.voice_id)
    || typeof value.budget_usd !== 'number' || !Number.isFinite(value.budget_usd)
    || value.budget_usd <= 0 || value.budget_usd > 10
    || value.credential_source !== 'macos-keychain') {
    throw new Error('Invalid local narration preference. Use ElevenLabs, a positive budget up to $10, and Keychain; never put keys in this file.');
  }
  return {...value};
}

export async function loadNarrationPreference(path = narrationPreferencePath) {
  let raw;
  try { raw = await readFile(path, 'utf8'); }
  catch (error) { if (error.code === 'ENOENT') return null; throw error; }
  let value;
  try { value = JSON.parse(raw); }
  catch { throw new Error('Local narration preference is not valid JSON. No fallback was selected.'); }
  return parseNarrationPreference(value);
}

export function studioEnvironment(preference, env = process.env, os = platform(), readKey = () =>
  execFileSync('/usr/bin/security', ['find-generic-password', '-s', 'elevenlabs-api-key', '-w'],
    {encoding: 'utf8', timeout: 12000, stdio: ['ignore', 'pipe', 'pipe']}).trim()) {
  parseNarrationPreference(preference);
  if (os !== 'darwin') throw new Error('This narration preference requires macOS Keychain. Configure Studio explicitly on another platform; no fallback was selected.');
  let key;
  try { key = readKey(); }
  catch { throw new Error('ElevenLabs Keychain credential is unavailable. No paid call or fallback was started.'); }
  if (typeof key !== 'string' || !key.trim()) throw new Error('ElevenLabs Keychain credential is empty.');
  return {...env, ELEVENLABS_API_KEY: key.trim()};
}

export function studioPlan(topic, os = platform(), preference = null) {
  const selected = preference ? parseNarrationPreference(preference) : null;
  const narration = selected
    ? `narration:\n  provider_name: elevenlabs\n  voice_id: ${JSON.stringify(selected.voice_id)}\n  model_id: ${selected.model_id}\n  voice_settings:\n    stability: 0.5\n    similarity_boost: 0.75`
    : os === 'darwin'
      ? 'narration:\n  provider_name: macos-say\n  voice: Samantha\n  words_per_minute: 165'
      : 'narration: null # Configure an available local voice explicitly before narration.';
  return `title: ${JSON.stringify(topic || 'Visual explanation')}
sources:
  - ../../CLAIMS.md
language_code: en
narration_budget_usd: ${selected?.budget_usd ?? 0}
${narration}
background_music:
  provider_name: none
has_end_credits: true
audience:
  description: A curious beginner; inferred starting level, not yet tested with a learner.
  unfamiliar_terms: []
goal: Answer one causal question and support a changed-situation prediction.
episodes:
  - id: ep01
    title: ${JSON.stringify(topic || 'Visual explanation')}
    question: ${JSON.stringify(topic || 'What changes, why, and what does it produce?')}
    question_type: mechanism
    presenter_name: theo
    estimated_duration_seconds: 180
    source_scope: Fill from the inspected primary sources in the shared claim ledger.
    taught_terms: []
    takeaway: Fill after designing the complete causal explanation.
    outline:
      - Start with one concrete example and prediction.
      - Show the input, necessary operations and useful output.
      - Reassemble the system and ask a transfer question before revealing.
`;
}

export async function createProject(options, os = platform(), preference = null) {
  const selected = options.mode !== 'interactive' && preference ? parseNarrationPreference(preference) : null;
  const destination = join(options.root, options.slug);
  await mkdir(options.root, {recursive: true});
  if (await exists(destination)) throw new Error('Project already exists. Use status and continue it.');
  const temporary = await mkdtemp(join(options.root, '.pending-explainer-'));
  try {
    const manifest = {
      schema_version: 1, id: randomUUID(), revision: 1, status: 'draft', mode: options.mode,
      question: options.topic, authoring: {model: null, authentication: 'host-managed', invoice_verified: false},
      narration: selected ? {provider_name: selected.provider_name, model_id: selected.model_id, voice_id: selected.voice_id} : null,
      costs: {speech_budget_usd: selected?.budget_usd ?? 0, speech_charged_usd: null, api_equivalent_usd: null},
      outputs: {interactive: 'interactive/index.html', video: 'video'},
      review: {engineering: 'not_run', technical: 'not_run', craft: 'not_run', learning: 'not_run'},
    };
    await writeFile(join(temporary, 'explanation.json'), JSON.stringify(manifest, null, 2) + '\n');
    await writeFile(join(temporary, 'BRIEF.md'), `# Learning brief\n\nQuestion: ${options.topic || 'To be filled from the request.'}\n\n- Audience and starting-level assumption:\n- One observable learner outcome:\n- Falsifiable learning hypothesis:\n- Complete input → operations/dependencies → useful output:\n- Prediction and reveal:\n- Transfer question, answer and 0/1/2 rubric:\n- Scope and omitted optional depth:\n- Intended viewing size and static alternative:\n`);
    await writeFile(join(temporary, 'CLAIMS.md'), '# Claim ledger\n\n| ID | Claim | Primary source/code location | Fact, illustration or inference | Scope/limits | Review |\n| --- | --- | --- | --- | --- | --- |\n');
    await writeFile(join(temporary, 'REVIEW.md'), '# Revision review\n\nRecord observed and inferred findings separately. Bind checks to the actual revision/output hashes.\n\n- Engineering:\n- Source correctness:\n- Craft/accessibility:\n- Beginner teach-back/transfer:\n- Output parity (interactive, narration, captions, cards):\n- Unresolved confusion and next change:\n- Actual model/runtime identity and usage receipt:\n- Verified charges vs API-equivalent estimates vs billing unknowns:\n- Owner decision (never infer approval):\n');
    await writeFile(join(temporary, '.gitignore'), '# Local outputs and private sessions\nexplainer-studio-versions.json\nexplainer-studio-versions.json.lock\n*.mp4\n*.wav\n*.aiff\n*.srt\n*.vtt\nlogs/\n**/narration/\n**/preview/\n**/render/\n.env*\n');
    if (options.mode !== 'video') await mkdir(join(temporary, 'interactive'));
    if (options.mode !== 'interactive') {
      const production = join(temporary, 'video', 'production');
      await mkdir(join(production, 'episodes', 'ep01', 'scenes'), {recursive: true});
      await writeFile(join(production, 'plan.yaml'), studioPlan(options.topic, os, selected));
    }
    // mkdir claims the target first: a concurrent init cannot replace a project created since the initial check.
    await mkdir(destination);
    try {
      for (const name of await readdir(temporary)) await rename(join(temporary, name), join(destination, name));
    } catch (error) {
      throw new Error('Project creation was interrupted; preserve the partial directory and inspect it.', {cause: error});
    }
    return {project: destination, mode: options.mode, status: 'draft', paid_calls: 0};
  } finally { await rm(temporary, {recursive: true, force: true}); }
}

function boundedPath(root, value) {
  if (typeof value !== 'string' || !value || isAbsolute(value)) throw new Error('Output paths must be project-relative.');
  const full = resolve(root, value);
  const rel = relative(root, full);
  if (rel === '..' || rel.startsWith('../') || isAbsolute(rel)) throw new Error('Output path escapes the project.');
  return full;
}

export async function projectStatus(directory) {
  const data = JSON.parse(await readFile(join(directory, 'explanation.json'), 'utf8'));
  if (data.schema_version !== 1 || !modes.has(data.mode) || !data.outputs) throw new Error('Unsupported project manifest.');
  const interactive = boundedPath(directory, data.outputs.interactive);
  const video = boundedPath(directory, data.outputs.video);
  const interactivePresent = await exists(interactive) && (await stat(interactive)).isFile();
  const videos = await exists(video) ? (await readdir(video, {withFileTypes: true}))
    .filter(entry => entry.isFile() && entry.name.endsWith('.mp4')).map(entry => entry.name) : [];
  return {project: directory, mode: data.mode, revision: data.revision, status: data.status,
    interactive_html_present: interactivePresent, delivered_video_files: videos,
    review: data.review, billing_verified: data.authoring?.invoice_verified === true};
}

export async function doctor() {
  const preference = await loadNarrationPreference();
  let studio = null;
  try {
    studio = execFileSync('explainer-studio', ['--version'], {encoding: 'utf8', timeout: 5000, stdio: ['ignore', 'pipe', 'ignore']}).trim();
  } catch { /* A missing or broken optional renderer does not disable interactive HTML. */ }
  const roots = [join(homedir(), '.codex', 'skills'), join(homedir(), '.agents', 'skills'),
    join(homedir(), '.claude', 'skills')];
  const anatomy = [];
  for (const root of roots) if (await exists(join(root, 'anatomy', 'SKILL.md'))) anatomy.push(join(root, 'anatomy'));
  return {node: process.version, platform: platform(), interactive: 'HTML/SVG authoring available through host tools',
    anatomy_locations: anatomy, studio_version_probe: studio,
    studio_dependencies: 'Run explainer-studio doctor --json before video production.',
    narration_default: preference ?? (platform() === 'darwin' ? 'macos-say, verify installed voice' : 'unset; choose a local voice explicitly'),
    paid_calls: 0, model_authentication: 'host-managed; billing not queried'};
}

export async function main(args) {
  const options = projectOptions(args);
  if (options.command === 'help') { process.stdout.write(help + '\n'); return; }
  if (options.command === 'studio') {
    const allowed = ['doctor', 'guide', 'plan', 'script', 'narrate', 'preview', 'render', 'notes', 'deliver', 'video'];
    if (!allowed.includes(options.args[0])) throw new Error('Unsupported Studio command. Use the Studio CLI directly for setup.');
    const preference = await loadNarrationPreference();
    const needsSpeech = options.args[0] === 'narrate' && !options.args.some(arg => ['--help', '-h'].includes(arg));
    const env = needsSpeech && preference ? studioEnvironment(preference) : process.env;
    try { execFileSync('explainer-studio', options.args, {env, stdio: 'inherit'}); }
    catch { throw new Error('Studio did not complete. Inspect its saved state before retrying narration; no fallback was selected.'); }
    return;
  }
  const preference = options.command === 'init' && options.mode !== 'interactive' ? await loadNarrationPreference() : null;
  const result = options.command === 'init' ? await createProject(options, platform(), preference)
    : options.command === 'status' ? await projectStatus(options.path) : await doctor();
  process.stdout.write(JSON.stringify(result, null, 2) + '\n');
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  main(process.argv.slice(2)).catch(error => {
    process.stderr.write(JSON.stringify({error: error.message}) + '\n');
    process.exitCode = 1;
  });
}
