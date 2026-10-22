import { useEffect, useRef, useState } from 'react';
import type { RefObject } from 'react';
import type { LegacyLesson as Lesson, Member } from '../contracts';
import { useGuide } from '../ac/useGuide';
import { teachingAt } from './state';

export function usePlayer(lesson:Lesson, member:Member, media:RefObject<HTMLAudioElement|null>, reduced:boolean):ReturnType<typeof useGuide> & {beat:ReturnType<typeof teachingAt>[0];progress:number;moving:boolean;change:()=>void;scrub:(value:number)=>void} {
  const guide=useGuide(lesson,member,media), [moving,setMoving]=useState(false);
  const start=useRef(0), startTime=useRef(0), beatRef=useRef(guide.step);
  const [beat,progress]=teachingAt(lesson.spec,guide.seconds);
  const clock=useRef(guide.time);
  useEffect(()=>{clock.current=guide.time;});
  useEffect(()=>{
    if(!moving) return;
    let frame=0;
    function tick(now:number):void {
      const p=Math.min(1,(now-start.current)/4200), stage=lesson.spec.stages[beatRef.current];
      clock.current(startTime.current+stage.duration*(.12+.58*p));
      if(p<1) frame=requestAnimationFrame(tick);else setMoving(false);
    }
    frame=requestAnimationFrame(tick);
    return ()=>cancelAnimationFrame(frame);
  },[moving,lesson.spec]);
  function pause():void { setMoving(false);guide.pause(); }
  function jump(index:number):void { pause();guide.jump(index); }
  function change():void {
    pause();
    beatRef.current=beat.stage;
    startTime.current=lesson.spec.stages.slice(0,beat.stage).reduce((n,s)=>n+s.duration,0);
    if(reduced) guide.time(startTime.current+lesson.spec.stages[beat.stage].duration*.72);
    else {start.current=performance.now();setMoving(true);}
  }
  function scrub(value:number):void { pause();guide.time(lesson.spec.stages.slice(0,beat.stage).reduce((n,s)=>n+s.duration,0)+lesson.spec.stages[beat.stage].duration*(.12+.58*value)); }
  async function listen():Promise<void> {
    setMoving(false);
    await guide.listen();
  }
  return {...guide,jump,pause,listen,beat,progress,moving,change,scrub};
}
