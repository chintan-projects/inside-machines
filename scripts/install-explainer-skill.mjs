/** Install the versioned skill for local Claude Code / Codex discovery, without changing account settings. */
import {lstat, mkdir, realpath, rename, symlink} from 'node:fs/promises';
import {homedir} from 'node:os';
import {dirname, join, resolve} from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {randomUUID} from 'node:crypto';

const repository = resolve(dirname(fileURLToPath(import.meta.url)), '..');
export const skillSource = join(repository, 'plugins', 'inside-explain', 'skills', 'explain-visually');

async function present(path) {
  try { await lstat(path); return true; }
  catch (error) { if (error.code === 'ENOENT') return false; throw error; }
}

export async function installSkill({home = homedir(), client = 'both', replace = false, check = false,
  codexHome = process.env.CODEX_HOME, source = skillSource} = {}) {
  if (!['both', 'codex', 'claude'].includes(client)) throw new Error('Client must be both, codex or claude.');
  const canonical = await realpath(source);
  if (!await present(join(canonical, 'SKILL.md'))) throw new Error('Skill source is missing SKILL.md.');
  const legacy = join(home, '.codex', 'skills', 'explain-visually');
  const codex = codexHome ? join(resolve(codexHome), 'skills', 'explain-visually')
    : await present(legacy) ? legacy : join(home, '.agents', 'skills', 'explain-visually');
  const targets = [
    ...(client !== 'claude' ? [{client: 'codex', path: codex}] : []),
    ...(client !== 'codex' ? [{client: 'claude', path: join(home, '.claude', 'skills', 'explain-visually')}] : []),
  ];
  // Preflight every target before mutating either discovery root.
  const plan = [];
  for (const target of targets) {
    let pointsAtSource = false;
    const exists = await present(target.path);
    if (exists) {
      try { pointsAtSource = await realpath(target.path) === canonical; }
      catch (error) { if (error.code !== 'ENOENT') throw error; }
    }
    if (exists && !pointsAtSource && !replace && !check) {
      throw new Error(`Existing ${target.client} skill preserved. Use --replace to back it up before updating.`);
    }
    plan.push({...target, exists, pointsAtSource});
  }
  if (check) return {source: canonical, installed: plan.every(x => x.pointsAtSource), targets: plan};
  const backups = join(home, '.local', 'state', 'inside-explain', 'skill-backups');
  const results = [];
  for (const target of plan) {
    if (target.pointsAtSource) { results.push({...target, action: 'unchanged'}); continue; }
    let backup = null;
    if (target.exists) {
      await mkdir(backups, {recursive: true});
      backup = join(backups, `${target.client}-${Date.now()}-${randomUUID()}`);
      await rename(target.path, backup);
    }
    await mkdir(dirname(target.path), {recursive: true});
    try { await symlink(canonical, target.path, 'dir'); }
    catch (error) {
      if (backup) await rename(backup, target.path);
      throw error;
    }
    results.push({client: target.client, path: target.path, action: 'installed', backup});
  }
  return {source: canonical, installed: true, targets: results, restart: 'Start a new agent session to refresh discovery.'};
}

async function main(args) {
  if (args.includes('--help')) {
    process.stdout.write('Install the shared skill: [--client both|codex|claude] [--replace] [--check] [--home DIR]\n--replace preserves existing skills outside discovery roots. No account settings, dependencies or model calls.\n');
    return;
  }
  const options = {};
  while (args.length) {
    const arg = args.shift();
    if (arg === '--replace') options.replace = true;
    else if (arg === '--check') options.check = true;
    else if (arg === '--client' || arg === '--home') {
      const value = args.shift();
      if (!value || value.startsWith('--')) throw new Error('Missing installation option value.');
      options[arg.slice(2)] = arg === '--home' ? resolve(value) : value;
      if (arg === '--home') options.codexHome = null; // Isolated fixtures must not inherit the real user's root.
    } else throw new Error('Unknown installation option. See --help.');
  }
  process.stdout.write(JSON.stringify(await installSkill(options), null, 2) + '\n');
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  main(process.argv.slice(2)).catch(error => { process.stderr.write(JSON.stringify({error: error.message}) + '\n'); process.exitCode = 1; });
}
