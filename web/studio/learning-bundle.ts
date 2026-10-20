import type { Lesson } from '../contracts';
import { parsePath, type LearningPath } from './path-contract.ts';

export interface BundleLesson extends Lesson { readonly spec_sha256?: string; readonly video_sha256?: string }
export interface LearningBundle { readonly path: LearningPath; readonly bundle_sha256: string; readonly lessons: readonly BundleLesson[] }
const sha = /^[a-f0-9]{64}$/;

/** Resolve only the immutable lesson IDs declared by this versioned path. */
export function checkedBundle(bundle: LearningBundle, rootId: string, requireBindings = false): LearningBundle {
  const ids = bundle.lessons.map(lesson => lesson.id);
  if (new Set(ids).size !== ids.length) throw new Error('The explanation contains duplicate revisions.');
  const path = parsePath(bundle.path, ids);
  if (typeof bundle.bundle_sha256 !== 'string' || (bundle.bundle_sha256 !== '' && !sha.test(bundle.bundle_sha256)) ||
      (requireBindings && path.nodes.length > 1 && !bundle.bundle_sha256)) throw new Error('The explanation is missing its learning-path identity.');
  if (path.nodes[0].lesson_id !== rootId) throw new Error('This path belongs to a different explanation.');
  const referenced = new Set(path.nodes.map(node => node.lesson_id));
  const lessons = bundle.lessons.filter(lesson => referenced.has(lesson.id));
  if (lessons.some(lesson => lesson.spec.version !== 2 || !lesson.spec.teaching || !lesson.spec.graphics?.length))
    throw new Error('A saved explanation is missing its teaching data. Reconnect and save it again.');
  if (requireBindings && lessons.some(lesson => !sha.test(lesson.spec_sha256 ?? '') ||
      typeof lesson.video_sha256 !== 'string' || (lesson.video_sha256 !== '' && !sha.test(lesson.video_sha256)) ||
      (lesson.video_ready && !sha.test(lesson.video_sha256))))
    throw new Error('The explanation is missing its artifact identities. Reconnect before saving it.');
  return { path, bundle_sha256: bundle.bundle_sha256, lessons };
}

/** The cached graph and each node's exact artifacts must match the current envelope. */
export function matchesSavedBundle(cached: LearningBundle, current: LearningBundle): boolean {
  if (cached.bundle_sha256 !== current.bundle_sha256 || JSON.stringify(cached.path) !== JSON.stringify(current.path)) return false;
  return current.lessons.every(lesson => {
    const old = cached.lessons.find(item => item.id === lesson.id);
    return !!old && !!lesson.spec_sha256 && old.spec_sha256 === lesson.spec_sha256 &&
      old.video_sha256 === lesson.video_sha256 && old.video_ready === lesson.video_ready;
  });
}

export function coreBundle(lesson: Lesson): LearningBundle {
  const teaching = lesson.spec.teaching;
  if (!teaching) throw new Error('This revision has no teaching data.');
  return checkedBundle({bundle_sha256: '', path: {
    schema_version: 'learning-path-1', id: lesson.id, title: lesson.spec.title,
    example: lesson.spec.summary, entry: 'core', nodes: [{ id: 'core', role: 'core',
      label: 'The complete picture', question: lesson.spec.question, outcome: teaching.goal,
      lesson_id: lesson.id, prerequisites: [], next: [], queries: [lesson.spec.question] }],
  }, lessons: [lesson]}, lesson.id);
}
