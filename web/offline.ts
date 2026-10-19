import type { CatalogEntry, Lesson, Member } from './contracts';

export interface SavedLesson { key: string; user: string; lesson: Lesson; video?: Blob; captions?: string; saved: number }
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
  return (await records()).filter(r => r.user === user).map(({ lesson, saved }) => ({
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
