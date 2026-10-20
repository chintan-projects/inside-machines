import {Circle, Line, Node, Rect, Txt, Scene2D, makeScene2D} from '@motion-canvas/2d';
import type {View2D} from '@motion-canvas/2d';
import {createSignal, Logger, PlaybackManager, PlaybackState, PlaybackStatus,
  SharedWebGLContext, Stage, Vector2, ValueDispatcher} from '@motion-canvas/core';
import {ReadOnlyTimeEvents} from '@motion-canvas/core/lib/scenes/timeEvents/ReadOnlyTimeEvents';
import type {FullSceneDescription, ThreadGeneratorFactory} from '@motion-canvas/core';
import {airInk, dirtInk, duration, ink, paper, pointAt, stateAt, story} from './model';
import type {Point} from './model';

declare global { interface Window { drawMotionFrame: (frame: number) => Promise<string>; motionReady: boolean; } }
const blocked = new URLSearchParams(location.search).get('blocked') === '1';
const seconds = blocked ? story.experiment.duration : duration;
const route: readonly Point[] = [[65,552], [151,548], [153,400], [196,335], [280,335],
  [358,380], [450,380], [505,391], [545,400], [650,400], [650,285], [890,285]];
const dirtyRoute: readonly Point[] = [...route.slice(0,7), [475,450]];
const centered = (point: Point): [number, number] => [point[0] - 480, point[1] - 360];

const description = makeScene2D(function* (view: View2D) {
  const clock = createSignal(0);
  const frame = () => stateAt(clock(), blocked);
  const root = new Node({});
  view.fill(paper);
  view.add(root);
  const rect = (x: number,y: number,w: number,h: number,fill: string,stroke = '#a3b3c3', radius = 16) => {
    const item = new Rect({x:x-480,y:y-360,width:w,height:h,fill,stroke,lineWidth:2,radius});
    root.add(item); return item;
  };
  const circle = (x:number,y:number,r:number,fill:string,stroke=fill) => {
    const item = new Circle({x:x-480,y:y-360,width:r*2,height:r*2,fill,stroke,lineWidth:2});
    root.add(item); return item;
  };
  const line = (points: readonly Point[], color:string,width:number) => {
    const item = new Line({points:points.map(centered),stroke:color,lineWidth:width,lineCap:'round',lineJoin:'round'});
    root.add(item); return item;
  };
  const text = (content:string,x:number,y:number,size=32,color=ink) => {
    const item = new Txt({text:content,x:x-480,y:y-360,fontFamily:'Arial',fontSize:size,fill:color,fontWeight:500});
    root.add(item); return item;
  };
  text('A small machine with three jobs',480,73,32,'#526372');
  rect(612,384,505,294,'#eef3f9','#aabac8',42);
  rect(612,227,112,18,paper,'#8d9faf',8);
  line([[370,524],[846,524]],'#b8c6d2',3);
  circle(416,544,18,ink); circle(797,544,18,ink);
  const hose: readonly Point[] = [[153,532],[153,400],[196,335],[280,335],[358,380],[410,380]];
  line(hose,'#71899d',25); line(hose,'#e8eef5',17);
  for(const [x,y] of [[175,368],[190,344],[215,335],[239,335],[265,335],[303,348],[326,362]])
    line([[x-3,y-10],[x+3,y+10]],'#9eafbd',2);
  root.add(new Line({points:[[115,535],[175,535],[193,558],[92,558]].map(p=>centered(p as [number,number])),closed:true,
    fill:'#d0dce7',stroke:'#617c92',lineWidth:2}));
  line([[73,566],[310,566]],'#c7d0d9',2);
  const bag = rect(476,402,128,186,'#e8dfce','#94856f',13);
  bag.shadowColor(()=>frame().beat===2?'#c8ba9d66':'#00000000'); bag.shadowBlur(18);
  for(let x=424;x<535;x+=13) line([[x,322],[x,484]],'#c4b69e',1.2);
  for(let y=322;y<486;y+=14) line([[536,y],[545,y+3]],'#94856f',2);
  for(let i=0;i<14;i++) circle(440+(i%5)*14,470-Math.floor(i/5)*13,3.5,dirtInk);
  const housing = new Circle({x:170,y:40,width:57,height:136,stroke:'#7f97ac',lineWidth:3,fill:'#e0e9f2'});
  root.add(housing);
  line([[650,400],[758,400]],'#536f85',7);
  rect(758,400,92,64,'#c5d5e4','#59768e',11);
  for(let x=731;x<791;x+=12) line([[x,373],[x,427]],'#8fa9bf',2);
  for(let i=0;i<6;i++) {
    root.add(new Line({points:()=>{
      const a=frame().angle*Math.PI/180+i*Math.PI/3;
      return [[650+5*Math.cos(a),400+10*Math.sin(a)],
        [650+23*Math.cos(a+.2),400+57*Math.sin(a+.2)],
        [650+23*Math.cos(a+.65),400+57*Math.sin(a+.65)]].map(p=>centered(p as [number,number]));
    },closed:true,fill:'#688ba8',stroke:'#365a75',lineWidth:1}));
  }
  circle(650,400,6,ink);
  line(route,'#b9caef',3);
  line([[844,270],[844,303]],'#6b8298',3);
  // Thin direction chevrons distinguish air flow from a pipe or an electrical wire.
  for(const [x,y] of [[353,380],[593,400],[832,285]]) line([[x-9,y-7],[x,y],[x-9,y+7]],airInk,3);
  for(let i=0;i<12;i++) {
    const mark = new Circle({width:11,height:11,fill:airInk,
      opacity:()=>frame().air.length?1:0,
      position:()=>centered(pointAt(route,frame().air[i]??0))});
    root.add(mark);
  }
  for(let i=0;i<5;i++) root.add(new Rect({width:8,height:8,radius:1,fill:dirtInk,
    opacity:()=>frame().dirt.length?1:0,
    position:()=>{const p=pointAt(dirtyRoute,frame().dirt[i]??0);return [p[0]-480,p[1]-351];}}));
  for(const [content,x,y,ax,ay] of [
    ['Nozzle',157,628,153,550],['Porous bag',464,270,480,310],['Fan',650,205,650,350],
    ['Motor',785,510,770,435],['Air out',850,207,850,280],
  ] as const) {
    line([[x,y+(y<ay?18:-18)],[ax,ay]],'#9aa9b5',1.5); text(content,x,y);
  }
  if(blocked) {
    line([[115,535],[185,580]],'#a43e32',9); line([[185,535],[115,580]],'#a43e32',9);
  }
  const title = text('',480,673,27,'#526372');
  title.text(()=>blocked?'The fan turns. Fresh air cannot enter.':[
    'Electricity → motor → fan → moving air',
    'Room air enters. Loose dirt travels with it.',
    'Air crosses the porous wall. Dirt stays inside.',
    'These jobs happen together, along one path.',
  ][frame().beat]);
  for(let i=0;i<=seconds*story.fps;i++) {clock(i/story.fps);yield;}
});

async function initialize(): Promise<void> {
  const playback = new PlaybackManager();
  playback.fps=story.fps; playback.state=PlaybackState.Rendering;
  const logger = new Logger();
  // Scene2D initializes its Variables itself. FullSceneDescription also includes
  // hot-reload fields not used by this offline Stage/PlaybackManager adapter.
  const full = {...description,name:'vacuum',size:new Vector2(story.width,story.height),
    resolutionScale:1,playback:new PlaybackStatus(playback),logger,
    timeEventsClass:ReadOnlyTimeEvents,sharedWebGLContext:new SharedWebGLContext(logger),
  } as unknown as FullSceneDescription<ThreadGeneratorFactory<View2D>>;
  full.onReplaced=new ValueDispatcher(full);
  const scene = new Scene2D(full);
  playback.setup([scene]);
  const stage = new Stage();
  stage.configure({size:new Vector2(story.width,story.height),resolutionScale:1,colorSpace:'srgb',background:paper});
  await playback.recalculate(); await playback.reset();
  document.body.append(stage.finalBuffer);
  window.drawMotionFrame=async(frame:number):Promise<string>=>{
    await playback.seek(frame);
    await stage.render(playback.currentScene,playback.previousScene);
    return stage.finalBuffer.toDataURL('image/png').split(',')[1];
  };
  window.motionReady=true;
}
void initialize();
