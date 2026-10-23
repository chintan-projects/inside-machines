// Explicit, reproducible integration repairs; the immutable API response is retained.
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
const dir=new URL('../../.vercel/claude-vacuum/private/',import.meta.url);
const original=await readFile(new URL('gpu-art-1.txt',dir),'utf8');
let code=original.trim().replace(/^```(?:js|javascript)\s*\n/,'').replace(/\n```$/,'');
const changes=['Remove model-added Markdown fences; preserve the original response.'];
const replace=(before,after,reason)=>{
  if(code.split(before).length!==2)throw new Error('Repair anchor mismatch: '+reason);
  code=code.replace(before,after);changes.push(reason);
};
replace("{ text: 'GPU chip', x: clampX(gpuPt[0] + 110), y: clampY(gpuPt[1] - 70) }",
  "{ text: 'GPU chip', x: 260, y: 210 }",'Separate chip and memory labels at phone width.');
replace("{ text: 'Memory', x: clampX(memPt[0] + 70), y: clampY(memPt[1] - 60) }",
  "{ text: 'Memory', x: 540, y: 180 }",'Give memory its own anchored label position.');
replace("{ text: 'Connection to computer', x: clampX(conPt[0] - 20), y: clampY(conPt[1] + 60) }",
  "{ text: 'Connection to computer', x: 260, y: 480 }",'Keep the connector label within the phone frame.');
replace('const laneY0 = 150, laneH = 66, laneGap = 12;',
  'const laneY0 = 178, laneH = 60, laneGap = 8;', 'Keep prerequisite legend clear of the first execution row.');
replace('rect(16, 134, 688, 4 * laneH + 3 * laneGap + 26',
  'rect(16, 166, 688, 4 * laneH + 3 * laneGap + 26','Align execution enclosure with its moved rows.');
replace("label = j.prerequisite ? 'needs ' + j.prerequisite : 'no data';",
  "label = j.prerequisite ? '← ' + j.prerequisite : '—';",'Keep missing-input labels inside their own cell at phone scale.');
replace("MUTE = '#8b8570'", "MUTE = '#51554a'",'Increase waiting/disabled text contrast.');
replace("COPPER = '#b4693a'", "COPPER = '#8b4a22'",'Meet the normal-text contrast target for prerequisite captions.');
replace("ln.enabled ? SIL : '#9aa0a5'", "ln.enabled ? SIL : '#5d656b'",'Keep unavailable-lane text readable on its gray label.');
replace("s += txt(640, y + 44, done ? 'Done' : 'Running', 24, done ? GREEN : COPPER, 'middle', 700);",
  '// Status already appears once on the lane label.', 'Remove a duplicate status that crowded the calculation.');
replace("s += rect(168, y + 8, 500 * p, laneH - 16, 8, done ? '#cfe5d2' : '#fbd9bb', 'none', 0);",
  "s += rect(168, y + 8, 500 * p, laneH - 16, 8, done ? '#cfe5d2' : '#fbd9bb', 'none', 0, 'data-progress=\"true\"');",
  'Expose progress bars for stable DOM updates while arithmetic labels stay mounted.');
replace("s += txt(30, 22, 'Inputs', 24, INK, 'start', 700);",
  "s += txt(30, 22, 'Pixel inputs: a brightness number for each', 24, INK, 'start', 700);",'Identify what the numerical input represents.');
replace("    const jobById = {};", `    // Nine illustrative gray levels make the arithmetic's visual job visible.
    const pixelShade=v=>'rgb('+[45+v*25,45+v*25,45+v*25].join(',')+')';
    const pixelInk=v=>v<3?'#fffdf5':'#000000';
    const jobById = {};`, 'Connect toy brightness numbers to visible pixel shades.');
replace("      s += rect(x, inY, 72, inH - 8, 8, fill, stroke, j.status === 'running' ? 4 : 2.5, extra);",
  "      if(j.input!==null)fill=pixelShade(j.input);\n      const inputInk=j.input===null?INK:pixelInk(j.input);\n      s += rect(x, inY, 72, inH - 8, 8, fill, stroke, j.status === 'running' ? 4 : 2.5, extra);",
  'Keep input pixels at their own brightness; state remains encoded by outline and lane/status.');
replace("s += txt(cx(i), inY + 30, j.id, 30, INK, 'middle', 700);",
  "s += txt(cx(i), inY + 30, j.id, 30, inputInk, 'middle', 700);",'Keep input IDs readable on their pixel.');
replace("s += txt(cx(i), inY + 58, String(j.input), 32, SILD, 'middle', 700);",
  "s += txt(cx(i), inY + 58, String(j.input), 32, inputInk, 'middle', 700);",'Keep brightness numbers readable.');
replace("done ? '#e3efe4' : '#f2eee2', done ? GREEN : MUTE",
  "done ? pixelShade(j.output) : '#f2eee2', done ? GREEN : MUTE",'Completed results show the computed brighter pixel.');
replace("s += txt(cx(i), outY + 26, j.id, 24, INK, 'middle', 700);",
  "s += txt(cx(i), outY + 26, j.id, 24, done ? pixelInk(j.output) : INK, 'middle', 700);",'Keep result identity legible on all gray levels.');
replace("s += txt(cx(i), outY + 58, String(j.output), 32, GREEN, 'middle', 700);",
  "s += txt(cx(i), outY + 58, String(j.output), 32, pixelInk(j.output), 'middle', 700);",'Keep completed numbers legible.');
replace("    s += links;", "    // Stable A–H identities map input to lane; omit crossing connector clutter.",
  'Omit crossing lines that obscured intermediate execution rows.');
const locatorStart=code.indexOf('    // tiny board locator');
const locatorEnd=code.indexOf('    const labels = [];',locatorStart);
if(locatorStart<0||locatorEnd<0)throw new Error('Locator repair anchor mismatch');
code=code.slice(0,locatorStart)+code.slice(locatorEnd);
changes.push('Remove a miniature board that covered completed G/H results; the native whole-GPU action supplies return context.');
replace("    return {\n      svg: '<g class=\"iso\" data-part=\"board\">' + out + '</g>',",
  `    const anchors=[gpuPt,memPt,conPt];
    out+=labels.map((l,i)=>'<path d="M'+anchors[i][0]+' '+anchors[i][1]+' L'+l.x+' '+l.y+'" stroke="#455b50" stroke-width="1.6" fill="none"/><circle cx="'+anchors[i][0]+'" cy="'+anchors[i][1]+'" r="3" fill="#fffdf5" stroke="#455b50"/>').join('');
    return {
      svg: '<g class="iso" data-part="board">' + out + '</g>',`,
  'Anchor each HTML core label to the actual projected chip/memory/connector.');
const sha=s=>createHash('sha256').update(s).digest('hex');
await writeFile(new URL('gpu-art-1-reviewed.js',dir),code);
await writeFile(new URL('gpu-art-1-repairs.json',dir),JSON.stringify({original_sha256:sha(original),reviewed_sha256:sha(code),changes},null,2));
