import type { CatalogEntry, Lesson, Member } from './contracts';
import type { LearningPath } from './studio/path-contract';
import { checkedBundle, coreBundle, type LearningBundle } from './studio/learning-bundle.ts';
import { verifyVideo } from './studio/artifact-integrity.ts';

export interface SavedLesson { key: string; user: string; lesson: Lesson; video?: Blob; captions?: string; saved: number; learningPath?:LearningPath; bundleSha256?: string; pathChild?: boolean }
const DB = 'inside-saved-lessons-v1';

async function database(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB, 1);
    request.onupgradeneeded = () => request.result.createObjectStore('lessons', { keyPath: 'key' });
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(new Error('This browser cannot save explanations offline.'));
  });
}

async function records(): Promise<SavedLesson[]> {
  const db = await database();
  try {
    return await new Promise((resolve, reject) => {
      const request = db.transaction('lessons').objectStore('lessons').getAll();
      request.onsuccess = () => resolve(request.result as SavedLesson[]);
      request.onerror = () => reject(new Error('Couldn’t read saved explanations.'));
    });
  } finally { db.close(); }
}

export async function savedLesson(user: string, id: string): Promise<SavedLesson | undefined> {
  return (await records()).find(record => record.user === user && record.lesson.id === id);
}

/** A path is usable offline only when every referenced revision is present. */
export async function savedLearningPath(user: string, id: string): Promise<{bundle: LearningBundle; records: readonly SavedLesson[]} | undefined> {
  const mine = (await records()).filter(record => record.user === user);
  const root = mine.find(record => record.lesson.id === id);
  if (!root) return undefined;
  const bundle = root.learningPath
    ? checkedBundle({path: root.learningPath, bundle_sha256: root.bundleSha256 ?? '', lessons: mine.map(record => record.lesson)}, id)
    : coreBundle(root.lesson);
  const included = mine.filter(record => bundle.lessons.some(lesson => lesson.id === record.lesson.id));
  if (included.some(record => record.lesson.video_ready && (!record.video || !record.captions)))
    throw new Error('This offline save is incomplete. Reconnect and save the explanation again.');
  return {bundle, records: included};
}

/** Download before the single transaction, so a failed child cannot leave a partial path. */
export async function prepareSavedPath(user: string, value: LearningBundle, rootId: string,
  download: typeof fetch = fetch): Promise<SavedLesson[]> {
  const bundle = checkedBundle(value, rootId, true), saved = Date.now();
  return Promise.all(bundle.lessons.map(async lesson => {
    const record: SavedLesson = { key: `${user}:${lesson.id}`, user,
      lesson: {...lesson, feedback: null}, saved, pathChild: lesson.id !== rootId };
    if (lesson.id === rootId) { record.learningPath = bundle.path; record.bundleSha256 = bundle.bundle_sha256; }
    if (lesson.video_ready) {
      const base = `/api/v1/lessons/${encodeURIComponent(lesson.id)}`;
      const [video, captions] = await Promise.all([download(`${base}/video`), download(`${base}/captions`)]);
      if (!video.ok || !captions.ok) throw new Error('Couldn’t download the complete explanation. Nothing new was saved.');
      record.video = await video.blob(); await verifyVideo(record.video, lesson.video_sha256);
      record.captions = await captions.text();
    }
    return record;
  }));
}

export async function saveLearningPath(user: string, bundle: LearningBundle, rootId: string): Promise<void> {
  const prepared = await prepareSavedPath(user, bundle, rootId);
  const db = await database();
  try {
    await new Promise<void>((resolve, reject) => {
      const tx = db.transaction('lessons', 'readwrite'), store = tx.objectStore('lessons');
      prepared.forEach(record => {
        // Read inside this serialized write transaction: another tab may have just
        // saved this child independently, including its own path identity.
        const previous = store.get(record.key);
        previous.onsuccess = () => {
          const old = previous.result as SavedLesson | undefined;
          if (record.pathChild && old && !old.pathChild) {
            record.pathChild = false; record.learningPath = old.learningPath; record.bundleSha256 = old.bundleSha256;
          }
          store.put(record);
        };
      });
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(new Error('Not enough browser storage. The previous save is preserved.'));
      tx.onabort = () => reject(new Error('The save was interrupted. The previous save is preserved.'));
    });
  } finally { db.close(); }
}

export async function saveLesson(user: string, lesson: Lesson): Promise<void> {
  const clean: Lesson = { ...lesson, feedback: null };
  const record: SavedLesson = { key: `${user}:${lesson.id}`, user, lesson: clean, saved: Date.now() };
  if (lesson.video_ready) {
    const [video, captions] = await Promise.all([
      fetch(`/api/v1/lessons/${encodeURIComponent(lesson.id)}/video`),
      fetch(`/api/v1/lessons/${encodeURIComponent(lesson.id)}/captions`),
    ]);
    if (!video.ok || !captions.ok) throw new Error('Couldn’t download the video. Please try saving again.');
    record.video = await video.blob(); record.captions = await captions.text();
  }
  const db = await database();
  try {
    await new Promise<void>((resolve, reject) => {
      const tx = db.transaction('lessons', 'readwrite');
      tx.objectStore('lessons').put(record);
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(new Error('Not enough browser storage. Free some space and try again.'));
    });
  } finally { db.close(); }
}

export async function offlineCatalog(user: string): Promise<CatalogEntry[]> {
  return (await records()).filter(r => r.user === user && !r.pathChild).map(({ lesson, saved }) => ({
    id: lesson.id, title: lesson.spec.title, canonical: lesson.spec.canonical, family: lesson.spec.family,
    question: lesson.spec.question, summary: lesson.spec.summary, category: lesson.spec.category,
    accent: lesson.spec.accent, duration: lesson.spec.stages.reduce((n, s) => n + s.duration, 0),
    parts: lesson.spec.parts.length, quality: lesson.quality, created_at: saved / 1000,
    views: 0, video_ready: lesson.video_ready, preview: lesson.spec,
  }));
}

export async function clearOffline(): Promise<void> {
  for (const key of Object.keys(localStorage)) if (key.startsWith('inside.progress.')) localStorage.removeItem(key);
  for (const key of Object.keys(sessionStorage)) if (key.startsWith('inside.chat.')) sessionStorage.removeItem(key);
  const db = await database();
  try {
    await new Promise<void>((resolve, reject) => {
      const tx = db.transaction('lessons', 'readwrite'); tx.objectStore('lessons').clear();
      tx.oncomplete = () => resolve(); tx.onerror = () => reject(new Error('Couldn’t clear saved lessons.'));
    });
  } finally { db.close(); }
}

export function rememberMember(member: Member): void {
  localStorage.setItem('inside.member', JSON.stringify({ ...member, owner: false }));
}
export function offlineMember(): Member | null {
  try {
    const raw: unknown = JSON.parse(localStorage.getItem('inside.member') || 'null');
    if (raw && typeof raw === 'object' && 'id' in raw && 'name' in raw && typeof raw.id === 'string' && typeof raw.name === 'string')
      return { id: raw.id, name: raw.name, owner: false };
  } catch { /* Corrupt metadata has no authority to establish a session. */ }
  return null;
}
