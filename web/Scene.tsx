import type { ReactElement } from 'react';
import type { LessonSpec, Part } from './contracts';

import { stageAt } from './lessonTimeline';
export { duration, stageAt } from './lessonTimeline';
import { Hardware } from './ac/Hardware';
import { Cutaway, acSceneHash } from './teaching/Context';
import { SectionContext, hasSectionArtwork } from './teaching/Sections';
export function partPose(part: Part, stage: number, progress: number): [number, number, number] {
  let dx = 0, dy = 0, angle = 0;
  for (const m of part.motion) {
    const p = m.stage < stage ? 1 : m.stage === stage ? progress : 0;
    if (m.kind === 'rotate') angle += m.amount * p;
    if (m.kind === 'translate') { if (m.axis === 'x') dx += m.amount * p; else dy += m.amount * p; }
  }
  return [dx, dy, angle];
}

interface Props { readonly spec: LessonSpec; readonly seconds?: number; readonly selected?: string; readonly onSelect?: (id: string) => void; readonly preview?: boolean; readonly zoom?: boolean }
export function Scene({ spec, seconds = 0, selected = '', onSelect, preview = false, zoom = false }: Props): ReactElement {
  if(spec.teaching?.renderer==='authored-sections-v1'&&hasSectionArtwork(spec))return <SectionContext spec={spec}/>;
  if(preview && spec.teaching?.renderer==='ac-cutaway-v2' && spec.teaching.renderer_fingerprint===acSceneHash) return <Cutaway/>;
  if (preview && spec.canonical === 'air-conditioner-craft') return <Hardware step={0} focus="" running={false} placement="outside" onSelect={() => undefined} preview />;
  const [stage, progress] = stageAt(spec, seconds);
  const active = new Set(spec.stages[stage].parts);
  const explorable = new Set(spec.stages.flatMap(s => s.parts));
  const labeled = new Set(spec.parts.filter(p => p.id.startsWith("label-")).map(p => p.id.slice(6)));
  const focused = spec.parts.find(p => p.id === selected);
  const componentLabel = spec.parts.find(p => p.id === `label-${selected}`);
  const bounds = focused?.points.length ? [Math.min(...focused.points.map(p => p[0])), Math.min(...focused.points.map(p => p[1])), Math.max(...focused.points.map(p => p[0])), Math.max(...focused.points.map(p => p[1]))] : focused ? [focused.x, focused.y, focused.x + focused.w, focused.y + focused.h] : [0,0,900,540];
  if (componentLabel) {
    bounds[0] = Math.min(bounds[0], componentLabel.x);
    bounds[1] = Math.min(bounds[1], componentLabel.y);
    bounds[2] = Math.max(bounds[2], componentLabel.x + componentLabel.label.length*componentLabel.h*.55);
    bounds[3] = Math.max(bounds[3], componentLabel.y+componentLabel.h);
  }
  const vx = Math.max(0, Math.min(400, (bounds[0]+bounds[2])/2 - 250));
  const vy = Math.max(0, Math.min(240, (bounds[1]+bounds[3])/2 - 150));
  return <svg className={`machine-scene ${preview ? 'preview' : ''}`} viewBox={zoom ? `${vx} ${vy} 500 300` : "0 0 900 540"} role={preview ? 'img' : 'group'} aria-label={`${spec.title}: ${spec.stages[stage].title}`}>
    {spec.canonical !== "air-conditioner-craft" && <ellipse cx="460" cy="479" rx="290" ry="22" fill="#e1e8eb" />}
    {[...spec.parts].sort((a, b) => a.layer - b.layer).map(part => {
      const [dx, dy, angle] = partPose(part, stage, progress);
      const flow = part.motion.some(m => m.kind === 'flow' && m.stage === stage);
      const heat = ['absorbed-heat', 'released-heat'].includes(part.id);
      const pulse = part.motion.some(m => m.kind === 'pulse' && m.stage === stage);
      const target = part.id.startsWith('label-') ? part.id.slice(6) : part.id;
      const interactive = !!onSelect && explorable.has(target) && !preview;
      const coreLabel = part.shape === 'text' && part.id.startsWith('label-');
      const focusable = interactive && (coreLabel || !labeled.has(target));
      const semanticPart = spec.parts.find(p => p.id === target) || part;
      const emphasized = coreLabel && (active.has(target) || selected === target);
      const stroke = part.stroke;
      const attrs = { fill: part.color, stroke, strokeWidth: selected === part.id ? 4 : 2 };
      let shape: ReactElement;
      if (part.shape === 'box') shape = <rect x={part.x} y={part.y} width={part.w} height={part.h} rx="4" {...attrs} />;
      else if (part.shape === 'ellipse' || part.shape === 'ring') shape = <ellipse cx={part.x + part.w / 2} cy={part.y + part.h / 2} rx={part.w / 2} ry={part.h / 2} {...attrs} fill={part.shape === 'ring' ? 'none' : part.color} strokeWidth={part.shape === 'ring' ? 5 : attrs.strokeWidth} />;
      else if (part.shape === 'polygon') shape = <polygon points={part.points.map(p => p.join(',')).join(' ')} {...attrs} />;
      else if (part.shape === 'text') shape = <text x={part.x} y={part.y} dominantBaseline="hanging" fontSize={part.h} fontWeight={coreLabel ? 650 : 450} fill={emphasized ? spec.accent : part.color}>{part.label}</text>;
      else shape = <g><polyline points={part.points.map(p => p.join(',')).join(' ')} fill="none" stroke={stroke} strokeWidth={Math.max(2, part.w)} strokeDasharray={heat ? "4 7" : undefined} strokeLinecap="round" strokeLinejoin="round" />
        {flow && part.points.length > 1 && (() => { const b=part.points[part.points.length-1], a=part.points[part.points.length-2], length=Math.hypot(b[0]-a[0],b[1]-a[1]) || 1, ux=(b[0]-a[0])/length, uy=(b[1]-a[1])/length; return <polygon points={`${b[0]},${b[1]} ${b[0]-ux*12-uy*6},${b[1]-uy*12+ux*6} ${b[0]-ux*12+uy*6},${b[1]-uy*12-ux*6}`} fill={part.stroke} />; })()}
        {flow && !heat && active.has(part.id) && part.points.slice(0, -1).map((a, i) => { const b = part.points[i + 1], length = Math.hypot(b[0]-a[0], b[1]-a[1]);
          if (length < 40) return null;
          const count = length > 130 ? 2 : 1, ux=(b[0]-a[0])/length, uy=(b[1]-a[1])/length;
          return Array.from({ length: count }, (_, j) => {
            const t = .12 + .76 * ((j / count + progress * .8) % 1), x=a[0]+(b[0]-a[0])*t, y=a[1]+(b[1]-a[1])*t;
            return <polyline key={`${i}-${j}`} points={`${x-ux*7-uy*5},${y-uy*7+ux*5} ${x},${y} ${x-ux*7+uy*5},${y-uy*7-ux*5}`} stroke="white" strokeWidth="2.5" fill="none" strokeLinecap="round" strokeLinejoin="round" />;
          }); })}</g>;
      return <g key={part.id} transform={`translate(${dx} ${dy}) rotate(${angle} ${part.x + part.w / 2} ${part.y + part.h / 2})`}
        className={interactive ? 'selectable-part' : undefined} role={focusable ? 'button' : undefined} aria-hidden={!focusable ? true : undefined}
        tabIndex={focusable ? 0 : undefined} aria-label={focusable ? semanticPart.name : undefined}
        aria-pressed={interactive ? selected === target : undefined}
        onClick={interactive ? () => onSelect?.(target) : undefined}
        onKeyDown={interactive ? e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onSelect?.(target); } } : undefined}>
        <title>{semanticPart.name}: {semanticPart.description}</title>
        {coreLabel && <rect x={part.x-8} y={part.y-6} width={part.label.length*part.h*.55+16} height={part.h+14} rx="5" fill="white" fillOpacity=".96" stroke={emphasized ? spec.accent : "#d6e1e5"} strokeWidth={emphasized ? 2 : 1} />}
        {shape}
        {spec.canonical !== 'air-conditioner-craft' && !preview && active.has(part.id) && !['path', 'text'].includes(part.shape) && <circle cx={part.x + part.w} cy={part.y} r={pulse ? 5 + 2 * Math.sin(progress * Math.PI * 8) : 5} fill={spec.accent} stroke="white" strokeWidth="2" />}
      </g>;
    })}
  </svg>;
}
