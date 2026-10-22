import { useEffect, useRef, useState } from 'react';
import type { ReactElement } from 'react';
import type { Answer, Lesson, Member } from '../contracts';
import { api, errorMessage } from '../api';
import { FeedbackPanel, ChatPanel } from '../LessonDiscussion';
import { LessonSaveButton } from '../useLessonAssets';
import { offlineMember, savedLearningPath, saveLearningPath } from '../offline';
import { progressKey, readProgress } from '../progress';
import { mountLesson } from './player';
import { mountPath, type LearningPathAPI } from './path-player';
import type { StudioAPI } from './contracts';
import { adaptLesson, rendererAvailable } from './lesson-adapter';
import { chapterStarts, chapterIndex, componentIds, lessonDuration } from './native-contracts';
import { nativeLesson } from './native-registry';
import { checkedBundle, matchesSavedBundle, type LearningBundle } from './learning-bundle';
import { mountPreservedLesson } from './preserved-player';
import { discussionCheckpoint } from './discussion-checkpoint';
import { progressWriter } from './progress-writer';
import theme from './theme.css?inline';

interface Props { readonly lesson: Lesson; readonly member: Member; readonly online: boolean }
interface Discussion { readonly lesson: Lesson; readonly stage: number }

/** The same trusted path/player used by local studies, with member-scoped persistence. */
export function SharedStudio({lesson, member, online}: Props): ReactElement {
  const host = useRef<HTMLDivElement>(null), pathApi = useRef<LearningPathAPI | undefined>(undefined);
  const currentBundle = useRef<LearningBundle | undefined>(undefined);
  const [error, setError] = useState(''), [loading, setLoading] = useState(true), [attempt, setAttempt] = useState(0);
  const [discussion, setDiscussion] = useState<Discussion>({lesson, stage: 0});
  const [saved, setSaved] = useState(false), [saving, setSaving] = useState(false), [saveError, setSaveError] = useState('');
  const [cacheNote, setCacheNote] = useState('');

  useEffect(() => {
    const node = host.current;
    if (!node) return;
    const shadow = node.shadowRoot ?? node.attachShadow({mode: 'open'});
    const style = document.createElement('style'); style.textContent = theme.replace(':root', ':host');
    const root = document.createElement('div'); root.className='hosted-studio'; shadow.replaceChildren(style, root);
    let cancelled = false, interval = 0, lastSave = 0, mounted: LearningPathAPI | undefined;
    const urls: string[] = [];
    const progressStore = progressWriter((id, value) => localStorage.setItem(progressKey(member.id, id), JSON.stringify(value)));
    setLoading(true); setError(''); setSaveError(''); setSaved(false); setCacheNote(''); currentBundle.current = undefined;
    setDiscussion({lesson, stage: 0});

    const persist = (): void => {
      if (!mounted || !currentBundle.current || offlineMember()?.id !== member.id) return;
      try {
        currentBundle.current.path.nodes.forEach(pathNode => {
          const player = mounted?.getPlayer(pathNode.id);
          if (!player) return;
          const record = currentBundle.current!.lessons.find(item => item.id === pathNode.lesson_id)!;
          const state = player.getState(), stage = chapterIndex(record.spec, state.time);
          progressStore.save(record.id, {seconds: state.time,
            selected: record.spec.stages[stage].focus || record.spec.stages[stage].parts[0], mode: 'explore', speed: 1});
        });
      } catch { if (!cancelled) setSaveError('Your place could not be saved. Playback still works.'); }
    };
    const leaving = (): void => { persist(); mounted?.getPlayer(mounted.getState().nodeId)?.pause(); };
    window.addEventListener('pagehide', leaving);

    async function open(): Promise<void> {
      try {
        let bundle: LearningBundle;
        const media = new Map<string, string>(), captions = new Map<string, string>();
        if (online) {
          bundle = checkedBundle(await api<LearningBundle>(`/learning-paths/${encodeURIComponent(lesson.id)}`), lesson.id, true);
          // An unavailable browser cache must not prevent online playback.
          void savedLearningPath(member.id, lesson.id).then(record => {
            if (!cancelled) {
              const current = !!record && matchesSavedBundle(record.bundle, bundle);
              setSaved(current);
              if (record && !current) setCacheNote('An earlier offline copy is preserved. Save again to include the current explanation and deeper questions.');
            }
          }).catch(() => { if (!cancelled) setSaveError('Offline storage is unavailable. The online explanation still works.'); });
          bundle.lessons.forEach(record => {
            media.set(record.id, `/api/v1/lessons/${encodeURIComponent(record.id)}/video`);
            captions.set(record.id, `/api/v1/lessons/${encodeURIComponent(record.id)}/captions`);
          });
        } else {
          const cached = await savedLearningPath(member.id, lesson.id);
          if (!cached) throw new Error('This explanation has not been saved on this device. Reconnect to open it.');
          bundle = cached.bundle;
          cached.records.forEach(record => {
            if (!record.video) return;
            const source = URL.createObjectURL(record.video); urls.push(source); media.set(record.lesson.id, source);
            const caption = URL.createObjectURL(new Blob([record.captions ?? 'WEBVTT\n'], {type: 'text/vtt'}));
            urls.push(caption); captions.set(record.lesson.id, caption);
          });
          if (!cancelled) setSaved(true);
        }
        if (cancelled) { urls.forEach(url => URL.revokeObjectURL(url)); return; }
        currentBundle.current = bundle;
        const factories = Object.fromEntries(bundle.lessons.map(record => [record.id, (target: HTMLElement): StudioAPI => {
          const source = media.get(record.id) ?? '';
          const spec=record.spec;
          const adapted=spec.version===3 ? nativeLesson(spec,source,record.video_ready) :
            rendererAvailable(spec) ? adaptLesson({...record,spec},source) : undefined;
          const player = adapted ? mountLesson(target,adapted,{embedded:true,predictionFirst:true,mediaUrl:source}) :
            mountPreservedLesson(target,record,source,captions.get(record.id));
          const progress = readProgress(progressKey(member.id, record.id), lessonDuration(spec), componentIds(spec));
          progressStore.restored(record.id, progress.seconds);
          player.seek(progress.seconds); // Restore a paused scene. Never start narration on navigation.
          return player;
        }]));
        mounted = mountPath(root, bundle.path, factories, {hashNavigation: false, brand: false,
          onSelect(pathNode, player) {
            const active = bundle.lessons.find(item => item.id === pathNode.lesson_id)!;
            setDiscussion({lesson: active, stage: chapterIndex(active.spec, player.getState().time)});
            persist();
          }});
        pathApi.current = mounted; setLoading(false);
        interval = window.setInterval(() => {
          if (cancelled || !mounted) return;
          if (performance.now() - lastSave >= 1000) { persist(); lastSave = performance.now(); }
          const pathNode = bundle.path.nodes.find(item => item.id === mounted!.getState().nodeId)!;
          const active = bundle.lessons.find(item => item.id === pathNode.lesson_id)!;
          const player = mounted.getPlayer(pathNode.id);
          if (!player) return;
          const stage = chapterIndex(active.spec, player.getState().time);
          setDiscussion(previous => previous.lesson.id === active.id && previous.stage === stage ? previous : {lesson: active, stage});
        }, 250);
      } catch (failure) {
        if (!cancelled) { setError(errorMessage(failure)); setLoading(false); }
      }
    }
    void open();
    return () => {
      persist(); cancelled = true; window.clearInterval(interval); window.removeEventListener('pagehide', leaving);
      mounted?.dispose(); pathApi.current = undefined; currentBundle.current = undefined;
      urls.forEach(url => URL.revokeObjectURL(url));
    };
  }, [lesson, member.id, online, attempt]);

  async function save(): Promise<void> {
    const bundle = currentBundle.current;
    if (!online || !bundle) return;
    setSaving(true); setSaveError('');
    try { await saveLearningPath(member.id, bundle, lesson.id); setSaved(true); setCacheNote(''); }
    catch (failure) { setSaveError(errorMessage(failure)); }
    finally { setSaving(false); }
  }
  function show(answer: Answer): void {
    const current = pathApi.current;
    const stage = discussionCheckpoint(discussion.lesson.spec, answer);
    if (!current || stage === undefined) return;
    const node = currentBundle.current?.path.nodes.find(item => item.lesson_id === discussion.lesson.id);
    if (!node) return;
    current.select(node.id);
    current.getPlayer(node.id)?.seek(chapterStarts(discussion.lesson.spec)[stage]);
    setDiscussion(previous => ({...previous, stage}));
    host.current?.scrollIntoView({block: 'start'});
  }
  const active = discussion.lesson;
  return <article className="shared-learning"><div className="shared-meta">
    {active.review_needed && <p className="draft-marker" title="Independent technical review, craft review and beginner testing are still pending.">Teaching draft · review pending</p>}
  </div>
    {lesson.superseded_by && <p>This earlier revision keeps your original conversation. <a href={`#/lesson/${lesson.superseded_by}`}>Open the revised explanation</a></p>}
    {loading && <p role="status">Opening the explanation…</p>}
    {error && <div role="alert" className="error"><p>{error}</p><button onClick={() => setAttempt(value => value + 1)}>Try opening again</button></div>}
    {saveError && <p role="alert" className="error">{saveError}</p>}
    {cacheNote && <p role="status">{cacheNote}</p>}
    {!online && !loading && !error && <p role="status">Saved on this device · live chat and feedback are available when you reconnect.</p>}
    <div ref={host} className="learning-studio" aria-busy={loading}/>
    {!loading&&!error&&<div className="shared-save"><LessonSaveButton online={online} saved={saved} saving={saving} save={save}/></div>}
    {!loading && !error && <div className="lesson-bottom" aria-label={`Questions and feedback for ${active.spec.title}`}>
      <FeedbackPanel key={`feedback-${active.id}`} lesson={active} online={online} stage={discussion.stage}/>
      <ChatPanel key={`chat-${active.id}`} lesson={active} member={member} online={online} onShow={show}/>
    </div>}
  </article>;
}
