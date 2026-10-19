import { sample, STAGES, DURATION } from './model.mjs';
const $ = id => document.getElementById(id);
let time = 0, playing = false, previous = 0, stageIndex = -1;
const reduced = matchMedia('(prefers-reduced-motion: reduce)');
const clock = n => `${String(Math.floor(n / 60)).padStart(2,'0')}:${String(Math.floor(n % 60)).padStart(2,'0')}`;
STAGES.forEach((s,i) => {
  const button = document.createElement('button');
  button.className = 'step';
  button.innerHTML = `<span class="step-number">${String(i+1).padStart(2,'0')}</span><span>${s.name}<small>${['Water meets detergent','Gravity does the work','Used water leaves','Fresh water, fresh start','Water out, clothes in'][i]}</small></span><b>↗</b>`;
  button.onclick = () => seek(s.start);
  $('steps').append(button);
});
function setPlaying(value) {
  playing = value;
  $('play').textContent = playing ? 'Ⅱ Pause cycle' : time === DURATION ? '↻ Replay cycle' : '▶ Play cycle';
  $('play').setAttribute('aria-label', playing ? 'Pause cycle' : 'Play cycle');
  document.body.classList.toggle('playing', playing && !reduced.matches);
}
function seek(t) { time = Number(t); render(); }
function render() {
  const s = sample(time);
  if (s.stageIndex !== stageIndex) {
    stageIndex = s.stageIndex;
    [...$('steps').children].forEach((b,i) => { b.setAttribute('aria-current',i === stageIndex ? 'step' : 'false'); b.classList.toggle('done',i < stageIndex); });
    $('stage-number').textContent = `${String(stageIndex+1).padStart(2,'0')} / ${s.stage.name.toUpperCase()}`;
    $('stage-title').textContent = s.stage.title;
    $('stage-text').textContent = s.stage.text;
    $('why').textContent = s.stage.why;
  }
  $('timeline').value = time;
  $('time').textContent = `${clock(time)} / 01:12`;
  $('water-reading').innerHTML = `${s.water.toFixed(1)} <small>L</small>`;
  $('rpm-reading').innerHTML = `${Math.abs(s.rpm).toFixed(0)} <small>rpm</small>`;
  $('valve-reading').textContent = s.inlet ? 'Open' : 'Closed';
  $('pump-reading').textContent = s.pump ? 'Running' : 'Off';
  $('door-reading').textContent = s.doorLocked ? 'Locked' : 'Released';
  $('machine-screen').textContent = s.complete ? 'DONE' : s.stage.name.toUpperCase();
  // All moving elements read the same deterministic state, including on seek.
  const angle = s.displayAngle * 180 / Math.PI;
  $('rotor').setAttribute('transform', `rotate(${angle})`);
  $('laundry').setAttribute('transform', `rotate(${s.laundryAngle})`);
  $('rotation-scale').textContent = `Drum motion ×1/${s.rotationScale}`;
  // Horizontal water surface in the drum plane, clipped by the round wall.
  const y = 56 - s.water / 12 * 49;
  $('water').setAttribute('d', `M-60 ${y} Q-30 ${y-1.4} 0 ${y} T60 ${y} V65 H-60Z`);
  $('water').setAttribute('opacity',s.water > 0.01 ? '1' : '0');
  $('spin-drops').setAttribute('opacity',Math.min(1,Math.abs(s.rpm)/1000));
  $('inlet-flow').classList.toggle('active',s.inlet);
  $('drain-flow').classList.toggle('active',s.pump);
  if (s.complete) setPlaying(false);
  window.labState = { ...s, playing };
}
$('play').onclick = () => { if(time >= DURATION) seek(0); setPlaying(!playing); };
$('reset').onclick = () => { setPlaying(false); seek(0); };
$('timeline').oninput = e => { setPlaying(false); seek(e.target.value); };
$('labels-toggle').onclick = () => { const hidden = $('machine').classList.toggle('hide-markers'); $('labels-toggle').textContent = hidden ? 'Show markers' : 'Hide markers'; $('labels-toggle').setAttribute('aria-pressed',String(!hidden)); };
document.addEventListener('keydown',e => {
  if (['INPUT','TEXTAREA','BUTTON','SUMMARY','A'].includes(document.activeElement.tagName)) return;
  if(e.code === 'Space') { e.preventDefault(); $('play').click(); }
  if(e.code === 'ArrowRight') { e.preventDefault(); setPlaying(false); seek(Math.min(72,time+2)); }
  if(e.code === 'ArrowLeft') { e.preventDefault(); setPlaying(false); seek(Math.max(0,time-2)); }
});
document.querySelectorAll('[data-part]').forEach(button => button.onclick = () => {
  const indices = { inlet:0, drum:1, pump:2 };
  document.querySelectorAll('[data-part]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
  setPlaying(false); seek(STAGES[indices[button.dataset.part]].start + 2);
  $('stage-title').scrollIntoView({ block:'center',behavior:reduced.matches?'instant':'smooth' });
});
let specific = false;
function mode(value) {
  specific = value;
  $('specific-panel').hidden = !value;
  $('general-mode').setAttribute('aria-pressed',String(!value));
  $('specific-mode').setAttribute('aria-pressed',String(value));
  $('scope-badge').textContent = value ? 'GENERIC VIEW · MODEL UNVERIFIED' : 'GENERIC · FRONT LOAD';
  $('request-status').textContent = value ? 'Add machine details below. The illustration remains generic.' : 'Local proof of concept · front-load washer available';
}
$('general-mode').onclick = () => mode(false);
$('specific-mode').onclick = () => mode(true);
$('question-form').onsubmit = e => {
  e.preventDefault();
  const q = $('question').value.toLowerCase();
  if (!/wash(?:ing|er)|laundry/.test(q) || /dish\s*wash|top[ -]?load/.test(q)) {
    $('request-status').textContent = 'This local demo supports a front-load washing machine. Other machines need a new model and drawing; live generation is not connected.';
    return;
  }
  if (/\bmy\b|\bour\b|specific/.test(q)) mode(true);
  else if (!specific) mode(false);
  setPlaying(false); seek(0);
  $('request-status').textContent = specific ? 'Is this your machine? Add its model below, or choose “Just the principles.”' : 'Ready: a generic front-load washing machine, from first principles.';
};
$('specific-form').onsubmit = e => {
  e.preventDefault();
  // Session memory only. No upload, persistence, or inferred verification.
  const model = $('machine-model').value.trim();
  const excerpt = $('manual').value.trim();
  if (!model) return;
  window.machineContext = { model, excerpt, verified:false };
  $('evidence-status').textContent = `Context noted for ${model}${excerpt ? ' with a manual excerpt' : ''}. Unverified; the model and all numbers remain generic. Details disappear on reload.`;
};
let visible = true;
new IntersectionObserver(entries => { visible = entries[0].isIntersecting; }).observe($('machine'));
document.addEventListener('visibilitychange',()=>{previous=0;});
function frame(now) {
  const dt = previous ? Math.min((now - previous)/1000,0.08) : 0;
  previous = now;
  if(playing && visible && !document.hidden) { time = Math.min(DURATION,time+dt); render(); }
  requestAnimationFrame(frame);
}
// Reduced motion starts paused, disables flow animation, and supports direct seeking.
reduced.addEventListener('change',()=>{setPlaying(false);});
render(); requestAnimationFrame(frame);
if('serviceWorker' in navigator) navigator.serviceWorker.register('/sw.js').catch(error=>console.warn('Offline cache unavailable:',error.message));
