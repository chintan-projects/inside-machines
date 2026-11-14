import {readFileSync} from 'node:fs';
import {compileNarration} from './narrate.mjs';

/** Load either the editable complete storyboard or its public per-scene manifest. */
export function loadNarration(url = new URL('./narration.json',import.meta.url)) {
  const value=JSON.parse(readFileSync(url,'utf8'));
  if(value.scene_files){
    const {scene_files,...metadata}=value;
    const scenes=scene_files.map(file=>{
      if(!/^scenes\/[a-z_]+\.json$/.test(file))throw new Error('Invalid storyboard scene path.');
      return JSON.parse(readFileSync(new URL(file,url),'utf8'));
    });
    // Keep the same field order as the editable document, including trailing scope.
    const {transfer,model_scope,...header}=metadata;
    return compileNarration({...header,scenes,model_scope,transfer});
  }
  if(!Array.isArray(value.scenes))throw new Error('Narration needs scenes.');
  return compileNarration(value);
}
