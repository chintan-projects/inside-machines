import { mkdirSync, readFileSync, writeFileSync, copyFileSync } from 'node:fs';
import * as k from '../vendor/anatomy/kit/iso-kit.mjs';

mkdirSync('dist-lab', { recursive: true });
const P = k.fitProjection(k.boxCorners({ x: -110, y: -85, w: 240, d: 200, r: 4 }, -8, 218), 760, 560, { pad: 45, azimuth: 64, elevation: 23 });
const at = p => k.iso(p, P);
const path = points => k.pathOf(points.map(at));
const closed = points => k.pathOf(points.map(at), true);
const pieces = [];
const slab = (name, x, y, w, d, z, h, cls = '') => pieces.push(`<g data-component="${name}" class="${cls}">${k.solidSvg(k.slabOf({ x, y, w, d, r: 1.8 }, z, h, P, 5, .6), { tone: 'mid' })}</g>`);
const bolt = (x, y, z) => pieces.push(k.solidSvg(k.cylinder(x, y, 2, z, 1.4, P, 12), { tone: 'lo' }));
const line = (points, cls = '') => `<path class="hardware ${cls}" d="${path(points)}"/>`;
const circleAt = (x, y, z, r, cls) => { const p = at([x, y, z]); return `<circle cx="${p[0]}" cy="${p[1]}" r="${r}" class="${cls}"/>`; };
const frontCenter = at([0, 62, 106]);
const ex = at([1, 62, 106]), ey = at([0, 62, 105]);
const matrix = `matrix(${ex[0]-frontCenter[0]} ${ex[1]-frontCenter[1]} ${ey[0]-frontCenter[0]} ${ey[1]-frontCenter[1]} ${frontCenter[0]} ${frontCenter[1]})`;
// A recognizable cabinet, feet, seams, mounts, two rails, and service space.
for (const [x, y] of [[-82,-52],[82,-52],[-82,58],[82,58]]) {
  slab('rubber foot', x-6,y-6,12,12,-8,5,'rubber');
  slab('adjustable foot',x-4,y-4,8,8,-3,7);
}
slab('base tray',-98,-68,196,140,4,7);
slab('rear cabinet panel',-96,-67,192,5,11,181);
slab('left cabinet panel',-96,-62,5,129,11,181);
for (const x of [-85,85]) {
  slab('frame rail',x-3,-56,6,117,12,6);
  slab('front upright',x-3,59,6,6,18,159);
  slab('rear upright',x-3,-58,6,6,18,159);
  for (const y of [-54,55]) bolt(x,y,18);
}
slab('rear motor mount',-20,-55,40,27,21,6);
slab('electric motor',-16,-50,32,24,27,22,'motor-body');
for (let x=-12;x<=12;x+=6) slab('motor cooling fin',x,-50,1.4,24,28,20);
slab('pump mount',57,28,27,25,11,4);
slab('drain pump',61,31,19,18,15,22,'pump-body');
for (const x of [61,77]) for (const y of [31,47]) bolt(x,y,37);
slab('detergent drawer housing',-76,-10,50,69,172,13);
slab('detergent drawer lip',-77,60,53,5,172,13);
slab('drawer handle',-65,65,29,3,177,3);
slab('inlet valve',-68,-52,22,18,170,13,'inlet-body');
for (const x of [-79,79]) {
  slab('suspension anchor',x-4,-15,8,14,171,7);
  for (const y of [-13,-5]) bolt(x,y,178);
  pieces.push(line([[x,-8,171],[x,-8,160],[x+4,-8,155],[x-4,-8,150],[x+4,-8,145],[x-4,-8,140],[x,-8,135]], 'suspension'));
}
// Outer tub barrel, drawn in depth order, with the front open for teaching.
const barrel = [];
for (let i=0;i<64;i++) {
  const a=i*Math.PI/32,b=(i+1)*Math.PI/32;
  const point=(ang,y)=>[68*Math.cos(ang),y,106+68*Math.sin(ang)];
  const pts=[point(a,-39),point(b,-39),point(b,57),point(a,57)];
  barrel.push({ depth:k.depthOf(point((a+b)/2,8),P),svg:`<path d="${closed(pts)}" fill="${['#ced5d0','#dce1db','#e6e9e2','#bec9c4'][Math.floor((Math.sin(a)+1)*1.9)]}" stroke="#a1aea6" stroke-width=".35"/>` });
}
pieces.push(`<g id="outer-tub">${barrel.sort((a,b)=>a.depth-b.depth).map(b=>b.svg).join('')}</g>`);
pieces.push(`<g transform="${matrix}">
  <circle r="69" fill="#b8c4bd" stroke="#63746a" stroke-width="1.2"/>
  <circle r="64" fill="#e4e8e0" stroke="#8a9b90" stroke-width=".6"/>
  <circle r="59" fill="#475b51"/>
  <circle r="55" fill="#d4ddd4" stroke="#798d7e" stroke-width=".7"/>
  <defs><clipPath id="drum-clip"><circle r="54"/></clipPath></defs>
  <g clip-path="url(#drum-clip)">
    <circle r="54" fill="#a1b6a8"/>
    <g id="rotor">${Array.from({length:72},(_,i)=>{
      const a=(i%24)*Math.PI/12,r=34+Math.floor(i/24)*8;
      return `<circle cx="${Math.cos(a)*r}" cy="${Math.sin(a)*r}" r="1.05" fill="#647f6d"/>`;
    }).join('')}${[0,120,240].map(a=>`<g transform="rotate(${a})"><path d="M-5 -49 L-3 -25 Q0 -21 3 -25 L5 -49 Z" fill="#ecf0e8" stroke="#78947e" stroke-width=".8"/><path d="M0 -47V-27" stroke="#9eafa0" stroke-width=".6"/></g>`).join('')}</g>
    <g id="laundry"><path d="M-29 11 l12 -8 11 5 -3 10 7 13 -14 8 -9 -7 -14 -4z" fill="#e9ad72" stroke="#bd824f" stroke-width=".8"/><path d="M5 17l11 -11 14 8 7 16 -11 13 -20 -4 -8 -10z" fill="#f5e7d4" stroke="#c9baa4" stroke-width=".8"/><path d="M-5 34l14 -8 13 15 -2 8 -26 3 -13 -8z" fill="#748e9d" stroke="#4f6c7c" stroke-width=".8"/></g>
    <path id="water" fill="#559daa" fill-opacity=".5" stroke="#347d8d" stroke-width=".7"/>
    <g id="spin-drops" stroke="#438f9e" stroke-width="1.3" stroke-linecap="round" opacity="0">${Array.from({length:12},(_,i)=>`<path transform="rotate(${i*30})" d="M0 -44v-5"/>`).join('')}</g>
  </g>
  <circle r="56" fill="none" stroke="#f2f3ec" stroke-width="2.5"/>
  <circle r="59.5" fill="none" stroke="#657b6c" stroke-width=".65"/>
  ${Array.from({length:10},(_,i)=>{const a=i*Math.PI/5;return `<circle cx="${66*Math.cos(a)}" cy="${66*Math.sin(a)}" r="1.1" fill="#65766a"/>`;}).join('')}
</g>`);
// Lines are flow paths, with explicit connection points at their terminals.
const inletRoute=[[-90,-80,183],[-57,-80,183],[-57,-43,183],[-57,-43,176],[-57,-5,176],[-57,27,170],[-42,27,152]];
const drainRoute=[[42,47,54],[70,47,47],[70,40,28],[84,40,28],[112,40,28],[112,-55,28],[112,-55,132],[112,-79,132]];
for (const [id,route] of [['inlet-flow',inletRoute],['drain-flow',drainRoute]]) {
  pieces.push(`<path class="hose" d="${path(route)}"/><path id="${id}" class="flow" d="${path(route)}"/>`);
  for (const point of [route[0],route.at(-1)]) pieces.push(circleAt(...point,3.2,'port'));
}
// Open roof exposes the inlet and drawer instead of hiding the cause of filling.
slab('top rear crossmember',-98,-68,196,15,190,5);
for (const x of [-98,90]) slab('top side rail',x,-53,8,115,190,5);
for (const x of [-94,94]) for (const y of [-60,57]) bolt(x,y,195);
slab('control fascia',-98,62,196,9,175,15);
slab('front lower plinth',-98,62,196,9,11,14);
slab('pump access cover',54,72,26,2,15,8);
for (const x of [-84,-70,-56,-42,-28,-14]) pieces.push(line([[x,72,18],[x+6,72,18]], 'vent'));
const dial = at([16,72,183]);
pieces.push(`<circle cx="${dial[0]}" cy="${dial[1]}" r="8" fill="#d6dcd4" stroke="#7b8980"/><circle cx="${dial[0]}" cy="${dial[1]}" r="5" fill="#f7f7ef" stroke="#a3aea4"/>`);
const display=at([54,73,183]);
pieces.push(`<rect x="${display[0]-18}" y="${display[1]-6}" width="37" height="13" rx="2" fill="#294a40"/><text id="machine-screen" x="${display[0]}" y="${display[1]+3}" fill="#b9d7b5" font-size="8" text-anchor="middle" font-family="monospace">FILL</text>`);
for (const [i,point] of [[1,[-57,-43,187]],[2,[49,63,142]],[3,[82,45,32]]]) {
  const p=at(point); pieces.push(`<g class="part-marker"><circle cx="${p[0]}" cy="${p[1]}" r="11"/><text x="${p[0]}" y="${p[1]+3.5}">${i}</text></g>`);
}
const svg=k.figureSvg({width:760,height:560,label:'Cutaway of a generic front-loading washing machine: inlet valve, perforated drum inside an outer tub, and a drain pump.',body:pieces.join('')});
const template=readFileSync('src/index.html','utf8');
writeFileSync('dist-lab/index.html',template.replace('<!-- MACHINE -->',svg));
copyFileSync('vendor/anatomy/kit/iso.css','dist-lab/anatomy.css');
copyFileSync('vendor/anatomy/LICENSE','dist-lab/ANATOMY-LICENSE.txt');
for(const file of ['app.mjs','model.mjs','style.css','sw.js','manifest.webmanifest','icon.svg']) copyFileSync('src/'+file,'dist-lab/'+file);
console.log(`Built dist-lab/index.html with ${pieces.length} geometry groups. Anatomy projection + solids; custom drum cutaway.`);
