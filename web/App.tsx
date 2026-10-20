import { useCallback, useEffect, useState } from 'react';
import type { FormEvent, ReactElement } from 'react';
import { ArrowLeft, ArrowUpRight, Box, Check, ChevronRight, Download, LogOut, Search, WifiOff } from 'lucide-react';
import { api, ApiError, errorMessage } from './api';
import type { CatalogEntry, Job, Lesson, Member, RequestResult } from './contracts';
import { clearOffline, offlineCatalog, offlineMember, rememberMember, savedLesson } from './offline';
import { Scene } from './Scene';
import { LessonView } from './LessonView';
import { OwnerView } from './OwnerView';

interface InstallEvent extends Event { prompt: () => Promise<void> }
const route = (): string => decodeURIComponent(location.hash.replace(/^#\/?/, ''));
export function navigate(path = ''): void { location.hash = path ? `/${path}` : '/'; }

function Login({ onLogin }: { readonly onLogin: (member: Member) => void }): ReactElement {
  const [name, setName] = useState(''), [code, setCode] = useState('');
  const [busy, setBusy] = useState(false), [error, setError] = useState('');
  async function login(event: FormEvent): Promise<void> {
    event.preventDefault(); setBusy(true); setError('');
    try {
      const member = await api<Member>('/auth/login', { name: name.trim(), code });
      if (offlineMember()?.id !== member.id) await clearOffline();
      rememberMember(member); onLogin(member);
    } catch (error) { setError(errorMessage(error)); } finally { setBusy(false); }
  }
  return <main id="main" tabIndex={-1} className="welcome"><div className="welcome-mark"><Box size={34} strokeWidth={1.5} /></div>
    <h1>Look inside.<br />Understand what happens.</h1>
    <p>Explore the moving parts of everyday machines, one clear explanation at a time.</p>
    <form onSubmit={event => void login(event)} className="invite-form">
      <h2>Join the family alpha</h2><p className="muted">Use the invite code shared with you.</p>
      <label>Your name<input autoComplete="given-name" required maxLength={60} value={name} onChange={e => setName(e.target.value)} placeholder="What should we call you?" /></label>
      <label>Invite code<input autoComplete="off" type="password" required maxLength={180} value={code} onChange={e => setCode(e.target.value)} /></label>
      {error && <p role="alert" className="error">{error}</p>}
      <button className="primary" disabled={busy || !name.trim()}>{busy ? 'Joining…' : 'Explore Inside'}<ChevronRight size={18} /></button>
      <small>No customer API key needed. Your conversations stay private.</small>
    </form>
  </main>;
}

function JobProgress({ id, onReady }: { readonly id: string; readonly onReady: (id: string) => void }): ReactElement {
  const [job, setJob] = useState<Job | null>(null), [error, setError] = useState('');
  useEffect(() => {
    const source = new EventSource(`/api/v1/jobs/${encodeURIComponent(id)}/events`);
    source.addEventListener('progress', (event: MessageEvent<string>) => {
      const next = JSON.parse(event.data) as Job; setJob(next); setError('');
      if (next.status === 'complete' && next.lesson_id) { source.close(); onReady(next.lesson_id); }
      if (next.status === 'failed') source.close();
    });
    source.onerror = () => setError('Reconnecting to your explanation. You can leave this page; the request is saved.');
    return () => source.close();
  }, [id, onReady]);
  const split = job?.pipeline_version === 'evidence-first-1';
  const phases = split ? ['Gather evidence', 'Build the scene', 'Check the explanation', 'Add narration', 'Render video'] : ['Research & build', 'Check the explanation', 'Add narration', 'Render video'];
  const current = job?.phase === 'author' ? 1 : job?.phase === 'review' ? (split?2:1) : job?.phase.startsWith('voice') ? (split?3:2) : job?.phase === 'video' ? (split?4:3) : 0;
  return <section className="job-panel" aria-live="polite"><Box size={28} /><h2>{job?.status === 'failed' ? 'This explanation needs another look' : 'Making the invisible visible'}</h2>
    <p>{job?.error || job?.message || 'Opening your saved request…'}</p><ol>{phases.map((phase, i) => <li key={phase} className={i === current ? 'current' : ''}>{i < current ? <Check size={16} /> : <span>{i + 1}</span>}{phase}</li>)}</ol>
    <p className="muted">A new lesson can take a few minutes. Once ready, everyone can reuse it.</p>
    {error && <p className="notice">{error}</p>}<button onClick={() => navigate()}>Browse the library</button>
  </section>;
}

export function App(): ReactElement {
  const [member, setMember] = useState<Member | null>(null), [loading, setLoading] = useState(true);
  const [online, setOnline] = useState(navigator.onLine), [path, setPath] = useState(route);
  const [catalog, setCatalog] = useState<CatalogEntry[]>([]), [lesson, setLesson] = useState<Lesson | null>(null);
  const [savedIds, setSavedIds] = useState<string[]>([]);
  const [error, setError] = useState(''), [notice, setNotice] = useState(''), [busy, setBusy] = useState(false);
  const [question, setQuestion] = useState(''), [scope, setScope] = useState<'general' | 'specific'>('general');
  const [model, setModel] = useState(''), [filter, setFilter] = useState('All');
  const [install, setInstall] = useState<InstallEvent | null>(null), [help, setHelp] = useState(false);
  const ready = useCallback((id: string) => navigate(`lesson/${id}`), []);

  useEffect(() => {
    const change = (): void => setPath(route());
    const network = (): void => setOnline(navigator.onLine);
    const installable = (event: Event): void => { event.preventDefault(); setInstall(event as InstallEvent); };
    const expired = (): void => {
      setMember(null); setLesson(null); setCatalog([]); localStorage.removeItem('inside.member');
      void clearOffline().catch(error => setError(errorMessage(error)));
    };
    const offlineUnavailable = (): void => setError('The browser couldn’t prepare offline access. Online lessons still work. Reload to try setting up offline access again.');
    window.addEventListener('inside:offline-unavailable', offlineUnavailable);
    window.addEventListener('inside:unauthorized', expired);
    window.addEventListener('hashchange', change); window.addEventListener('online', network); window.addEventListener('offline', network);
    window.addEventListener('beforeinstallprompt', installable);
    return () => { window.removeEventListener('hashchange', change); window.removeEventListener('online', network); window.removeEventListener('offline', network); window.removeEventListener('beforeinstallprompt', installable); window.removeEventListener('inside:unauthorized', expired); window.removeEventListener('inside:offline-unavailable', offlineUnavailable); };
  }, []);

  useEffect(() => {
    let cancelled = false;
    async function restore(): Promise<void> {
      try {
        let current: Member | null = null;
        if (online) {
          if (localStorage.getItem('inside.revoke-pending')) {
            await api('/auth/logout', {}); localStorage.removeItem('inside.revoke-pending');
          }
          current = await api<Member>('/auth/me'); rememberMember(current);
        } else current = offlineMember();
        if (!cancelled) { setMember(current); setError(''); }
      } catch (error) {
        if (!cancelled) {
          if (error instanceof ApiError && error.status === 401) { setMember(null); localStorage.removeItem('inside.member'); await clearOffline(); }
          else setError('Couldn’t reach Inside. Check your connection and reload to try again.');
        }
      } finally { if (!cancelled) setLoading(false); }
    }
    void restore(); return () => { cancelled = true; };
  }, [online]);

  useEffect(() => {
    if (!member) return;
    let cancelled = false;
    async function load(): Promise<void> {
      try {
        const entries = online ? await api<CatalogEntry[]>('/lessons') : await offlineCatalog(member!.id);
        const saved = online ? await offlineCatalog(member!.id) : entries;
        if (!cancelled) { setCatalog(entries); setSavedIds(saved.map(e => e.id)); }
      } catch (error) { if (!cancelled) setError(errorMessage(error)); }
    }
    void load(); return () => { cancelled = true; };
  }, [member, online, path]);

  useEffect(() => {
    if (!member || !path.startsWith('lesson/')) return;
    const id = path.slice(7); let cancelled = false;
    async function load(): Promise<void> {
      try {
        const result = online ? await api<Lesson>(`/lessons/${encodeURIComponent(id)}`) : (await savedLesson(member!.id, id))?.lesson;
        if (!result) throw new Error('This explanation hasn’t been saved on this device. Reconnect to open it.');
        if (!cancelled) { setLesson(result); setError(''); }
      } catch (error) { if (!cancelled) { setLesson(null); setError(errorMessage(error)); } }
    }
    void load(); return () => { cancelled = true; };
  }, [member, online, path]);

  async function logout(): Promise<void> {
    setBusy(true); localStorage.setItem('inside.revoke-pending', '1');
    try {
      if (online) { await api('/auth/logout', {}); localStorage.removeItem('inside.revoke-pending'); }
      localStorage.removeItem('inside.member'); await clearOffline();
      for (const key of Object.keys(sessionStorage)) if (key.startsWith('inside.chat.')) sessionStorage.removeItem(key);
      setMember(null); setLesson(null); setCatalog([]); setError(''); navigate();
    } catch (error) { setError(`Couldn’t finish signing out: ${errorMessage(error)}`); }
    finally { setBusy(false); }
  }
  async function request(event: FormEvent): Promise<void> {
    event.preventDefault(); setBusy(true); setNotice(''); setError('');
    try {
      const result = await api<RequestResult>('/requests', { question, scope, model });
      if (result.kind === 'lesson' && result.lesson_id) ready(result.lesson_id);
      else if (result.kind === 'job' && result.job_id) navigate(`job/${result.job_id}`);
      else setNotice(result.message || 'Your request has been saved.');
    } catch (error) { setError(errorMessage(error)); } finally { setBusy(false); }
  }

  const categories = ['All', 'Saved', ...new Set(catalog.map(e => e.category))];
  const entries = catalog.filter(e => filter === 'All' || (filter === 'Saved' ? savedIds.includes(e.id) : filter === e.category));
  return <><a className="skip-link" href="#main" onClick={e => { e.preventDefault(); document.getElementById('main')?.focus(); }}>Skip to content</a><header className={lesson?.id === "air-conditioner-craft" && path.startsWith("lesson/") ? "topbar studio-nav" : "topbar"}><a href="#/" className="brand" aria-label="Inside home"><Box size={25} strokeWidth={1.6} />inside<span>family alpha</span></a>
    <nav aria-label="Main navigation">{member && <><a href="#/" aria-current={!path ? 'page' : undefined}>Library</a>{member.owner && online && <a href="#/owner" aria-current={path === 'owner' ? 'page' : undefined}>Alpha insights</a>}</>}
      <button aria-label="Install Inside" onClick={() => { if (install) void install.prompt(); else setHelp(!help); }}><Download size={18} /><span className="install-label">Install</span></button>
      {member && <button onClick={() => void logout()} disabled={busy} aria-label={`Sign out ${member.name}`}><LogOut size={17} /></button>}</nav>
    </header>
    {help && <aside className="install-help"><strong>Keep Inside close.</strong><p>On iPhone or iPad, open in Safari, tap Share, then Add to Home Screen. On Android or desktop, choose Install app from your browser menu.</p><button onClick={() => setHelp(false)}>Got it</button></aside>}
    {!online && <div className="offline-banner" role="status"><WifiOff size={16} />Offline · Saved explanations work. New lessons, feedback and live chat need a connection.</div>}
    {loading ? <main id="main" tabIndex={-1} className="loading" aria-live="polite">Opening Inside…</main> : !member ? <>{error && <p role="alert" className="error shell-error">{error}</p>}<Login onLogin={setMember} /></> : <main id="main" tabIndex={-1} className={lesson?.id === "air-conditioner-craft" && path.startsWith("lesson/") ? "app-shell studio-shell" : "app-shell"}>
      {error && <div role="alert" className="error">{error}<button onClick={() => setError('')} aria-label="Dismiss error">Dismiss</button></div>}
      {path.startsWith('job/') ? <JobProgress id={path.slice(4)} onReady={ready} /> : path === 'owner' ? <OwnerView /> : path.startsWith('lesson/') ? <>
        <button className="back" onClick={() => navigate()}><ArrowLeft size={16} />All explanations</button>
        {lesson && lesson.id === path.slice(7) ? <LessonView key={lesson.id} lesson={lesson} member={member} online={online} /> : !error && <p role="status">Opening the explanation…</p>}
      </> : <>
        <section className="library-intro"><div><p className="eyebrow">Curiosity, made visible</p><h1>How does it work?</h1><p>Look inside the things around you.<br className="desktop-only" /> Follow the parts. Understand the principle.</p></div><div className="library-count"><strong>{catalog.length}</strong><span>{online ? 'shared explanations' : 'saved on this device'}</span></div></section>
        <form className="ask-machine" onSubmit={event => void request(event)}><label htmlFor="machine-question">What would you like to understand?</label>
          <div className="search-row"><Search size={21} /><input id="machine-question" required minLength={3} maxLength={180} value={question} onChange={e => setQuestion(e.target.value)} placeholder="An air conditioner, a pressure cooker, a television…" /><button className="primary" disabled={busy || !online}>{busy ? 'Looking…' : 'Explain it'}<ArrowUpRight size={18} /></button></div>
          <div className="scope-row"><label><input type="radio" name="scope" checked={scope === 'general'} onChange={() => setScope('general')} />Understand the principles</label><label><input type="radio" name="scope" checked={scope === 'specific'} onChange={() => setScope('specific')} />My specific machine</label></div>
          {scope === 'specific' && <label className="model-field">Make and model, if you know it<input value={model} onChange={e => setModel(e.target.value)} maxLength={120} placeholder="e.g. the model printed on the label" /><small>Exact-model manuals and photos are planned. This alpha can show the general mechanism, with its limits clearly labelled.</small></label>}
          <p className="search-note">We look in the library first. A missing machine becomes a new shared lesson using the family’s AI budget.</p>
          {notice && <p role="status" className="notice">{notice}</p>}
        </form>
        <section aria-label="Explanation library" className="library"><div className="section-heading"><h2>{online ? 'Inside the library' : 'Your saved explanations'}</h2><div className="filters" aria-label="Filter by category">{categories.map(category => <button key={category} aria-pressed={filter === category} onClick={() => setFilter(category)}>{category}</button>)}</div></div>
          {!entries.length && <div className="empty"><Box size={28} /><h3>{online && filter !== 'Saved' ? 'The library starts with a question.' : 'Nothing saved here yet.'}</h3><p>{online && filter !== 'Saved' ? 'Ask about a machine above. New explanations will appear here when ready.' : 'Open an explanation while connected and choose Save offline.'}</p></div>}
          <div className="catalog">{entries.map((entry, i) => <a className="catalog-row" key={entry.id} href={`#/lesson/${entry.id}`}><div className="catalog-art"><Scene spec={entry.preview} preview /></div><div className="catalog-copy"><div className="catalog-meta"><span>{entry.category}</span><span>{Math.round(entry.duration)} sec · {entry.preview.stages.length} steps</span></div><h3>{entry.title}</h3><p>{entry.question}</p><small>{entry.family}{entry.review_needed && <span className="draft-marker"> · Learning draft</span>}</small></div><span className="open-lesson">Explore<ChevronRight size={18} /></span><span className="catalog-index" aria-hidden="true">{String(i + 1).padStart(2, '0')}</span></a>)}</div>
        </section><footer className="library-footer">Built for curious people. Schematic explanations, clear assumptions, room for questions.</footer>
      </>}
    </main>}</>;
}
