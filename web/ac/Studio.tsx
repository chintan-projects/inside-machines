import { useRef, useState } from "react";
import type { ReactElement } from "react";
import { ArrowLeft, ArrowRight, Headphones, Pause, Play, RotateCcw, Volume2 } from "lucide-react";
import type { Answer, Lesson, Member } from "../contracts";
import { ChatPanel, FeedbackPanel } from "../LessonDiscussion";
import { AcLearningCheck } from "../AcLearningCheck";
import { LessonSaveButton, useLessonAssets } from "../useLessonAssets";
import { Hardware } from "./Hardware";
import { Experiment } from "./Experiment";
import { story } from "./story";
import { duration, playingMediaTime } from "../lessonTimeline";
import type { Placement } from "./story";
import { useGuide, useMedia } from "./useGuide";
import "./studio.css";

interface Props {
  readonly lesson: Lesson;
  readonly member: Member;
  readonly online: boolean;
}
export function AcStudio({ lesson, member, online }: Props): ReactElement {
  const audio = useRef<HTMLAudioElement>(null);
  const guide = useGuide(lesson, member, audio),
    assets = useLessonAssets(lesson, member, online);
  const compact = useMedia("(max-width:760px)"),
    reduced = useMedia("(prefers-reduced-motion:reduce)");
  const [placement, setPlacement] = useState<Placement>("outside"),
    [overview, setOverview] = useState(false);
  const current = story[guide.step],
    chapter = lesson.spec.stages[guide.step];
  function jump(index: number): void {
    guide.jump(index);
    setOverview(false);
    setPlacement("outside");
    if (compact)
      requestAnimationFrame(() =>
        document
          .querySelector(".ac-step-copy")
          ?.scrollIntoView({ behavior: reduced ? "instant" : "smooth", block: "start" }),
      );
  }
  function inspect(id: string): void {
    const primary = story.findIndex((s, i) => i > 0 && s.focus === id);
    const index =
      primary >= 0 ? primary : lesson.spec.stages.findIndex((s, i) => i > 0 && s.parts.includes(id));
    if (index >= 0) jump(index);
  }
  function show(answer: Answer): void {
    if (answer.stage !== null) jump(answer.stage);
    else if (answer.part) inspect(answer.part);
    document
      .querySelector(".ac-lesson")
      ?.scrollIntoView({ behavior: reduced ? "instant" : "smooth", block: "start" });
  }
  async function listen(): Promise<void> {
    if (guide.seconds >= duration(lesson.spec) - 0.1) {
      setPlacement("outside");
      setOverview(false);
    }
    await guide.listen();
    if (compact && audio.current && !audio.current.paused)
      document.querySelector(".ac-step-copy")?.scrollIntoView({
        behavior: reduced ? "instant" : "smooth",
        block: "start",
      });
  }
  function experiment(value: Placement): void {
    guide.jump(5);
    setPlacement(value);
    setOverview(true);
  }
  return (
    <article className="ac-studio">
      <header className="ac-heading">
        <div>
          <p>Look inside an air conditioner</p>
          <h1>Where does the room’s heat go?</h1>
        </div>
        <LessonSaveButton online={online} saved={assets.saved} saving={assets.saving} save={assets.save} />
      </header>
      {(guide.error || assets.saveError) && (
        <p role="alert" className="error">
          {guide.error || assets.saveError}
        </p>
      )}
      <section className="ac-lesson" aria-label="Guided air conditioner explanation">
        <aside className="ac-guide">
          <div className="ac-guide-label">Follow the heat</div>
          <ol>
            {story.map((step, i) => (
              <li key={step.short}>
                <button aria-current={guide.step === i ? "step" : undefined} onClick={() => jump(i)}>
                  <span>{i < guide.step ? "✓" : i + 1}</span>
                  <div>{step.short}</div>
                </button>
              </li>
            ))}
          </ol>
          <div className="ac-guide-bottom">
            <button
              className={guide.listening ? "ac-listening" : ""}
              disabled={!lesson.video_ready || guide.loading}
              onClick={() => void listen()}
            >
              {guide.listening ? <Pause size={17} /> : <Headphones size={17} />}
              <span>
                {guide.loading
                  ? "Loading narration…"
                  : guide.listening
                    ? "Pause narration"
                    : "Listen & watch"}
              </span>
            </button>
            <button onClick={() => jump(0)}>
              <RotateCcw size={15} />
              Start over
            </button>
          </div>
        </aside>
        <div className="ac-stage">
          <div className="ac-step-copy" aria-live="polite">
            <span className="ac-step-count">
              {guide.step + 1} / {story.length}
            </span>
            <div>
              <h2>{current.title}</h2>
              <p>{current.copy}</p>
            </div>
          </div>
          <div className="ac-art">
            <Hardware
              step={guide.step}
              focus={current.focus}
              running={guide.motion && !reduced}
              placement={placement}
              onSelect={inspect}
              compact={compact}
              overview={overview}
            />
            <div className="ac-scene-tools">
              {compact && guide.step !== 0 && guide.step !== 5 && (
                <button aria-pressed={overview} onClick={() => setOverview(!overview)}>
                  {overview ? "Focus on this part" : "See both units"}
                </button>
              )}
              <button
                aria-label={guide.motion ? "Pause machine motion" : "Animate machine motion"}
                disabled={reduced}
                onClick={guide.toggleMotion}
              >
                {guide.motion && !reduced ? <Pause size={14} /> : <Play size={14} />}
                <span>{reduced ? "Reduced motion" : guide.motion ? "Pause motion" : "Animate"}</span>
              </button>
            </div>
          </div>
          {guide.step === 5 && <Experiment placement={placement} onChange={experiment} />}
          <div className="ac-stage-footer">
            <div className="ac-change">
              <span className="ac-status-dot" />
              {placement === "inside" ? "Room heat returns, plus the electricity added" : current.change}
            </div>
            <div className="ac-step-actions">
              <button
                className="ac-prev"
                aria-label="Previous step"
                disabled={guide.step === 0}
                onClick={() => jump(guide.step - 1)}
              >
                <ArrowLeft size={17} />
              </button>
              <button
                className="ac-next"
                onClick={() => jump(guide.step === story.length - 1 ? 0 : guide.step + 1)}
              >
                {current.next}
                <ArrowRight size={16} />
              </button>
            </div>
          </div>
        </div>
      </section>
      <div className="ac-figure-note">
        <span>Generic split-system cutaway · panels removed to reveal the mechanism</span>
        <span>Flow is illustrative. All four processes run together.</span>
      </div>
      {guide.step !== 5 && (
        <section className="ac-invitation">
          <div>
            <span className="ac-section-label">Try a thought experiment</span>
            <h2>Could it cool a room with both units inside?</h2>
          </div>
          <button
            onClick={() => {
              jump(5);
              document
                .querySelector(".ac-lesson")
                ?.scrollIntoView({ behavior: reduced ? "instant" : "smooth", block: "start" });
            }}
          >
            Try it yourself
            <ArrowRight size={16} />
          </button>
        </section>
      )}
      <div className="ac-afterword">
        <section>
          <span className="ac-section-label">The idea to take with you</span>
          <h2>
            It carries heat away.
            <br />
            It doesn’t manufacture cold.
          </h2>
          <p>
            The refrigerant stays inside the pipes. Room air and outdoor air stay separate. The compressor
            makes it possible to move heat from the cooler room to the warmer outdoors.
          </p>
          <details className="ac-details">
            <summary>How the parts and evidence fit together</summary>
            <p>{chapter.explanation}</p>
            <p>
              <strong>Why:</strong> {chapter.cause}
            </p>
            <dl>
              <dt>Comes in</dt>
              <dd>{chapter.input_state}</dd>
              <dt>Leaves</dt>
              <dd>{chapter.output_state}</dd>
            </dl>
            <h3>Sources</h3>
            <ol>
              {lesson.spec.sources.map((source) => (
                <li key={source.url}>
                  <a href={source.url} target="_blank" rel="noreferrer">
                    {source.title}
                  </a>
                  <p>{source.supports}</p>
                </li>
              ))}
            </ol>
            <h3>What is simplified</h3>
            <ul>
              {lesson.spec.assumptions.map((a) => (
                <li key={a}>{a}</li>
              ))}
            </ul>
            <p>
              This is an authored explanation with computer narration. It has not been independently
              certified. Use your manufacturer’s manual for a real appliance.
            </p>
          </details>
          <details className="ac-details">
            <summary>{guide.listening && <Volume2 size={16} />}Read the narration for this step</summary>
            <p>{chapter.narration}</p>
          </details>
          <details className="ac-details">
            <summary>Check your understanding</summary>
            <AcLearningCheck onShow={jump} />
          </details>
          <FeedbackPanel lesson={lesson} online={online} stage={guide.step} />
        </section>
        <ChatPanel lesson={lesson} member={member} online={online} onShow={show} />
      </div>
      <audio
        ref={audio}
        src={assets.videoUrl}
        preload="none"
        onLoadedMetadata={(e) => {
          e.currentTarget.currentTime = guide.initialTime();
        }}
        onTimeUpdate={(e) => {
          // A canceled media load can emit a stale zero-time event after a manual step.
          // Only actively playing, decoded media owns the guide clock.
          const nextTime = playingMediaTime(e.currentTarget);
          if (nextTime !== null) guide.time(nextTime);
        }}
        onPause={(e) => {
          if (e.currentTarget.paused) guide.stopped();
        }}
        onEnded={(e) => {
          guide.time(e.currentTarget.currentTime);
          guide.stopped();
        }}
        onError={() =>
          assets.setSaveError("Narration could not load. The interactive explanation still works.")
        }
      />
    </article>
  );
}
