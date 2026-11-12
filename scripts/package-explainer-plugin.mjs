/** Build a clean skills-only ZIP. Explicit allowlist; never includes experiment media, sessions or credentials. */
import {execFileSync} from 'node:child_process';
import {copyFile, lstat, mkdir, mkdtemp, readFile, readdir, rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {dirname, join, resolve} from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const allowedSkills = new Set([
  'explain-visually/SKILL.md', 'explain-visually/agents/openai.yaml',
  'explain-visually/references/computing.md', 'explain-visually/references/interactive.md',
  'explain-visually/references/video.md', 'explain-visually/references/chat.md',
  'explain-visually/scripts/project.mjs',
]);

async function copySkill(source, destination, prefix = '') {
  await mkdir(destination, {recursive: true});
  for (const entry of await readdir(source, {withFileTypes: true})) {
    const path = join(source, entry.name);
    const logical = prefix + entry.name;
    if (entry.isSymbolicLink()) throw new Error('Release packages must not contain symlinks.');
    if (entry.name.startsWith('.') || ['logs', 'node_modules', '__pycache__'].includes(entry.name)) {
      throw new Error('A private or generated directory was found in the skill package.');
    }
    if (entry.isDirectory() && [...allowedSkills].some(item => item.startsWith(logical + '/'))) {
      await copySkill(path, join(destination, entry.name), logical + '/');
    }
    else if (entry.isFile() && allowedSkills.has(logical)) await copyFile(path, join(destination, entry.name));
    else throw new Error('Unexpected file type in the skill package.');
  }
}

export async function packagePlugin({source = join(root, 'plugins', 'inside-explain'), output} = {}) {
  const manifest = JSON.parse(await readFile(join(source, 'plugin.json'), 'utf8'));
  if (manifest.name !== 'inside-explain' || !/^\d+\.\d+\.\d+$/.test(manifest.version)) throw new Error('Invalid release identity.');
  const destination = resolve(output || join(root, '.vercel', 'plugin-release', `${manifest.name}-${manifest.version}.zip`));
  try { await lstat(destination); throw new Error('Release archive already exists; choose a new output path or version.'); }
  catch (error) { if (error.code !== 'ENOENT') throw error; }
  const stage = await mkdtemp(join(tmpdir(), 'inside-explain-package-'));
  try {
    for (const file of ['plugin.json', '.claude-plugin/plugin.json', '.codex-plugin/plugin.json', 'README.md', 'LICENSE']) {
      const input = join(source, file);
      if (!(await lstat(input)).isFile() || (await lstat(input)).isSymbolicLink()) throw new Error('Expected a regular release source file.');
      await mkdir(dirname(join(stage, file)), {recursive: true});
      await copyFile(input, join(stage, file));
    }
    await copySkill(join(source, 'skills'), join(stage, 'skills'));
    await mkdir(dirname(destination), {recursive: true});
    execFileSync('zip', ['-q', '-r', destination, '.'], {cwd: stage, timeout: 30000, stdio: ['ignore', 'pipe', 'pipe']});
    return {archive: destination, version: manifest.version, published: false};
  } finally { await rm(stage, {recursive: true, force: true}); }
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  const args = process.argv.slice(2);
  if (args.length && (args[0] !== '--output' || args.length !== 2)) {
    process.stderr.write('Usage: node scripts/package-explainer-plugin.mjs [--output FILE.zip]\n'); process.exitCode = 1;
  } else packagePlugin({output: args[1]}).then(result => process.stdout.write(JSON.stringify(result, null, 2) + '\n'))
    .catch(error => { process.stderr.write(JSON.stringify({error: error.message}) + '\n'); process.exitCode = 1; });
}
