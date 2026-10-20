/** @typedef {Readonly<{time:number, phase:number, focus:string, flow:boolean, blocked:boolean}>} BagPose */

/** Presentation-only reveal, derived from the common storyboard pose. @param {BagPose} pose */
export function bagWindowAlpha(pose) {
  if (!Number.isFinite(pose.time) || pose.focus !== 'bag') return 0;
  return Math.max(0, Math.min(1, (pose.time - 24) / .45, (34 - pose.time) / .45));
}

/** @param {number} x @param {number} y @param {number} opacity */
function airArrow(x, y, opacity) {
  return `<path data-air="true" d="M${x-8},${y-7} l16,7 -16,7 4,-7Z" fill="#1f7a78" stroke="#134e4c" stroke-width="1.5" opacity="${opacity}"/>`;
}

/** @param {number} x @param {number} y @param {number} angle @param {string} kind @param {number} opacity */
function dirt(x, y, angle, kind, opacity=1) {
  return `<rect data-${kind}="true" x="${x-9}" y="${y-9}" width="18" height="18" rx="3" transform="rotate(${angle} ${x} ${y})" fill="#77502f" stroke="#3c2a1d" stroke-width="2" opacity="${opacity}"/>`;
}

/**
 * Independent physical surroundings and labeled bag mechanism, rather than a
 * crop of whole-machine coordinates. No new causal rules: flow/phase come from
 * the common pose. Fibers and particles are qualitative, enlarged symbols.
 * @param {BagPose} pose
 * @param {string} locator Trusted whole-machine SVG from the same pose.
 * @returns {string}
 */
export function bagWindow(pose, locator='') {
  const alpha = bagWindowAlpha(pose);
  if (!alpha) return '';
  if (!Number.isFinite(pose.phase)) throw new RangeError('Invalid bag presentation phase');
  const phase = ((pose.phase % 1) + 1) % 1;
  let air = '';
  let incoming = '';
  if (pose.flow) {
    for (const y of [228,283,338,393]) {
      air += `<path d="M88 ${y} C170 ${y-7} 260 ${y+7} 316 ${y} S405 ${y-5} 630 ${y}" fill="none" stroke="#1f7a78" stroke-width="2.5" opacity=".25"/>`;
      for (let i=0; i<4; i++) {
        const progress=(phase*2+i/4)%1;
        air += airArrow(88+progress*530,y,.9);
      }
    }
    for (let i=0; i<3; i++) {
      const progress=(phase*1.2+i/3)%1;
      const fade=Math.min(1,progress*10,(1-progress)*12);
      incoming += dirt(95+progress*214,245+i*55,20+i*23,'incoming',fade);
    }
  }
  // The same retained sample remains under both open and blocked conditions.
  const retained = [249,304,359].map((y,i)=>dirt(310,y,15+i*20,'retained')).join('');
  let fibers = '';
  for (let i=0;i<5;i++) {
    const x=329+i*10;
    fibers += `<path d="M${x} 208 Q${x+6} 260 ${x-2} 306 T${x+2} 415" stroke="#b79d64" stroke-width="4" fill="none"/>`;
  }
  for (let i=0;i<8;i++) {
    const y=216+i*27;
    fibers += `<path d="M324 ${y} Q348 ${y-7} 373 ${y+3}" stroke="#c5ad78" stroke-width="3" fill="none"/>`;
  }
  const cue = pose.flow
    ? 'Air passes through gaps; larger dirt is caught.'
    : 'Inlet blocked: no steady stream reaches this wall.';
  return `<g data-bag-inset="true" opacity="${alpha}">
  <rect x="22" y="23" width="676" height="600" rx="22" fill="#d8ccb2" opacity=".65"/>
  <rect x="16" y="16" width="688" height="600" rx="22" fill="#fff9eb" stroke="#2a2118" stroke-width="2.5"/>
  <text x="46" y="65" font-family="Georgia,serif" font-size="34" font-weight="700" fill="#2a2118">Air passes. Dirt gets caught.</text>
  <text x="46" y="104" font-family="Georgia,serif" font-size="27" fill="#665440">Inside the collecting bag · enlarged schematic</text>
  <rect x="48" y="155" width="620" height="284" rx="15" fill="#e5d7b5" stroke="#8a7043" stroke-width="3"/>
  <path d="M63 169 H320 V425 H63Z" fill="#f8eac7"/>
  <path d="M375 169 H653 V425 H375Z" fill="#edf3ee"/>
  <path d="M50 155 H666 V173 H50Z M50 420 H666 V439 H50Z" fill="#b85b43" stroke="#7d3829" stroke-width="1.5"/>
  <text x="80" y="205" font-family="Georgia,serif" font-size="28" fill="#443725">Air + loose dirt</text>
  <text x="419" y="205" font-family="Georgia,serif" font-size="28" fill="#134e4c">Air continues</text>
  <rect x="320" y="173" width="58" height="247" fill="#eadbb3" stroke="#8a7043" stroke-width="2.5"/>
  ${air}${fibers}${incoming}${retained}
  <path d="M349 422 V449" stroke="#443725" stroke-width="2"/>
  <circle cx="349" cy="422" r="4" fill="#443725"/>
  <text x="349" y="479" text-anchor="middle" font-family="Georgia,serif" font-size="29" font-weight="700" fill="#443725">Porous bag wall</text>
  <text x="45" y="518" font-family="Georgia,serif" font-size="28" fill="#443725">${cue}</text>
  <g transform="translate(32 515) scale(.14)" opacity=".85">${locator}</g>
  <text x="150" y="580" font-family="Georgia,serif" font-size="27" fill="#665440">Same air path</text>
  </g>`;
}
