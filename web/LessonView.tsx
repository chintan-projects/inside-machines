import { useCallback, useEffect, useRef, useState } from 'react';
import type { ReactElement } from 'react';
import { Pause, Play, RotateCcw } from 'lucide-react';
import type { Answer, Lesson, Member } from './contracts';
import { offlineMember } from './offline';
import { ChatPanel, FeedbackPanel } from './LessonDiscussion';
import { AcStudio } from './ac/Studio';
import { LessonSaveButton, useLessonAssets } from './useLessonAssets';
import { duration, Scene, stageAt } from './Scene';
import { progressKey, readProgress } from './progress';
import { WasherExperiment } from './WasherExperiment';

interface Props { readonly lesson: Lesson; readonly member: Member; readonly online: boolean }
export function LessonView(props: Props): ReactElement {
  return props.lesson.id === 'air-conditioner-craft' ? <AcStudio {...props} /> : <StandardLessonView {...props} />;
}
function StandardLessonView({ lesson, member, online }: Props): ReactElement {
  const { spec } = lesson, total = duration(spec);
  const key = progressKey(member.id, lesson.id);
  const [initial] = useState(() => readProgress(key, total, [spec.stages[0].focus || spec.stages[0].parts[0], ...spec.parts.map(p => p.id)]));
  const [seconds, setSeconds] = useState(initial.seconds), [playing, setPlaying] = useState(false), [speed, setSpeed] = useState(initial.speed);
  const [selected, setSelected] = useState(initial.selected);
  const [mode, setMode] = useState<'explore' | 'watch'>(initial.mode);
  const { saved, saving, saveError, setSaveError, videoUrl, captionUrl, save } = useLessonAssets(lesson,member,online);
  const [prediction, setPrediction] = useState(false), [zoom, setZoom] = useState(false);
  const explorable = new Set(spec.stages.flatMap(s => s.parts));
  const namedComponents = spec.parts.filter(p => p.shape === "text" && p.id.startsWith("label-")).sort((a,b) => (Number.parseInt(a.label,10)||99)-(Number.parseInt(b.label,10)||99));
  const components = spec.parts.filter(p => explorable.has(p.id) && p.shape !== 'text');
  const clock = useRef(initial.seconds);
  const video = useRef<HTMLVideoElement>(null);
  const [stageIndex] = stageAt(spec, seconds), stage = spec.stages[stageIndex];
  const previousChapter = useRef(stageIndex);
  const updateTime = useCallback((time: number): void => {
    const [index] = stageAt(spec,time);
    if (previousChapter.current !== index) {
      setSelected(spec.stages[index].focus || spec.stages[index].parts[0]);
      previousChapter.current = index;
    }
    setSeconds(time);
  }, [spec]);
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
  }, [key, member.id, selected, mode, speed, setSaveError]);
  useEffect(() => {
    if (!playing) return;
    let frame = 0, last = performance.now();
    function tick(now: number): void {
      const next = Math.min(total, clock.current + Math.min(.1, (now - last) / 1000) * speed);
      last = now; clock.current = next; updateTime(next);
      if (next >= total) setPlaying(false); else frame = requestAnimationFrame(tick);
    }
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [playing, total, speed, updateTime]);

  function goTo(index: number, id?: string): void {
    previousChapter.current = index;
    setPlaying(false); setSeconds(spec.stages.slice(0, index).reduce((sum, s) => sum + s.duration, 0));
    setSelected(id || spec.stages[index].focus || spec.stages[index].parts[0]); setMode('explore');
  }
  function inspectPart(id: string): void {
    const chapter = spec.stages.findIndex((s,i) => i > 0 && s.focus === id);
    if (chapter >= 0) goTo(chapter,id); else setSelected(id);
  }
  function jumpToChapter(index: number): void {
    if (mode === 'watch' && video.current) {
      const time = spec.stages.slice(0,index).reduce((sum,s) => sum+s.duration,0);
      video.current.currentTime = time; setSeconds(time);
    } else goTo(index);
  }
  function showAnswer(answer: Answer): void {
    if (answer.stage !== null) goTo(answer.stage, answer.part || undefined);
    else if (answer.part) { setSelected(answer.part); setMode('explore'); }
    document.querySelector('.lesson-player')?.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth', block: 'start' });
  }
  return <article className="lesson"><div className="lesson-heading"><div><p className="eyebrow">{spec.family}</p><h1>{spec.title}</h1><p>{spec.big_idea}</p></div><LessonSaveButton online={online} saved={saved} saving={saving} save={save} /></div>
    {lesson.review_needed && !lesson.superseded_by && <p className="draft-marker">Learning draft · component labels and the teaching sequence are still under review.</p>}
    {lesson.superseded_by && <p className="lesson-premise">This is an earlier teaching draft. Your conversation stays with this version. <a href={`#/lesson/${lesson.superseded_by}`}>Open the revised explanation</a></p>}
    {saveError && <p role="alert" className="error">{saveError}</p>}

    <div className="lesson-workspace"><section className="lesson-player" aria-label="Visual explanation"><div className="player-header"><div className="segmented"><button aria-pressed={mode === 'explore'} onClick={() => setMode('explore')}>Explore the parts</button><button aria-pressed={mode === 'watch'} disabled={!lesson.video_ready} onClick={() => { setMode('watch'); setPlaying(false); }}>Watch & listen</button></div><span className="schematic-label">Schematic · time condensed</span></div>
      {mode === 'watch' ? <div className="video-container"><video ref={video} key={videoUrl} onLoadedMetadata={e => { e.currentTarget.currentTime = seconds; }} onTimeUpdate={e => updateTime(e.currentTarget.currentTime)} controls playsInline preload="metadata" src={videoUrl} onError={() => setSaveError('Couldn’t load the narrated video. Try the interactive explanation or reconnect.')}><track kind="captions" src={captionUrl} srcLang="en" label="English captions" /></video><div className="spoken-caption" aria-label="Narration transcript"><span>Narration · chapter {stageIndex+1}</span><p>{stage.narration}</p></div></div> : <>
        <Scene spec={spec} seconds={seconds} selected={selected} onSelect={inspectPart} zoom={zoom} />
        <div className="diagram-tools"><span><i className="key-tube" />{lesson.id === "air-conditioner-craft" ? "Refrigerant in sealed tubing" : "Flow through the machine"}</span>{lesson.id === "air-conditioner-craft" && <span><i className="key-heat" />Heat crossing the coil</span>}<button aria-pressed={zoom} onClick={() => setZoom(!zoom)}>{zoom ? 'Whole machine' : 'Enlarge selected part'}</button></div>
        <div className="player-controls"><button className="play-button" aria-label={playing ? 'Pause explanation' : 'Play explanation'} onClick={() => { if (seconds >= total) { updateTime(0); clock.current = 0; } setPlaying(!playing); }}>{playing ? <Pause size={20} fill="currentColor" /> : <Play size={20} fill="currentColor" />}</button><input aria-label="Explanation timeline in seconds" type="range" min="0" max={total} step=".05" value={seconds} onChange={e => { setPlaying(false); updateTime(Number(e.target.value)); }} /><span className="time-label">{Math.floor(seconds)} / {Math.round(total)}s</span><button aria-label="Restart explanation" onClick={() => goTo(0)}><RotateCcw size={17} /></button><label className="speed-label"><span className="sr-only">Playback speed</span><select value={speed} onChange={e => setSpeed(Number(e.target.value))}><option value=".5">0.5×</option><option value="1">1×</option><option value="2">2×</option></select></label></div>
        <p className="scene-hint">Select a working component to see its job. Motion shows direction, not measured speed.</p>
      </>}
      <div className="stage-tabs" aria-label="Explanation steps">{spec.stages.map((s, i) => <button key={s.title} aria-current={i === stageIndex ? 'step' : undefined} onClick={() => jumpToChapter(i)}>{lesson.id !== "air-conditioner-craft" && <span>{i + 1}</span>}{s.title}</button>)}</div>
    </section><aside className="mechanism-notes"><p className="eyebrow">Step {stageIndex + 1} of {spec.stages.length}</p><h2>{stage.title}</h2>{stage.input_state && <div className="state-change"><div><span>Comes in</span><strong>{stage.input_state}</strong></div><div><span>Leaves</span><strong>{stage.output_state}</strong></div></div>}<p>{stage.explanation}</p><div className="cause"><strong>Why this happens</strong><p>{stage.cause}</p></div>{stage.source_indices && stage.source_indices.length > 0 && <p className="chapter-sources">Based on {stage.source_indices.map((n,i) => <span key={n}>{i > 0 ? ' · ' : ''}<a href={spec.sources[n]?.url} target="_blank" rel="noreferrer">Source {n+1}</a></span>)}</p>}{namedComponents.length > 0 && <div className="component-buttons" aria-label="Choose a component">{namedComponents.map(label => <button key={label.id} aria-pressed={selected === label.id.slice(6)} onClick={() => inspectPart(label.id.slice(6))}>{label.label}</button>)}</div>}<details className="extra-parts" open={!namedComponents.length}><summary>Airflow, tubing and other parts</summary><label className="part-picker">Parts and paths<select value={selected} onChange={e => setSelected(e.target.value)}>{components.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}</select></label></details>{part && <div className="part-description"><strong>{part.name}</strong><p>{part.description}</p></div>}</aside></div>
    <div className="lesson-bottom"><section className="learning-notes">{lesson.id === 'washing-machine' && <WasherExperiment />}<h2>Make the idea yours</h2><p>{spec.prediction}</p><button onClick={() => setPrediction(!prediction)} aria-expanded={prediction}>{prediction ? 'Hide the explanation' : 'Think it through, then reveal'}</button>{prediction && <p className="prediction-answer">{spec.prediction_answer}</p>}
      <details className="evidence"><summary>Sources, assumptions & what this shows</summary><p>{lesson.quality === 'ai-reviewed' ? 'AI-generated and checked by a second automated pass. This is not human verification.' : lesson.quality === 'authored-craft' ? 'An authored teaching benchmark. References were consulted; independent technical review remains outstanding. The voice is computer-generated.' : 'An authored starter lesson. Its geometry and timing are simplified for learning.'}</p><h3>Assumptions</h3><ul>{spec.assumptions.map(a => <li key={a}>{a}</li>)}</ul><h3>Sources</h3><ol>{spec.sources.map(source => <li key={source.url}><a href={source.url} target="_blank" rel="noreferrer">{source.title}</a><p>{source.supports}</p></li>)}</ol><p className="muted">Use your manufacturer’s manual for operating or repairing a real appliance.</p></details>
      <FeedbackPanel lesson={lesson} online={online} stage={stageIndex} />
    </section><ChatPanel lesson={lesson} member={member} online={online} onShow={showAnswer} /></div>
  </article>;
}
