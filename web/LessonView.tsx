import { useEffect, useRef, useState } from 'react';
import type { FormEvent, ReactElement } from 'react';
import { Check, Download, MessageCircle, Pause, Play, RotateCcw, Send, ThumbsDown, ThumbsUp } from 'lucide-react';
import { api, askChat, errorMessage } from './api';
import type { Answer, Conversation, Feedback, Lesson, Member } from './contracts';
import { offlineMember, savedLesson, saveLesson } from './offline';
import { duration, Scene, stageAt } from './Scene';
import { progressKey, readProgress } from './progress';
import { WasherExperiment } from './WasherExperiment';

interface Props { readonly lesson: Lesson; readonly member: Member; readonly online: boolean }
export function LessonView({ lesson, member, online }: Props): ReactElement {
  const { spec } = lesson, total = duration(spec);
  const key = progressKey(member.id, lesson.id);
  const [initial] = useState(() => readProgress(key, total, spec.parts.map(p => p.id)));
  const [seconds, setSeconds] = useState(initial.seconds), [playing, setPlaying] = useState(false), [speed, setSpeed] = useState(initial.speed);
  const [selected, setSelected] = useState(initial.selected);
  const [mode, setMode] = useState<'explore' | 'watch'>(initial.mode);
  const [saved, setSaved] = useState(false), [saving, setSaving] = useState(false), [saveError, setSaveError] = useState('');
  const [videoUrl, setVideoUrl] = useState(`/api/v1/lessons/${encodeURIComponent(lesson.id)}/video`);
  const [captionUrl, setCaptionUrl] = useState(`/api/v1/lessons/${encodeURIComponent(lesson.id)}/captions`);
  const [prediction, setPrediction] = useState(false);
  const clock = useRef(initial.seconds);
  const [stageIndex] = stageAt(spec, seconds), stage = spec.stages[stageIndex];
  const part = spec.parts.find(p => p.id === selected);

  useEffect(() => { clock.current = seconds; }, [seconds]);
  useEffect(() => {
    const persist = (): void => {
      if (offlineMember()?.id !== member.id) return;
      try { localStorage.setItem(key, JSON.stringify({ seconds:clock.current, selected, mode, speed })); }
      catch { setSaveError('The browser couldn’t save your place. Playback still works.'); }
    };
    const interval = window.setInterval(persist, 1000);
    window.addEventListener('pagehide', persist);
    return () => { window.clearInterval(interval); window.removeEventListener('pagehide', persist); persist(); };
  }, [key, member.id, selected, mode, speed]);
  useEffect(() => {
    if (!playing) return;
    let frame = 0, last = performance.now();
    function tick(now: number): void {
      const next = Math.min(total, clock.current + Math.min(.1, (now - last) / 1000) * speed);
      last = now; clock.current = next; setSeconds(next);
      if (next >= total) setPlaying(false); else frame = requestAnimationFrame(tick);
    }
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [playing, total, speed]);
  useEffect(() => {
    let cancelled = false; const urls: string[] = [];
    void savedLesson(member.id, lesson.id).then(record => {
      if (cancelled || !record) return;
      setSaved(true);
      if (!online && record.video) {
        const video = URL.createObjectURL(record.video); urls.push(video); setVideoUrl(video);
        const caption = URL.createObjectURL(new Blob([record.captions || 'WEBVTT\n'], { type: 'text/vtt' })); urls.push(caption); setCaptionUrl(caption);
      }
    }).catch(error => { if (!cancelled) setSaveError(errorMessage(error)); });
    return () => { cancelled = true; urls.forEach(url => URL.revokeObjectURL(url)); };
  }, [member.id, lesson.id, online]);

  function goTo(index: number, id?: string): void {
    setPlaying(false); setSeconds(spec.stages.slice(0, index).reduce((sum, s) => sum + s.duration, 0));
    setSelected(id || spec.stages[index].parts[0]); setMode('explore');
  }
  function showAnswer(answer: Answer): void {
    if (answer.stage !== null) goTo(answer.stage, answer.part || undefined);
    else if (answer.part) { setSelected(answer.part); setMode('explore'); }
    document.querySelector('.lesson-player')?.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth', block: 'start' });
  }
  async function save(): Promise<void> {
    setSaving(true); setSaveError('');
    try { await saveLesson(member.id, lesson); setSaved(true); }
    catch (error) { setSaveError(errorMessage(error)); } finally { setSaving(false); }
  }
  return <article className="lesson"><div className="lesson-heading"><div><p className="eyebrow">{spec.family}</p><h1>{spec.title}</h1><p>{spec.big_idea}</p></div><button className="save-button" disabled={!online || saving} onClick={() => void save()}>{saved ? <Check size={17} /> : <Download size={17} />}{saving ? 'Saving…' : saved ? 'Saved offline' : 'Save offline'}</button></div>
    {saveError && <p role="alert" className="error">{saveError}</p>}
    <div className="lesson-workspace"><section className="lesson-player" aria-label="Visual explanation"><div className="player-header"><div className="segmented"><button aria-pressed={mode === 'explore'} onClick={() => setMode('explore')}>Explore the parts</button><button aria-pressed={mode === 'watch'} disabled={!lesson.video_ready} onClick={() => { setMode('watch'); setPlaying(false); }}>Watch & listen</button></div><span className="schematic-label">Schematic · time condensed</span></div>
      {mode === 'watch' ? <div className="video-container"><video key={videoUrl} controls playsInline preload="metadata" src={videoUrl} onError={() => setSaveError('Couldn’t load the narrated video. Try the interactive explanation or reconnect.')}><track kind="captions" src={captionUrl} srcLang="en" label="English captions" default /></video><p>Computer-generated narration · Use the player’s CC control for captions.</p></div> : <>
        <Scene spec={spec} seconds={seconds} selected={selected} onSelect={setSelected} />
        <div className="player-controls"><button className="play-button" aria-label={playing ? 'Pause explanation' : 'Play explanation'} onClick={() => { if (seconds >= total) { setSeconds(0); clock.current = 0; } setPlaying(!playing); }}>{playing ? <Pause size={20} fill="currentColor" /> : <Play size={20} fill="currentColor" />}</button><input aria-label="Explanation timeline in seconds" type="range" min="0" max={total} step=".05" value={seconds} onChange={e => { setPlaying(false); setSeconds(Number(e.target.value)); }} /><span className="time-label">{Math.floor(seconds)} / {Math.round(total)}s</span><button aria-label="Restart explanation" onClick={() => { setSeconds(0); setPlaying(false); }}><RotateCcw size={17} /></button><label className="speed-label"><span className="sr-only">Playback speed</span><select value={speed} onChange={e => setSpeed(Number(e.target.value))}><option value=".5">0.5×</option><option value="1">1×</option><option value="2">2×</option></select></label></div>
        <p className="scene-hint">Select a part to see what it does. Playback is silent; Watch & listen includes narration.</p>
      </>}
      <div className="stage-tabs" aria-label="Explanation steps">{spec.stages.map((s, i) => <button key={s.title} aria-current={i === stageIndex ? 'step' : undefined} onClick={() => goTo(i)}><span>{i + 1}</span>{s.title}</button>)}</div>
    </section><aside className="mechanism-notes"><p className="eyebrow">Step {stageIndex + 1} of {spec.stages.length}</p><h2>{stage.title}</h2><p>{stage.explanation}</p><div className="cause"><strong>Why this happens</strong><p>{stage.cause}</p></div><label className="part-picker">Look closer<select value={selected} onChange={e => setSelected(e.target.value)}>{spec.parts.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}</select></label>{part && <div className="part-description"><strong>{part.name}</strong><p>{part.description}</p></div>}</aside></div>
    <div className="lesson-bottom"><section className="learning-notes">{lesson.id === 'washing-machine' && <WasherExperiment />}<h2>Make the idea yours</h2><p>{spec.prediction}</p><button onClick={() => setPrediction(!prediction)} aria-expanded={prediction}>{prediction ? 'Hide the explanation' : 'Think it through, then reveal'}</button>{prediction && <p className="prediction-answer">{spec.prediction_answer}</p>}
      <details className="evidence"><summary>Sources, assumptions & what this shows</summary><p>{lesson.quality === 'ai-reviewed' ? 'AI-generated and checked by a second automated pass. This is not human verification.' : 'An authored starter lesson. Its geometry and timing are simplified for learning.'}</p><h3>Assumptions</h3><ul>{spec.assumptions.map(a => <li key={a}>{a}</li>)}</ul><h3>Sources</h3><ol>{spec.sources.map(source => <li key={source.url}><a href={source.url} target="_blank" rel="noreferrer">{source.title}</a><p>{source.supports}</p></li>)}</ol><p className="muted">Use your manufacturer’s manual for operating or repairing a real appliance.</p></details>
      <FeedbackPanel lesson={lesson} online={online} stage={stageIndex} />
    </section><ChatPanel lesson={lesson} member={member} online={online} onShow={showAnswer} /></div>
  </article>;
}

function FeedbackPanel({ lesson, online, stage }: { readonly lesson: Lesson; readonly online: boolean; readonly stage: number }): ReactElement {
  const [feedback, setFeedback] = useState<Feedback | null>(lesson.feedback), [reason, setReason] = useState(lesson.feedback?.reason || '');
  const [busy, setBusy] = useState(false), [status, setStatus] = useState(''), [error, setError] = useState('');
  async function vote(value: 'up' | 'down', text = reason): Promise<void> {
    setBusy(true); setError('');
    try { await api(`/lessons/${encodeURIComponent(lesson.id)}/feedback`, { value, reason: text, stage }); setFeedback({ value, reason: text }); setStatus('Thanks. Your feedback is saved.'); }
    catch (error) { setError(errorMessage(error)); } finally { setBusy(false); }
  }
  return <section className="feedback"><h3>Did this help you understand?</h3><div className="vote-buttons"><button disabled={!online || busy} aria-pressed={feedback?.value === 'up'} onClick={() => void vote('up')}><ThumbsUp size={18} />Yes, it helped</button><button disabled={!online || busy} aria-pressed={feedback?.value === 'down'} onClick={() => void vote('down')}><ThumbsDown size={18} />Not quite</button></div>
    {feedback && <form onSubmit={e => { e.preventDefault(); void vote(feedback.value); }}><label>What worked, or what was confusing? <span className="muted">Optional</span><textarea maxLength={600} rows={2} value={reason} onChange={e => setReason(e.target.value)} /></label><button disabled={!online || busy}>Save a note</button></form>}
    {status && <p role="status" className="muted">{status}</p>}{error && <p role="alert" className="error">{error}</p>}
  </section>;
}

interface ChatProps extends Props { readonly onShow: (answer: Answer) => void }
function ChatPanel({ lesson, member, online, onShow }: ChatProps): ReactElement {
  const [chat, setChat] = useState<Conversation | null>(null), [question, setQuestion] = useState('');
  const [busy, setBusy] = useState(false), [status, setStatus] = useState(''), [error, setError] = useState('');
  const [suggestion, setSuggestion] = useState<number | null>(null);
  const key = `inside.chat.${member.id}.${lesson.id}`;
  const historyEnd = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const id = sessionStorage.getItem(key); if (!id || !online) return;
    let cancelled = false;
    void api<Conversation>(`/chats/${encodeURIComponent(id)}`).then(result => { if (!cancelled) setChat(result); }).catch(error => { if (!cancelled) setError(errorMessage(error)); });
    return () => { cancelled = true; };
  }, [key, online]);
  useEffect(() => { if (chat?.messages.length) historyEnd.current?.scrollIntoView({ block: 'nearest' }); }, [chat]);
  async function send(event: FormEvent): Promise<void> {
    event.preventDefault(); if (!question.trim()) return;
    setBusy(true); setError(''); setStatus('Opening your private conversation…');
    try {
      const current = chat || await api<Conversation>('/chats', { lesson_id: lesson.id });
      sessionStorage.setItem(key, current.id); setChat(current);
      const result = await askChat(current.id, question.trim(), setStatus); setChat(result); setQuestion('');
    } catch (error) { setError(errorMessage(error)); } finally { setBusy(false); setStatus(''); }
  }
  return <section className="chat-panel" aria-label="Lesson questions"><div className="chat-heading"><MessageCircle size={21} /><div><h2>Keep asking</h2><p>Start with a question, or follow your curiosity.</p></div></div><div className="suggested-questions">{lesson.spec.questions.map((q, i) => <button key={q.question} aria-expanded={suggestion === i} onClick={() => setSuggestion(suggestion === i ? null : i)}>{q.question}</button>)}</div>
    {suggestion !== null && <div className="suggested-answer"><p>{lesson.spec.questions[suggestion].answer}</p><button onClick={() => { const q = lesson.spec.questions[suggestion]; onShow({ answer: q.answer, stage: q.stage, part: q.part || null, source_indices: [], uncertain: false }); }}>Show me in the machine</button><small>Included with this lesson · works offline</small></div>}
    <div className="chat-messages" aria-live="polite">{chat?.messages.map((message, i) => <div key={`${message.at}-${i}`} className={`chat-message ${message.role}`}><strong>{message.role === 'user' ? 'You' : 'Inside'}</strong><p>{message.text}</p>{message.answer?.uncertain && <small>This answer has uncertainty. Check the lesson’s sources.</small>}{message.answer && (message.answer.stage !== null || message.answer.part) && <button onClick={() => onShow(message.answer!)}>Show me</button>}{message.answer && message.answer.source_indices.length > 0 && <div className="answer-sources">{message.answer.source_indices.map(index => <a key={index} href={lesson.spec.sources[index]?.url} target="_blank" rel="noreferrer">Source {index + 1}</a>)}</div>}</div>)}<div ref={historyEnd} /></div>
    <form className="chat-form" onSubmit={event => void send(event)}><label htmlFor="followup">Ask a follow-up<textarea id="followup" required minLength={3} maxLength={700} rows={2} value={question} onChange={e => setQuestion(e.target.value)} placeholder="What would happen if…" disabled={!online || busy} /></label><button className="primary" disabled={!online || busy || question.trim().length < 3}><Send size={17} />{busy ? 'Preparing reply…' : 'Ask Inside'}</button></form>
    {status && <p role="status" className="muted">{status}</p>}{error && <p role="alert" className="error">{error}</p>}
    <small className="chat-privacy">Your chat is private. Live replies use the alpha’s AI budget and don’t change the shared lesson.</small>
  </section>;
}
