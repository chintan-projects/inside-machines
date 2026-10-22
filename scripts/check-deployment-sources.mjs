/** Check directory traversal as well as leaf matches before a Vercel source upload. */
import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import ignore from 'ignore';

const defaults=['.git','.hg','.svn','.gitmodules','.vercel','node_modules','.env.local','.env.*.local'];

export function excludedUploadSources(rules,paths) {
  const filter=ignore().add(defaults).add(rules),excluded=[];
  for(const file of paths) {
    const parts=file.split('/');
    for(let i=1;i<=parts.length;i++) {
      const ancestor=parts.slice(0,i).join('/');
      if(filter.ignores(ancestor)){excluded.push({file,blockedAt:ancestor});break;}
    }
  }
  return excluded;
}

if(process.argv[1]&&import.meta.url===pathToFileURL(resolve(process.argv[1])).href) {
  const registry=JSON.parse(readFileSync('native/registry.json','utf8'));
  const paths=[...new Set(registry.renderers.flatMap(entry=>entry.sources.map(source=>source.path))),
    'native/registry.json','native/specs.json','vendor/anatomy/LICENSE','public/licenses/anatomy-MIT.txt'];
  const excluded=excludedUploadSources(readFileSync('.vercelignore','utf8'),paths);
  if(excluded.length)throw new Error(`Vercel source upload prunes required artwork: ${JSON.stringify(excluded)}`);
  process.stdout.write(`Verified upload traversal for ${paths.length} required native sources and notices.\n`);
}
