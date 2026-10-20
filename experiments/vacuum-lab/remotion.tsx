import React from 'react';
import {AbsoluteFill, Composition, registerRoot, useCurrentFrame} from 'remotion';
import {airInk, dirtInk, duration, ink, paper, pointAt, stateAt, story} from './model';
import type {Point} from './model';

interface Props extends Record<string,unknown> {readonly blocked:boolean;}
const route:readonly Point[]=[[68,553],[145,548],[160,431],[210,329],[280,329],[353,380],
  [439,380],[500,390],[550,400],[648,400],[648,280],[891,280]];
const dirtRoute:readonly Point[]=[...route.slice(0,7),[477,450]];
const lineOf=(points:readonly Point[]):string=>points.map((p,i)=>`${i?'L':'M'}${p[0]},${p[1]}`).join(' ');

function Label({text,x,y,ax,ay}:{readonly text:string;readonly x:number;readonly y:number;readonly ax:number;readonly ay:number}):React.JSX.Element {
  return <g><path d={`M${ax},${ay} L${x},${y+(y<ay?14:-20)}`} fill="none" stroke="#8d9ead" strokeWidth="1.6"/>
    <circle cx={ax} cy={ay} r="3" fill={ink}/><text x={x} y={y} textAnchor="middle" fontSize="32" fontWeight="500"
      fill={ink} stroke={paper} strokeWidth="7" paintOrder="stroke">{text}</text></g>;
}

function VacuumFilm({blocked}:Props):React.JSX.Element {
  const t=useCurrentFrame()/story.fps;
  const state=stateAt(t,blocked);
  const titles=['The motor powers the air mover','The room supplies the incoming air',
    'The bag separates dirt from the air','Three jobs. One connected machine.'];
  const emphasis=state.beat;
  return <AbsoluteFill style={{background:paper,fontFamily:'Arial,sans-serif'}}>
    <svg viewBox="0 0 960 720" width="960" height="720" role="img" aria-label="Illustrated bagged vacuum cleaner cutaway">
      <defs>
        <linearGradient id="shell" x1="0" y1="0" x2="1" y2="1"><stop stopColor="#f4f7fb"/><stop offset="1" stopColor="#c7d5e2"/></linearGradient>
        <linearGradient id="metal" x1="0" y1="0" x2="0" y2="1"><stop stopColor="#f7fbff"/><stop offset=".45" stopColor="#94adc3"/><stop offset="1" stopColor="#e0e9f2"/></linearGradient>
        <linearGradient id="bag" x1="0" y1="0" x2="1" y2="0"><stop stopColor="#f1eadc"/><stop offset="1" stopColor="#d4c7b1"/></linearGradient>
        <pattern id="mesh" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M0 0 L10 10 M10 0 L0 10" stroke="#b8a78b" strokeWidth=".7" opacity=".55"/></pattern>
        <filter id="shadow"><feGaussianBlur stdDeviation="7"/></filter>
      </defs>
      <text x="480" y="76" textAnchor="middle" fontSize="32" fill="#526372">{blocked?'What if we seal the inlet?':titles[emphasis]}</text>
      <ellipse cx="581" cy="563" rx="267" ry="13" fill="#243f5b" opacity=".1" filter="url(#shadow)"/>
      <path d="M351 492 V318 Q351 252 417 252 H781 Q856 252 856 323 V495 Q856 530 819 530 H395 Q351 530 351 492 Z"
        fill="url(#shell)" stroke="#849aaf" strokeWidth="2"/>
      <path d="M373 489 V326 Q373 276 424 276 H775 Q830 276 830 327 V490 Z" fill="#f9fbfe" stroke="#b3c2d0" strokeWidth="2"/>
      <path d="M555 251 V227 Q555 216 570 216 H650 Q667 216 667 229 V251" fill="none" stroke="#7890a5" strokeWidth="14"/>
      <path d="M555 247 V229 Q555 220 570 220 H650 Q663 220 663 231 V247" fill="none" stroke="#e5edf5" strokeWidth="6"/>
      {[414,799].map(x=><g key={x}><circle cx={x} cy="538" r="23" fill="#4a6176"/><circle cx={x} cy="538" r="14" fill="url(#metal)"/><circle cx={x} cy="538" r="4" fill="#4a6176"/></g>)}
      <path d="M147 537 L162 430 Q170 386 209 329 Q225 307 255 318 L353 380 H415" fill="none" stroke="#69839b" strokeWidth="27" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M147 537 L162 430 Q170 386 209 329 Q225 307 255 318 L353 380 H415" fill="none" stroke="#cddce9" strokeWidth="19" strokeLinecap="round" strokeLinejoin="round"/>
      {Array.from({length:11},(_,i)=>{const p=pointAt(route.slice(1,6),(i+1)/12);return <path key={i} d={`M${p[0]-5} ${p[1]-10} l10 20`} stroke="#8199ae" strokeWidth="2"/>;})}
      <path d="M112 535 H173 L199 560 H87 Z" fill="url(#metal)" stroke="#637e95" strokeWidth="2"/>
      <path d="M88 561 H199" stroke="#334f65" strokeWidth="5"/>
      <path d="M74 568 H310" stroke="#d3dce5" strokeWidth="2"/>
      <g opacity={emphasis===0?.8:1}>
        <path d="M414 322 Q471 304 536 327 L544 478 Q482 500 418 478 Z" fill="url(#bag)" stroke="#9c8c73" strokeWidth="2"/>
        <path d="M414 322 Q471 304 536 327 L544 478 Q482 500 418 478 Z" fill="url(#mesh)"/>
        <path d="M410 320 Q475 301 541 325" fill="none" stroke="#b1a087" strokeWidth="7"/>
        <path d="M405 366 H429 V397 H405 Z" fill="#e0d5bf" stroke="#9c8c73" strokeWidth="2"/>
        {Array.from({length:15},(_,i)=><rect key={i} x={438+i%5*15} y={470-Math.floor(i/5)*12} width="7" height="7" rx="1.5" fill={dirtInk}/>)}
      </g>
      <g>
        <path d="M636 348 H673 V452 H636 Z" fill="#e2ebf3" stroke="#7e96aa" strokeWidth="2"/>
        <ellipse cx="648" cy="400" rx="29" ry="66" fill="#dce7f0" stroke="#8ba1b4" strokeWidth="2"/>
        <path d="M649 400 H757" stroke="#506d84" strokeWidth="8"/>
        <rect x="714" y="368" width="89" height="64" rx="10" fill="url(#metal)" stroke="#6a849b" strokeWidth="2"/>
        {Array.from({length:6},(_,i)=><path key={i} d={`M${727+i*12} 374 v52`} stroke="#8199ad" strokeWidth="2"/>)}
        {Array.from({length:7},(_,i)=>{const a=(state.angle+i*360/7)*Math.PI/180;
          const pts:Point[]=[[648+6*Math.cos(a),400+11*Math.sin(a)], [648+25*Math.cos(a+.16),400+58*Math.sin(a+.16)],
            [648+25*Math.cos(a+.55),400+58*Math.sin(a+.55)]];
          return <path key={i} d={`${lineOf(pts)} Z`} fill="#5d7e9b" stroke="#35566f" strokeWidth="1"/>;})}
        <ellipse cx="648" cy="400" rx="5" ry="9" fill="#334f65"/>
      </g>
      <path d={lineOf(route)} fill="none" stroke={airInk} strokeWidth="3" opacity=".22"/>
      {state.air.map((v,i)=>{const p=pointAt(route,v);return <circle key={i} cx={p[0]} cy={p[1]} r="5.5" fill={airInk}/>;})}
      {state.dirt.map((v,i)=>{const p=pointAt(dirtRoute,v);return <rect key={i} x={p[0]-4} y={p[1]+7} width="8" height="8" rx="1.5" fill={dirtInk}/>;})}
      {[0,1,2].map(i=><path key={i} d={`M${840+i*7} 265 v31`} stroke="#728da4" strokeWidth="3"/>)}
      {blocked&&<path d="M112 536 l72 44 M184 536 l-72 44" stroke="#a43e32" strokeWidth="9" strokeLinecap="round"/>}
      <Label text="Nozzle" x={153} y={632} ax={150} ay={550}/>
      <Label text="Porous bag" x={443} y={208} ax={474} ay={319}/>
      <Label text="Fan" x={639} y={160} ax={648} ay={345}/>
      <Label text="Motor" x={786} y={502} ax={758} ay={432}/>
      <Label text="Air out" x={848} y={209} ax={851} ay={278}/>
      <text x="480" y="688" textAnchor="middle" fontSize="25" fill="#667583">Illustrative cutaway · motion slowed · bagged cleaner</text>
    </svg>
  </AbsoluteFill>;
}

function Root():React.JSX.Element {return <>
  <Composition id="Vacuum" component={VacuumFilm} width={story.width} height={story.height} fps={story.fps}
    durationInFrames={duration*story.fps} defaultProps={{blocked:false}}/>
  <Composition id="Blocked" component={VacuumFilm} width={story.width} height={story.height} fps={story.fps}
    durationInFrames={story.experiment.duration*story.fps} defaultProps={{blocked:true}}/>
</>;}
registerRoot(Root);
