import type { ReactElement } from 'react';
import type { LessonSpec, Part } from './contracts';

export function duration(spec: LessonSpec): number { return spec.stages.reduce((n, s) => n + s.duration, 0); }
export function stageAt(spec: LessonSpec, seconds: number): [number, number] {
  let elapsed = 0;
  for (let i = 0; i < spec.stages.length; i++) {
    const stage = spec.stages[i];
    if (seconds < elapsed + stage.duration || i === spec.stages.length - 1)
      return [i, Math.max(0, Math.min(1, (seconds - elapsed) / stage.duration))];
    elapsed += stage.duration;
  }
  return [0, 0];
}
export function partPose(part: Part, stage: number, progress: number): [number, number, number] {
  let dx = 0, dy = 0, angle = 0;
  for (const m of part.motion) {
    const p = m.stage < stage ? 1 : m.stage === stage ? progress : 0;
    if (m.kind === 'rotate') angle += m.amount * p;
    if (m.kind === 'translate') { if (m.axis === 'x') dx += m.amount * p; else dy += m.amount * p; }
  }
  return [dx, dy, angle];
}

interface Props { readonly spec: LessonSpec; readonly seconds?: number; readonly selected?: string; readonly onSelect?: (id: string) => void; readonly preview?: boolean }
export function Scene({ spec, seconds = 0, selected = '', onSelect, preview = false }: Props): ReactElement {
  const [stage, progress] = stageAt(spec, seconds);
  const active = new Set(spec.stages[stage].parts);
  return <svg className={`machine-scene ${preview ? 'preview' : ''}`} viewBox="0 0 900 540" role={preview ? 'img' : 'group'} aria-label={`${spec.title}: ${spec.stages[stage].title}`}>
    <ellipse cx="460" cy="479" rx="290" ry="22" fill="#e1e8eb" />
    {[...spec.parts].sort((a, b) => a.layer - b.layer).map(part => {
      const [dx, dy, angle] = partPose(part, stage, progress);
      const flow = part.motion.some(m => m.kind === 'flow' && m.stage === stage);
      const pulse = part.motion.some(m => m.kind === 'pulse' && m.stage === stage);
      const stroke = selected === part.id ? spec.accent : part.stroke;
      const attrs = { fill: part.color, stroke, strokeWidth: selected === part.id ? 4 : 2 };
      let shape: ReactElement;
      if (part.shape === 'box') shape = <rect x={part.x} y={part.y} width={part.w} height={part.h} rx="4" {...attrs} />;
      else if (part.shape === 'ellipse' || part.shape === 'ring') shape = <ellipse cx={part.x + part.w / 2} cy={part.y + part.h / 2} rx={part.w / 2} ry={part.h / 2} {...attrs} fill={part.shape === 'ring' ? 'none' : part.color} strokeWidth={part.shape === 'ring' ? 5 : attrs.strokeWidth} />;
      else if (part.shape === 'polygon') shape = <polygon points={part.points.map(p => p.join(',')).join(' ')} {...attrs} />;
      else if (part.shape === 'text') shape = <text x={part.x} y={part.y + part.h} fontSize={part.h} fill={part.color}>{part.label}</text>;
      else shape = <g><polyline points={part.points.map(p => p.join(',')).join(' ')} fill="none" stroke={stroke} strokeWidth={Math.max(2, part.w)} strokeLinecap="round" strokeLinejoin="round" />
        {flow && part.points.slice(0, -1).map((a, i) => { const b = part.points[i + 1]; return Array.from({ length: 6 }, (_, j) => {
          const t = (j / 6 + progress * .6) % 1;
          return <circle key={`${i}-${j}`} cx={a[0] + (b[0] - a[0]) * t} cy={a[1] + (b[1] - a[1]) * t} r="3" fill={spec.accent} />;
        }); })}</g>;
      return <g key={part.id} transform={`translate(${dx} ${dy}) rotate(${angle} ${part.x + part.w / 2} ${part.y + part.h / 2})`}
        className={onSelect ? 'selectable-part' : undefined} role={onSelect ? 'button' : undefined}
        tabIndex={onSelect && !preview ? 0 : undefined} aria-label={onSelect ? part.name : undefined}
        aria-pressed={onSelect ? selected === part.id : undefined}
        onClick={onSelect ? () => onSelect(part.id) : undefined}
        onKeyDown={onSelect ? e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onSelect(part.id); } } : undefined}>
        <title>{part.name}: {part.description}</title>
        {shape}
        {!preview && active.has(part.id) && !['path', 'text'].includes(part.shape) && <circle cx={part.x + part.w} cy={part.y} r={pulse ? 5 + 2 * Math.sin(progress * Math.PI * 8) : 5} fill={spec.accent} stroke="white" strokeWidth="2" />}
      </g>;
    })}
  </svg>;
}
