import { useState } from 'react';
import type { ReactElement } from 'react';
import { spinContact } from './washer-physics.mjs';

export function WasherExperiment(): ReactElement {
  const [rpm, setRpm] = useState(45);
  const model = spinContact(rpm);
  return <section className="principle-lab" aria-label="Drum speed experiment"><p className="eyebrow">Change one thing</p><h2>When does tumbling stop?</h2><p>Test whether a small piece of fabric could remain against the wall at the top of an idealized drum.</p>
    <div className="experiment-visual"><svg viewBox="0 0 250 250" role="img" aria-label={model.contact ? 'Fabric can remain against the wall at the top.' : 'Fabric cannot remain against the wall at the top; it separates and falls.'}>
      <circle cx="125" cy="130" r="91" fill="#d6e3e9" stroke="#718e9d" strokeWidth="3" /><circle cx="125" cy="130" r="83" fill="#f4f8f9" stroke="#a9c0ca" strokeWidth="2" />
      <line x1="125" y1="130" x2="208" y2="130" stroke="#829aa6" strokeDasharray="4 4" /><circle cx="125" cy="130" r="3" fill="#526d7b" />
      <text x="140" y="149" fontSize="11" fill="#52616d">r = 0.25 m</text>
      {!model.contact && <><rect x="112" y="48" width="26" height="18" rx="3" fill="none" stroke="#b59368" strokeDasharray="4 3" /><path d="M125 74V148m-7-8 7 8 7-8" stroke="#9a713c" strokeWidth="2" fill="none" /></>}
      <rect x={model.contact ? 112 : 108} y={model.contact ? 48 : 174} width={model.contact ? 26 : 34} height="18" rx="4" fill="#d6ad78" stroke="#926e3c" strokeWidth="2" />
      {model.contact && <path d="M125 74V111m-7-8 7 8 7-8" stroke="#006d7c" strokeWidth="3" fill="none" />}
      <text x="125" y="242" textAnchor="middle" fontSize="11" fill="#52616d">Illustrative cross-section</text>
    </svg><div aria-live="polite"><strong>{model.contact ? 'Can stay against the wall' : 'Separates from the wall'}</strong><p>{model.contact ? 'Gravity and an inward push from the wall can together provide the required circular acceleration.' : 'At this speed, gravity pulls inward more strongly than circular contact would require. The wall cannot pull fabric outward to compensate, so contact is lost.'}</p></div></div>
    <label>Drum speed <output>{rpm} rpm</output><input aria-label="Experiment drum speed in revolutions per minute" type="range" min="0" max="120" step="1" value={rpm} onChange={e => setRpm(Number(e.target.value))} /></label>
    <div className="experiment-presets"><button onClick={() => setRpm(45)}>Slower: 45 rpm</button><button onClick={() => setRpm(90)}>Faster: 90 rpm</button><button onClick={() => setRpm(45)}>Reset</button></div>
    <details><summary>Why this changes near {Math.round(model.criticalRpm)} rpm</summary><p>At the top, the required inward acceleration is ω²r. Gravity supplies {model.gravity} m/s² inward. At {rpm} rpm, ω²r is {model.acceleration.toFixed(2)} m/s². Contact is possible when the wall can supply any remaining inward push.</p><p>The radius is an illustrative 0.25 m. This point-mass model omits fabric shape, friction and water; it is not a measured washer setting. Real final spins run much faster.</p><a href="https://openstax.org/books/university-physics-volume-1/pages/6-3-centripetal-force" target="_blank" rel="noreferrer">Physics reference: OpenStax, centripetal force</a></details>
  </section>;
}
