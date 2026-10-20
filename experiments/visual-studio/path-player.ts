/** Shared question/depth navigation. Topic rules, artwork and providers stay outside. */
import type { StudioAPI } from './contracts.ts';
import { isDepthRequest, parsePath, resolveQuestion, type LearningPath } from './path-contract.ts';

export interface LearningPathAPI {
  select(id: string): void;
  back(): void;
  getState(): { readonly nodeId: string; readonly history: readonly string[]; readonly visited: readonly string[] };
}
declare global { interface Window { learningPath: LearningPathAPI } }
const el = <K extends keyof HTMLElementTagNameMap>(tag: K, text = ''): HTMLElementTagNameMap[K] => {
  const e = document.createElement(tag); e.textContent = text; return e;
};
const btn = (text: string, run: () => void): HTMLButtonElement => {
  const b = el('button', text); b.type = 'button'; b.addEventListener('click', run); return b;
};

/** Lazy mount trusted lessons once, preserving exact paused scenes and ephemeral answers. */
export function mountPath(root: HTMLElement, value: unknown,
  lessons: Readonly<Record<string, (host: HTMLElement) => StudioAPI>>): LearningPathAPI {
  const path: LearningPath = parsePath(value, Object.keys(lessons));
  const header = el('header'); header.className = 'path-heading';
  const brand = el('div'); brand.className = 'brand-bar';
  const wordmark = el('span', 'Inside'); wordmark.className = 'wordmark';
  brand.append(wordmark, el('span', 'Visual explanations'));
  const heading = el('h1', path.title); heading.tabIndex = -1;
  header.append(brand, heading);
  const layout = el('div'); layout.className = 'path-layout';
  const sidebar = el('aside'); sidebar.className = 'path-sidebar';
  const content = el('div'); content.className = 'path-content';
  const nav = el('nav'); nav.className = 'path-nav'; nav.setAttribute('aria-label', 'Explanation depth');
  const navTitle = el('p', 'In this explanation'); navTitle.className = 'nav-title';
  const mobile = el('div'); mobile.className = 'path-mobile';
  const chapter = el('select'); chapter.id = 'path-choice';
  const chapterLabel = el('label', 'In this explanation'); chapterLabel.htmlFor = chapter.id;
  mobile.append(chapterLabel, chapter);
  const context = el('div'); context.className = 'path-context';
  const back = btn('', () => api.back()); back.hidden = true;
  back.className = 'path-back';
  const depth = btn('Dive deeper', () => findQuestion('dive deeper'));
  depth.className = 'depth-button';
  const contextActions = el('div'); contextActions.className = 'path-context-actions'; contextActions.append(back, depth);
  const prerequisite = el('p'); context.append(contextActions, prerequisite);
  const notice = el('p'); notice.className = 'path-notice'; notice.setAttribute('role', 'status');
  const viewport = el('div'); viewport.className = 'path-lesson';
  const deeper = el('section'); deeper.className = 'deeper';
  const next = el('div'); next.className = 'next-questions';
  const form = el('form'); form.className = 'path-search';
  const input = el('input'); input.id = 'find-question'; input.maxLength = 200;
  input.placeholder = 'Try “dive deeper” or “matrix”';
  const label = el('label', 'Find a question in this explanation'); label.htmlFor = input.id;
  const submit = el('button', 'Find explanation'); submit.type = 'submit'; form.append(label, input, submit);
  const help = el('p', 'Search the saved explanations. Type a question, then press Enter or Find explanation.');
  help.id = 'question-help'; help.className = 'path-help'; input.setAttribute('aria-describedby', help.id);
  const deeperHeading = el('h2', 'Follow your curiosity'); deeperHeading.tabIndex = -1;
  deeper.append(deeperHeading, next, form, help, notice);
  sidebar.append(navTitle, nav, mobile, context); content.append(viewport, deeper);
  layout.append(sidebar, content); root.append(header, layout);
  const mounted = new Map<string, { host: HTMLElement; api: StudioAPI }>();
  const buttons = new Map<string, HTMLButtonElement>();
  const history: string[] = []; let current = '';
  const show = (id: string, push: boolean, focus = true): void => {
    const node = path.nodes.find(n => n.id === id);
    if (!node) throw new Error('Unknown learning-path node');
    if (id === current) return;
    let target = mounted.get(id);
    if (!target) {
      const host = el('section'); host.hidden = true; host.dataset.node = id; viewport.append(host);
      try { target = { host, api: lessons[node.lesson_id](host) }; mounted.set(id, target); }
      catch {
        host.remove(); const previous = mounted.get(current);
        if (!previous) throw new Error('The entry explanation could not load');
        window.lessonStudio = previous.api; window.seek = previous.api.seek;
        notice.textContent = 'This explanation could not load. Your previous place is preserved.'; return;
      }
    }
    const previous = mounted.get(current); previous?.api.pause();
    if (previous) target.api.setMuted(previous.api.getState().muted);
    if (push && current) history.push(current);
    if (previous) previous.host.hidden = true;
    current = id; target.host.hidden = false;
    heading.textContent = node.question;
    // No hidden lesson or asynchronous media event can replace the active inspection API.
    window.lessonStudio = target.api; window.seek = target.api.seek;
    buttons.forEach((button, key) => button.setAttribute('aria-current', key === id ? 'page' : 'false'));
    chapter.value = id;
    const parent = path.nodes.find(n => n.id === history[history.length - 1]);
    back.hidden = !parent; back.textContent = parent ? `Back to ${parent.label.toLowerCase()}` : '';
    depth.textContent = node.next.length ? 'Dive deeper' : 'Questions';
    depth.setAttribute('aria-label', node.next.length ? 'Dive deeper' : 'Browse available questions');
    const missing = node.prerequisites.filter(id => !mounted.has(id));
    prerequisite.textContent = missing.length ? `Builds on: ${missing.map(id => path.nodes.find(n => n.id === id)!.label.toLowerCase()).join(', ')}. You can return at any time.` : '';
    next.replaceChildren(...node.next.map(id => {
      const child = path.nodes.find(n => n.id === id)!;
      return btn(child.question, () => api.select(id));
    }));
    if (!node.next.length) next.append(...path.nodes.filter(n => n.id !== current).map(n =>
      btn(n.role === 'core' ? 'Return to the complete story' : n.question, () => api.select(n.id))));
    notice.textContent = ''; input.value = '';
    historyReplace(id);
    if (focus) {
      heading.focus({ preventScroll: true });
      heading.scrollIntoView({ block: 'start', behavior: 'auto' });
    }
  };
  const historyReplace = (id: string): void => { window.history.replaceState(null, '', `#${id}`); };
  const api: LearningPathAPI = {
    select(id) { show(id, true); },
    back() { const id = history.pop(); if (id) show(id, false); },
    getState() { return { nodeId: current, history: [...history], visited: [...mounted.keys()] }; },
  };
  path.nodes.forEach(node => {
    const b = btn(node.label, () => api.select(node.id)); buttons.set(node.id, b); nav.append(b);
    const option = el('option', node.label); option.value = node.id; chapter.append(option);
  });
  chapter.addEventListener('change', () => api.select(chapter.value));
  const findQuestion = (question: string): void => {
    const target = resolveQuestion(path, current, question);
    if (target) {
      if (target.id === current) notice.textContent = 'You are viewing that explanation. Use its scene controls to explore.';
      else api.select(target.id);
    } else if (isDepthRequest(question)) {
      notice.textContent = 'You have reached the deepest explanation saved for this topic. The questions above open other saved explanations. A further level has not been created yet.';
      deeperHeading.focus({ preventScroll: true }); deeper.scrollIntoView({ block: 'start', behavior: 'auto' });
    } else notice.textContent = 'That question is not covered in this saved explanation yet. Choose one of the questions above.';
  };
  form.addEventListener('submit', event => {
    event.preventDefault();
    findQuestion(input.value);
  });
  const requested = location.hash.slice(1);
  show(path.nodes.some(n => n.id === requested) ? requested : path.entry, false, false);
  window.learningPath = api;
  return api;
}
