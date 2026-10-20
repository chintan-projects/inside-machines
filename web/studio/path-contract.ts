/** Portable, data-only learning envelope. Python emits its JSON schema for API callers. */
export interface PathNode {
  readonly id: string;
  readonly role: 'core' | 'insight' | 'model';
  readonly label: string;
  readonly question: string;
  readonly outcome: string;
  readonly lesson_id: string;
  readonly prerequisites: readonly string[];
  readonly next: readonly string[];
  readonly queries: readonly string[];
}
export interface LearningPath {
  readonly schema_version: 'learning-path-1';
  readonly id: string;
  readonly title: string;
  readonly example: string;
  readonly entry: string;
  readonly nodes: readonly PathNode[];
}
const object = (v: unknown): Record<string, unknown> => {
  if (!v || typeof v !== 'object' || Array.isArray(v)) throw new Error('Expected a learning-path object');
  return v as Record<string, unknown>;
};
const text = (v: unknown, min: number, max: number): string => {
  if (typeof v !== 'string' || v.length < min || v.length > max) throw new Error('Invalid learning-path text');
  return v;
};
const id = (v: unknown, max = 64): string => {
  const s = text(v, 1, max); if (!/^[a-z][a-z0-9-]*$/.test(s)) throw new Error('Invalid stable ID'); return s;
};
const list = (v: unknown, min: number, max: number): readonly unknown[] => {
  if (!Array.isArray(v) || v.length < min || v.length > max) throw new Error('Invalid learning-path list'); return v;
};
const keys = (v: Record<string, unknown>, allowed: readonly string[]): void => {
  if (Object.keys(v).some(k => !allowed.includes(k))) throw new Error('Unsupported learning-path field');
};
/** Validate network/JSON input before resolving any trusted lesson adapter. */
export function parsePath(value: unknown, allowedLessons: readonly string[]): LearningPath {
  const p = object(value);
  keys(p, ['schema_version', 'id', 'title', 'example', 'entry', 'nodes']);
  if (p.schema_version !== 'learning-path-1') throw new Error('Unsupported learning-path version');
  const nodes: PathNode[] = list(p.nodes, 1, 8).map(value => {
    const n = object(value); keys(n, ['id', 'role', 'label', 'question', 'outcome', 'lesson_id', 'prerequisites', 'next', 'queries']);
    if (n.role !== 'core' && n.role !== 'insight' && n.role !== 'model') throw new Error('Unsupported node role');
    return { id: id(n.id), role: n.role, label: text(n.label, 3, 80), question: text(n.question, 8, 200),
      outcome: text(n.outcome, 10, 400), lesson_id: id(n.lesson_id, 96),
      prerequisites: list(n.prerequisites, 0, 7).map(v => id(v)), next: list(n.next, 0, 7).map(v => id(v)),
      queries: list(n.queries, 1, 12).map(v => { const q = text(v, 1, 160); if (!q.trim()) throw new Error('Empty query'); return q; }) };
  });
  const path: LearningPath = { schema_version: p.schema_version, id: id(p.id, 96), title: text(p.title, 3, 120),
    example: text(p.example, 10, 400), entry: id(p.entry), nodes };
  const ids = nodes.map(n => n.id), seen = new Set<string>();
  if (new Set(ids).size !== nodes.length || path.entry !== ids[0] || nodes[0].role !== 'core' ||
      nodes.filter(n => n.role === 'core').length !== 1) throw new Error('Invalid core entry or duplicate nodes');
  for (const n of nodes) {
    if (!allowedLessons.includes(n.lesson_id) || new Set(n.prerequisites).size !== n.prerequisites.length ||
        n.prerequisites.some(p => !seen.has(p)) || new Set(n.next).size !== n.next.length ||
        n.next.some(p => !ids.includes(p) || p === n.id)) throw new Error('Invalid lesson or graph reference');
    seen.add(n.id);
  }
  const visited = new Set<string>();
  const visit = (node: PathNode, ancestors: readonly string[]): void => {
    if (ancestors.includes(node.id)) throw new Error('Cyclic learning path');
    if (visited.has(node.id)) return;
    visited.add(node.id);
    node.next.forEach(child => visit(nodes.find(n => n.id === child)!, [...ancestors, node.id]));
  };
  visit(nodes[0], []);
  if (visited.size !== nodes.length) throw new Error('Unreachable learning node');
  return path;
}
const normalized = (s: string): string => s.toLowerCase().replace(/[^\p{L}\p{N}]+/gu, ' ').trim();
/** Recognize a bounded depth command; named topics and negations stay explicit queries. */
export function isDepthRequest(question: string): boolean {
  return /^(?:please )?(?:(?:can|could|would) you (?:please )?|let s )?(?:deeper|dive deeper|go deeper|tell me more|more|explain more|show me more|explain in more detail|go into more detail)(?: please)?$/.test(normalized(question));
}
/** Local retrieval only. Ambiguous/unavailable questions never fabricate an AI answer. */
export function resolveQuestion(path: LearningPath, current: string, question: string): PathNode | undefined {
  const q = normalized(question);
  if (!q) return undefined;
  const here = path.nodes.find(n => n.id === current);
  if (isDepthRequest(question)) {
    return path.nodes.find(n => n.id === here?.next[0]);
  }
  const exact = path.nodes.filter(n => [n.question, n.label, ...n.queries].some(x => normalized(x) === q));
  if (exact.length === 1) return exact[0];
  const vocabulary = new Set(normalized([path.title, path.example,
    ...path.nodes.flatMap(n => [n.label, n.question, n.outcome, ...n.queries]),
    'can you tell me more about please how does do a an the work works what is it explain show why with when to for of and',
  ].join(' ')).split(' '));
  if (q.split(' ').some(word => !vocabulary.has(word))) return undefined;
  const matches = path.nodes.filter(n => n.queries.some(alias => {
    const term = normalized(alias); return term.length >= 4 && ` ${q} `.includes(` ${term} `);
  }));
  return matches.length === 1 ? matches[0] : undefined;
}
