/** Revision binding and unresolved-confusion guard, not an automated teaching grader. */
import {createHash} from 'node:crypto';
import {readFile,access} from 'node:fs/promises';
import {dirname,isAbsolute,relative,resolve,join} from 'node:path';

const sha256 = bytes => createHash('sha256').update(bytes).digest('hex');

export function validateTeachingReadiness(review, script) {
  if (!review || review.schema_version!==1 || review.review_kind!=='fresh_automated_reader'
      || typeof review.reviewer_id!=='string' || !review.reviewer_id.trim()
      || !Array.isArray(review.findings)) throw new Error('A genuine fresh-reader record is required before narration or handoff.');
  if(review.findings.some(item=>!item||!['core','depth'].includes(item.scope)
    ||!['lost','wrong','minor'].includes(item.kind)||!['open','fixed','kept'].includes(item.status))) {
    throw new Error('Each teaching finding needs a valid kind, scope and status.');
  }
  if (review.script_sha256!==sha256(script)) throw new Error('Teaching review is stale. Review the changed script before narration or handoff.');
  if (review.causal_teachback!=='pass' || review.novel_transfer!=='pass') {
    throw new Error('Fix causal teach-back and novel transfer before narration or handoff.');
  }
  const pending=review.findings.filter(item=>item.scope==='core' && ['lost','wrong'].includes(item.kind)
    && item.status!=='fixed');
  if (pending.length) throw new Error('Unresolved core confusion blocks narration and handoff. Rewrite and obtain a fresh read; a review-round limit is not acceptance.');
  return {automated_core:'passed', human_acceptance:false};
}

async function present(path) {
  try {await access(path);return true;}
  catch(error){if(error.code==='ENOENT')return false;throw error;}
}

function bounded(root,path) {
  if(typeof path!=='string'||!path||isAbsolute(path))throw new Error('Teaching gate paths must be project-relative.');
  const full=resolve(root,path),rel=relative(root,full);
  if(rel==='..'||rel.startsWith('../')||isAbsolute(rel))throw new Error('Teaching gate path escapes the project.');
  return full;
}

export async function enforceTeachingReadiness(args,cwd=process.cwd()) {
  if(!['narrate','deliver'].includes(args[0])||args.some(arg=>['--help','-h'].includes(arg)))return null;
  let series;
  const index=args.indexOf('--series'),joined=args.filter(arg=>arg.startsWith('--series='));
  if(joined.length>1||(joined.length&&index>=0)||args.lastIndexOf('--series')!==index)throw new Error('Use one series directory.');
  if(joined.length){const value=joined[0].slice('--series='.length);if(!value)throw new Error('Missing series directory.');series=resolve(cwd,value);}
  else if(index>=0){if(!args[index+1])throw new Error('Missing series directory.');series=resolve(cwd,args[index+1]);}
  else {
    let current=resolve(cwd);
    while(true){if(await present(join(current,'production','plan.yaml'))){series=current;break;}const parent=dirname(current);if(parent===current)break;current=parent;}
  }
  if(!series)return null; // Non-helper projects retain Studio's native review contract.
  const root=dirname(series),manifestPath=join(root,'explanation.json');
  if(!await present(manifestPath))return null;
  const manifest=JSON.parse(await readFile(manifestPath,'utf8'));
  if(!manifest.teaching_gate)return null; // Preserve explicit legacy project behavior.
  const episode=args[1];
  if(typeof episode!=='string'||!/^[a-zA-Z0-9_-]+$/.test(episode))throw new Error('Use an explicit episode ID for teaching review.');
  const review=JSON.parse(await readFile(bounded(root,manifest.teaching_gate),'utf8'));
  if(review.episode!==episode)throw new Error('Teaching review belongs to a different episode.');
  const script=await readFile(join(series,'production','episodes',episode,'script.yaml'));
  return validateTeachingReadiness(review,script);
}
