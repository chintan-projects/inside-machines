/** Shared local playback/assessment controls. No concept rules or provider code. */
import type { Action, Controls, FrameState, Lesson, Question, StudioAPI } from './contracts.ts';

const NS = 'http://www.w3.org/2000/svg';
const element = <K extends keyof HTMLElementTagNameMap>(tag: K, text = ''): HTMLElementTagNameMap[K] => {
  const e = document.createElement(tag); e.textContent = text; return e;
};
const button = (text: string, action: () => void): HTMLButtonElement => {
  const b = element('button', text); b.type = 'button'; b.addEventListener('click', action); return b;
};

/** Mount a trusted lesson adapter into an empty shell; rendering is always derived. */
export function mountLesson<T extends FrameState>(root: HTMLElement, lesson: Lesson<T>): StudioAPI {
  let time = 0, controls: Controls = { ...lesson.defaultControls }, playing = false;
  let stopAt = lesson.duration, last = 0, raf = 0, hasStarted = false;
  let activeAction: Action = { id: 'tour', label: '', start: 0, end: lesson.duration, controls: lesson.defaultControls };
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const renderMode = new URLSearchParams(location.search).has('render');
  const header = element('header');
  header.append(element('p', 'Inside / a small curiosity'), element('h1', lesson.title), element('p', lesson.summary));
  const main = element('main');
  const actions = element('div'); actions.className = 'actions'; actions.setAttribute('role', 'group');
  actions.setAttribute('aria-label', 'Explore the explanation');
  const hint = element('p'); hint.className = 'hint'; hint.setAttribute('aria-live', 'polite');
  hint.tabIndex = -1;
  const revealScene = (): void => {
    hint.focus({ preventScroll: true });
    hint.scrollIntoView({ block: 'start', behavior: reduced.matches ? 'auto' : 'smooth' });
  };
  const stage = element('div'); stage.className = 'stage';
  const svg = document.createElementNS(NS, 'svg'); svg.classList.add('iso');
  svg.setAttribute('data-theme', 'light'); svg.setAttribute('viewBox', '0 0 720 620');
  svg.setAttribute('role', 'img'); stage.append(svg);
  const labels = element('div'); labels.className = 'labels'; stage.append(labels);
  const caption = element('p'); caption.className = 'caption';
  const controlArea = element('div'); controlArea.className = 'controls';
  const advanced = element('details'); advanced.className = 'advanced';
  advanced.append(element('summary', 'One more thing: data'));
  const controlButtons: { key: string; value: string; button: HTMLButtonElement }[] = [];
  const pause = button('Pause', () => playing ? api.pause() : api.play());
  pause.id = 'pause'; pause.hidden = true;
  const scrub = element('input'); scrub.type = 'range'; scrub.min = '0'; scrub.max = String(lesson.duration);
  scrub.step = '0.1'; scrub.value = '0'; scrub.setAttribute('aria-label', 'Explore the explanation timeline');
  const timeline = element('div'); timeline.className = 'timeline';
  timeline.append(button(`Play the ${lesson.duration}-second story`, () => {
    run({ id: 'tour', label: '', start: 0, end: lesson.duration, controls: lesson.defaultControls }); revealScene();
  }), pause, button('Reset', () => api.reset()), scrub);
  const questionResets: (() => void)[] = [];
  let lastDescription = '', lastView = '', labelsKey = '', lastContent = '';
  const stop = (): void => { playing = false; cancelAnimationFrame(raf); };
  const pose = (): T => lesson.stateAt(time, controls);
  const draw = (): void => {
    const state = pose(), scene = lesson.render(state);
    const vp = scene.viewport ?? { x: 0, y: 0, width: 720, height: 620 };
    svg.setAttribute('viewBox', `${vp.x} ${vp.y} ${vp.width} ${vp.height}`);
    stage.style.aspectRatio = `${vp.width}/${vp.height}`;
    stage.style.width = `min(100%,calc(72vh * ${vp.width} / ${vp.height}))`;
    const content = scene.contentKey ?? scene.svg;
    if (content !== lastContent) { svg.innerHTML = scene.svg; lastContent = content; }
    scene.attributes?.forEach(update => svg.querySelectorAll(update.selector).forEach(node => {
      node.setAttribute(update.name, update.value);
    }));
    svg.setAttribute('aria-label', scene.alt);
    if (state.description !== lastDescription) { hint.textContent = state.description; lastDescription = state.description; }
    const key = JSON.stringify([scene.labels, vp]);
    if (key !== labelsKey) {
      labels.replaceChildren(...scene.labels.map(label => {
        const tag = element('span', label.text); tag.className = 'tag';
        tag.style.left = `${(label.x - vp.x) / vp.width * 100}%`;
        tag.style.top = `${(label.y - vp.y) / vp.height * 100}%`; return tag;
      })); labelsKey = key;
    }
    caption.textContent = scene.caption; scrub.value = String(state.time);
    const visible = lesson.controlsVisible(state);
    controlArea.hidden = !visible; advanced.hidden = !visible;
    const values = lesson.controlValues(state);
    controlButtons.forEach(item => item.button.setAttribute('aria-pressed', String(values[item.key] === item.value)));
    pause.hidden = !hasStarted;
    pause.textContent = playing ? 'Pause' : time >= stopAt ? 'Replay' : reduced.matches ? 'Finish this step' : 'Resume';
    take.hidden = !lesson.takeawayVisible(state);
    if (state.beatId !== lastView) { stage.dataset.beat = state.beatId; lastView = state.beatId; }
  };
  const tick = (now: number): void => {
    if (!playing) return;
    time = Math.min(stopAt, time + Math.min(0.1, (now - last) / 1000)); last = now;
    if (time >= stopAt) stop(); draw(); if (playing) raf = requestAnimationFrame(tick);
  };
  const run = (action: Action): void => {
    activeAction = action;
    stop(); controls = { ...controls, ...action.controls }; time = action.start; stopAt = action.end; hasStarted = true;
    if (renderMode || reduced.matches) time = action.still ?? stopAt;
    else { playing = true; last = performance.now(); raf = requestAnimationFrame(tick); }
    draw();
  };
  const api: StudioAPI = {
    seek(t: number): void { stop(); time = Number.isFinite(t) ? Math.max(0, Math.min(lesson.duration, t)) : 0;
      stopAt = lesson.duration; hasStarted = time > 0; draw(); },
    play(): void {
      if (time >= stopAt) { run(activeAction); return; }
      hasStarted = true;
      if (renderMode || reduced.matches) time = stopAt;
      else if (!playing) { playing = true; last = performance.now(); raf = requestAnimationFrame(tick); }
      draw();
    },
    pause(): void { stop(); draw(); },
    reset(): void { stop(); time = 0; controls = { ...lesson.defaultControls }; hasStarted = false; stopAt = lesson.duration;
      advanced.open = false; questionResets.forEach(reset => reset()); draw(); },
    setControl(key: string, value: string): void {
      const definition = lesson.controls.find(c => c.key === key);
      if (!definition?.options.some(o => o.value === value)) throw new Error('Unsupported lesson control');
      run(lesson.controlRestart({ ...controls, ...lesson.controlValues(pose()), [key]: value }));
    },
    getState(): ReturnType<StudioAPI['getState']> { return { ...pose(), playing, controls: { ...controls } }; },
  };
  lesson.actions.forEach((action, i) => {
    const b = button(action.label, () => run(action)); b.id = action.id; if (i === 0) b.className = 'primary'; actions.append(b);
  });
  lesson.controls.forEach(control => {
    const group = element('fieldset'); group.append(element('legend', control.label));
    control.options.forEach(option => {
      const b = button(option.label, () => api.setControl(control.key, option.value));
      b.dataset.control = control.key; b.dataset.value = option.value;
      controlButtons.push({ key: control.key, value: option.value, button: b }); group.append(b);
    }); (control.advanced ? advanced : controlArea).append(group);
  });
  const assessment = (q: Question, title: string): HTMLElement => {
    const section = element('section'); section.className = 'question';
    const choices = element('div'); choices.className = 'choices';
    const answer = element('p'); answer.className = 'answer'; answer.hidden = true; answer.setAttribute('aria-live', 'polite');
    let selected = '';
    const choicesButtons = q.choices.map(choice => {
      const b = button(choice, () => { selected = choice; choicesButtons.forEach(x => x.setAttribute('aria-pressed', String(x === b))); });
      choices.append(b); return b;
    });
    const reveal = button('Show me', () => {
      answer.textContent = q.answer; answer.hidden = false;
      reveal.textContent = selected ? 'See it again' : 'Replay the explanation';
      if (q.revealAction) {
        run(q.revealAction); revealScene();
      }
    });
    choices.append(reveal); section.append(element('h2', title), element('p', q.prompt), choices, answer);
    questionResets.push(() => { selected = ''; answer.hidden = true; answer.textContent = ''; reveal.textContent = 'Show me';
      choicesButtons.forEach(x => x.setAttribute('aria-pressed', 'false')); });
    return section;
  };
  const footer = element('footer'); const sources = element('details');
  sources.append(element('summary', 'Sources, scope and this model’s limits'), element('p', lesson.scope));
  lesson.sources.forEach(source => {
    const p = element('p'); const a = element('a', source.title); a.href = source.url; a.target = '_blank'; a.rel = 'noreferrer';
    p.append(a, document.createTextNode(` — ${source.locator}`)); sources.append(p);
  }); footer.append(sources);
  const take = element('p', lesson.takeaway); take.className = 'takeaway';
  main.append(actions, hint, stage, caption, controlArea, advanced, timeline,
    assessment(lesson.prediction, 'A small prediction'), take, assessment(lesson.transfer, 'Try the idea somewhere new'));
  root.append(header, main, footer);
  scrub.addEventListener('input', () => api.seek(Number(scrub.value)));
  document.addEventListener('visibilitychange', () => { if (document.hidden) api.pause(); });
  reduced.addEventListener('change', () => { if (reduced.matches) api.pause(); });
  window.lessonStudio = api; window.seek = api.seek; draw(); return api;
}
