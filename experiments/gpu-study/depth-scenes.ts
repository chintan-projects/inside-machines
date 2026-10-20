/** Trusted GPU views. Arithmetic/readiness is supplied by depth-model, never calculated here. */
import type { Scene } from '../visual-studio/contracts.ts';
import { arrow, box, figure, ink, paper, picture, pixelRow, rust, teal, text } from '../visual-studio/drawing.ts';
import { INPUT, type CoreState, type FeedState, type Matrix, type MatrixState } from './depth-model.ts';
import { pointAt } from '../shared/geometry.ts';

const scene = (svg: string, caption: string, alt: string, contentKey: string, height = 620): Scene => ({
  svg: figure(svg).replaceAll('flow-head', `${contentKey}-flow-head`), labels: [], caption, alt, contentKey, viewport: { x: 0, y: 0, width: 720, height },
});
function slots(jobs: readonly { readonly input: number | null; readonly id: string }[], progress: number,
  increment: number, label: string, complete = false): string {
  let svg = text(360, 210, label, 28);
  for (let i = 0; i < 4; i++) {
    const x = 48 + i % 2 * 324, y = 234 + Math.floor(i / 2) * 110, job = jobs[i];
    svg += box(x, y, 300, 90, job ? '#e2ece5' : '#f0f0e8', job ? teal : '#a9afa3') +
      text(x + 150, y + 30, `Slot ${i + 1}${job ? ` · ${job.id}` : complete ? ' · idle' : ' · waiting'}`, 28, job ? teal : ink) +
      text(x + 150, y + 66, job ? `${job.input} + ${increment}` : complete ? 'All work complete' : 'No ready input', 30);
    if (job) svg += `<rect data-studio-progress x="${x + 20}" y="${y + 78}" width="${260 * progress}" height="5" fill="${teal}" rx="2"/>`;
  }
  return svg;
}
export function coreScene(s: CoreState, board: Scene): Scene {
  if (s.phase === 'board' || s.phase === 'whole') return { ...board, contentKey: `core-${s.phase}`, alt: `${s.description} ${board.alt}`,
    caption: s.phase === 'board' ? board.caption : 'The program requests work. GPU memory holds inputs/results. The chip computes. Data movement and computation may overlap in real systems.' };
  if (s.phase === 'pixels') return scene(text(360, 64, 'A picture is stored as numbers') + picture(INPUT, 112) +
    text(360, 350, 'One number per pixel', 30) + box(190, 404, 340, 90, '#f3e4d0', rust) +
    text(360, 459, `Our operation: add ${s.increment}`, 32, rust),
  'Eight toy brightness values, A–H in reading order. Shade represents the stored number; this is not an image format or calibrated luminance.', `${s.description} Input values in reading order: ${INPUT.join(', ')}.`, 'pixels');
  if (s.phase === 'program' || s.phase === 'load') {
    const point = pointAt(s.phase === 'program' ? [[185, 224], [185, 276], [285, 276], [285, 320]] :
      [[537, 224], [537, 276], [435, 276], [435, 320]], s.transferProgress);
    return { ...scene(
    box(38, 70, 294, 148, '#f3e4d0', rust) + text(185, 114, 'Program on CPU', 30, rust) +
    text(185, 168, `Add ${s.increment} to each pixel`, 28) +
    box(392, 70, 290, 148, '#e2ece5', teal) + text(537, 114, 'GPU memory', 30, teal) + text(537, 168, '0  1  2  3  4  5  6  7', 28) +
    arrow('M185 218V276H285V320', rust) + text(80, 267, 'Request', 28, rust) +
    arrow('M537 218V276H435V320') + text(650, 267, 'Inputs', 28, teal) +
    box(205, 320, 310, 150, paper, teal) + text(360, 366, 'GPU chip', 34, teal) + text(360, 416, 'Read · calculate', 28) +
    arrow('M360 470V512') + box(160, 518, 400, 70, '#e2ece5', teal) + text(360, 562, 'Store results in memory', 28) +
    `<g data-copy transform="translate(${point[0]} ${point[1]})">${s.phase === 'program'
      ? box(-44, -20, 88, 42, rust, rust) + text(0, 10, `+${s.increment}`, 30, paper)
      : box(-78, -20, 156, 42, '#e2ece5', teal) + text(0, 10, '0  1  2  3', 28)}</g>`,
    'Logical discrete-GPU example. The moving instruction or copied values show a work/data relationship, not a physical packet, hardware travel time or exclusive timing. Other memory organizations exist.',
    s.description, `system-${s.phase}-${s.increment}`), attributes: [{ selector: '[data-copy]', name: 'transform', value: `translate(${point[0]} ${point[1]})` }] };
  }
  if (s.phase === 'compute') {
    const jobs = s.schedule.lanes.flatMap(l => {
      const job = s.schedule.jobs.find(j => j.id === l.jobId); return job ? [{ id: job.id, input: job.input }] : [];
    });
    return { ...scene(text(360, 42, 'Input values in GPU memory', 28) + pixelRow(INPUT, 62) +
      slots(jobs, s.schedule.progress, s.increment, 'Four illustrative calculation slots') +
      text(360, 494, 'Results written back', 28) + pixelRow(s.results, 518),
    'Logical calculation view. The same instruction acts on different inputs. Four slots and rounds are a teaching model, not a die layout or GPU timing.',
    `${s.description} Inputs: ${INPUT.join(', ')}. Working: ${jobs.map(j => j.id).join(', ')}. Stored results: ${s.results.map(n => n ?? 'not ready').join(', ')}.`, `core-work-${s.increment}-${s.results.filter(n => n !== null).length}`),
    attributes: [{ selector: '[data-studio-progress]', name: 'width', value: String(260 * s.schedule.progress) }] };
  }
  return scene(text(360, 40, 'Before: input picture', 28) + picture(INPUT, 64, 64) +
    arrow('M360 218V282', rust) + text(510, 260, `Add ${s.increment} to each value`, 28, rust) +
    text(360, 324, 'After: stored results', 28) + picture(s.results, 350, 78) +
    text(360, 570, 'Same pixels. Changed numbers.', 30),
  'Eight pixels stay in the same reading order. Each output is its input plus the requested amount.', `${s.description} Inputs: ${INPUT.join(', ')}. Stored results: ${s.results.join(', ')}.`, `result-${s.increment}`);
}
export function feedScene(s: FeedState): Scene {
  const working = s.working.map(i => ({ id: 'ABCDEFGH'[i], input: INPUT[i] }));
  const caption = `Toy data-supply model · ${s.supply} input${s.supply === 1 ? '' : 's'} per ideal round · ${s.round}/${s.rounds} rounds complete. Inputs are delivered before each round's calculation. No real bandwidth or timing is implied.`;
  return { ...scene(text(360, 42, 'Inputs waiting in memory', 28) + pixelRow(INPUT.map((n, i) => i < s.arrived ? null : n), 62) +
    text(360, 170, `${s.supply} input${s.supply === 1 ? '' : 's'} supplied per round`, 28, rust) +
    slots(working, s.progress, 1, 'Four slots remain available', s.results.every(n => n !== null)) + text(360, 494, 'Completed results', 28) + pixelRow(s.results, 518),
  caption, `${s.description} Working jobs: ${working.map(j => `${j.id}, input ${j.input}`).join('; ') || 'none'}. Stored results: ${s.results.map(n => n ?? 'not ready').join(', ')}.`,
  `feed-${s.supply}-${s.arrived}-${s.round}`), attributes: [{ selector: '[data-studio-progress]', name: 'width', value: String(260 * s.progress) }] };
}
function grid(m: Matrix, x: number, y: number, selected: (r: number, c: number) => boolean,
  color: string, visible: (r: number, c: number) => boolean = () => true, size = 86): string {
  return m.map((row, r) => row.map((value, c) => {
    const on = selected(r, c);
    return box(x + c * size, y + r * size, size - 6, size - 6, on ? color === teal ? '#e2ece5' : '#f3e4d0' : paper, on ? color : '#a9afa3', 7) +
      text(x + c * size + (size - 6) / 2, y + r * size + size / 2 + 10, visible(r, c) ? value : '?', 38);
  }).join('')).join('');
}
export function matrixScene(s: MatrixState): Scene {
  const pairs = s.step !== 'grids', products = ['multiply', 'sum', 'outputs', 'connect'].includes(s.step);
  const summed = ['sum', 'outputs', 'connect'].includes(s.step), all = ['outputs', 'connect'].includes(s.step);
  let svg = text(160, 36, 'A · picture values', 28, teal) + text(544, 36, 'B · example weights', 28, rust) +
    grid(s.a, 78, 78, r => pairs && r === s.row, teal) +
    grid(s.b, 460, 78, (_r, c) => pairs && c === s.column, rust) +
    text(160, 286, pairs ? `Row ${s.row + 1}` : 'Two rows', 28, teal) +
    text(544, 286, pairs ? `Column ${s.column + 1}` : 'Two columns', 28, rust);
  if (pairs) {
    svg += arrow('M160 300V320') + arrow('M544 300V320', rust);
    for (let i = 0; i < 2; i++) {
      const x = 50 + i * 346;
      svg += box(x, 330, 276, 72, '#f5efe1', '#a9afa3') +
        text(x + 138, 376, `${s.left[i]} × ${s.right[i]}${products ? ` = ${s.products[i]}` : ''}`, 36);
    }
  }
  if (summed) svg += text(360, 453, `${s.products[0]} + ${s.products[1]} = ${s.sum}`, 38);
  svg += text(360, 500, 'C · output values', 28) + grid(s.result, 277, 524,
    (r, c) => all && s.changed ? c === 1 : r === s.row && c === s.column, teal,
    (r, c) => all || (summed && r === s.row && c === s.column), 86);
  if (s.changed) svg += text(360, 726, 'Changed weight: output column 2 changes', 28, rust);
  const outputs = s.result.map((row, r) => row.map((n, c) => all || (summed && r === s.row && c === s.column) ? n : 'not revealed').join(', ')).join('; ');
  return scene(svg, 'A uses four results from the original add-one picture, rearranged into two rows. Each output combines a row of A with a column of B. The weights are examples, not real AI weights.',
    `${s.description} A rows: ${s.a.map(r => r.join(', ')).join('; ')}. B rows: ${s.b.map(r => r.join(', ')).join('; ')}. C rows: ${outputs}.`, `matrix-${s.step}-${s.row}-${s.column}-${s.changed}`, 750);
}
