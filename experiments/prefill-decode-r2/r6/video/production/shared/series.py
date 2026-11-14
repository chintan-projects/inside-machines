"""Render computed scalar data. Model rules live in lesson/mechanism.mjs."""
import json
import textwrap
from pathlib import Path
from explainer_studio.scene_kit import *
from shared.workbench import draw_workbench

DATA=json.loads((Path(__file__).parent/'narration.json').read_text())
TEAL,GOLD,BLUE,MUTED='#65D5BE','#EDC16B','#91B6FF','#ACBBC2'

def text(content: str,size: int=38,color: str=WHITE,width: float=12.3) -> Text:
    item=Text(content.replace('’', chr(39)).replace('‘', chr(39)),font_size=size).set_color(color)
    if item.get_width()>width:item.set_width(width)
    return item

def card(content: str,color: str=BLUE,width: float=3) -> VGroup:
    box=RoundedRectangle(width=width,height=.85,corner_radius=.12).set_fill(color,.1).set_stroke(color,2)
    return VGroup(box,text(content,48,color,width-.25).move_to(box))

def table(rows: list,top: float=1.35,bottom: float=-2.5) -> VGroup:
    group=VGroup();has_selection=any(r.get('selected') for r in rows)
    for i,r in enumerate(rows):
        label=text(r['label'],30,MUTED)
        value=text(textwrap.fill(r['value'],width=54,break_long_words=False),46,GOLD if r.get('selected') or (not has_selection and i==len(rows)-1) else WHITE).next_to(label,DOWN,buff=.09,aligned_edge=LEFT)
        group.add(VGroup(label,value))
    group.arrange(DOWN,buff=.18,aligned_edge=LEFT)
    if group.get_height()>top-bottom:group.set_height(top-bottom)
    group.move_to([-5.9,top,0],aligned_edge=UL)
    return group

def cache(p: dict) -> VGroup:
    group=VGroup()
    for layer,count in enumerate(p['counts']):
        if p.get('visibleLayer') is not None and p['visibleLayer']!=layer:continue
        y=1.1-layer*1.9;group.add(text(f'Layer {layer+1}',32,MUTED,width=2).move_to([-5.3,y,0]))
        for i,name in enumerate(p['cacheNames']):
            x=-2.9+i*2.1;color=(GOLD if i==3 else TEAL) if i<count else MUTED
            chip=card(name,color,1.8).move_to([x,y,0])
            entry=p['entries'][layer][i] if i<count else None
            label=('new K / V' if i==3 else 'old K / V') if entry else 'empty'
            if entry and i in p['expandedPositions']:label='old K '+entry['key']+'\nV '+entry['value']
            caption=text(label,26,color,width=1.95).next_to(chip,DOWN,buff=.12)
            group.add(chip,caption)
    group.add(text('Each layer keeps its own input-derived preparation',28,TEAL).move_to([0,-2.6,0]))
    return group

def body(p: dict) -> VGroup:
    if p['kind']=='workbench':return draw_workbench(p['workbench'],text,card,BLUE,TEAL,GOLD,MUTED)
    if p['kind']=='distribution':
        d=p['distribution'];rows=d['rows'];group=VGroup();center=.65-.45*(len(rows)-1)
        group.add(text('Matches',30,BLUE).move_to([-4.2,1.65,0]),text('Reading shares',30,GOLD).move_to([4.2,1.65,0]))
        box=RoundedRectangle(width=3.8,height=.9*len(rows),corner_radius=.12).set_fill(TEAL,.06).set_stroke(TEAL,2).move_to([0,center,0])
        group.add(box,text('Make reading\nfractions',36,WHITE,width=3.2).move_to([0,center+.2,0]),text('all matches together',23,TEAL,width=3.2).move_to([0,center-.5,0]))
        ys=[]
        for i,r in enumerate(rows):
            y=.65-.9*i;ys.append(y)
            left=card(r['match'],BLUE,2.5).set_height(.7).move_to([-4.2,y,0]);right=card(r['fraction'] if d['reveal'] else '?',GOLD,2.5).set_height(.7).move_to([4.2,y,0])
            group.add(left,right,text(r['source'],28,WHITE,width=1.3).move_to([-6.1,y,0]),text(r['source'],28,WHITE,width=1.3).move_to([6.1,y,0]))
            group.add(Line(left.get_right(),[-2.55,y,0]).set_color(BLUE),Line([2.55,y,0],right.get_left()).set_color(GOLD))
        group.add(Line([-2.55,max(ys),0],[-2.55,min(ys),0]).set_color(BLUE),Line([2.55,max(ys),0],[2.55,min(ys),0]).set_color(GOLD))
        group.add(Arrow([-2.55,center,0],box.get_left(),buff=.05,thickness=2).set_color(BLUE),Arrow(box.get_right(),[2.55,center,0],buff=.05,thickness=2).set_color(GOLD))
        return group
    if p['kind']=='operation':
        op=p['operation'];group=VGroup();chips=[]
        for x,value,label,color in [(-4,op['left'],op['leftLabel'],BLUE),(0,op['operator'],op['operatorLabel'],TEAL),(4,op['right'],op['rightLabel'],GOLD)]:
            chip=card(value,color,3.2).move_to([x,0,0]);chips.append(chip)
            group.add(chip,text(label,30,color,width=3.7).move_to([x,1,0]))
        group.add(Arrow(chips[0].get_right(),chips[1].get_left(),buff=.08,thickness=3).set_color(MUTED),Arrow(chips[1].get_right(),chips[2].get_left(),buff=.08,thickness=3).set_color(MUTED))
        return group
    if p['kind']=='boundary':
        left=card(p['handoff'],BLUE,3.6).move_to([-3,0.6,0]);right=card(p['handoff'],BLUE,3.6).move_to([3,.6,0])
        kept=card('K '+p['retained']['key']+' / V '+p['retained']['value'],TEAL,7).move_to([0,-1.55,0])
        return VGroup(left,right,Arrow(left.get_right(),right.get_left(),buff=.1,thickness=3).set_color(BLUE),text('finished first-stage result',30,BLUE,width=5.5).move_to([-3,1.55,0]),text('same second-stage input',30,BLUE,width=5.5).move_to([3,1.55,0]),kept,text('separate preparation stays at the first stage',28,TEAL).move_to([0,-2.45,0]))
    if p['kind']=='cache':return cache(p)
    if p['kind']=='input':
        chips=VGroup(*(card(t,GOLD if t=='?' else BLUE,1.6) for t in p['tokens'])).arrange(RIGHT,buff=.2).move_to([0,1.2,0])
        return VGroup(chips,table(p['rows'],.25,-2.4))
    if p['kind']=='choice':
        return VGroup(table(p['rows'],1.3,-1.3),card(p['chosen']+' · selected, not processed',GOLD,9).move_to([0,-2.2,0]))
    return table(p['rows'])

class WorkedScene(NarratedScene):
    scene_id: str=''
    def construct(self) -> None:
        scene=next(s for s in DATA['scenes'] if s['id']==self.scene_id)
        self.add(text(scene['title'],42,width=12.7).move_to([0,3.25,0]));previous=None;previous_kind=None
        for beat in scene['beats']:
            p=DATA['panels'][beat['id']]
            group=VGroup(text(p['subject'],30,TEAL).move_to([-5.9,2.65,0],aligned_edge=LEFT),body(p),text(textwrap.fill(p['note'],width=110,break_long_words=False),24,MUTED).move_to([0,-3.55,0]))
            if p['guide']:group.add(text(p['guide'],26,BLUE).move_to([0,2.05,0]))
            if p.get('readingFractions'):group.add(text('Computed fractions: '+' · '.join(r['name']+' '+r['percent']+'%' for r in p['readingFractions']),28,TEAL).move_to([0,-2.85,0]))
            with self.play_beat(beat['id']) as duration:
                if previous is not None and previous_kind=='workbench' and p['kind']=='workbench':
                    # Keep shared positions steady; morphing whole text groups ghosts labels.
                    self.remove(previous)
                    self.add(group)
                    phase=p['workbench']['phase']
                    focal={'query':(-.7,.95,2,.98),'key':(-.7,-.25,2,.98),'match':(3.2,.6,2,.8),'amount_positive':(3.2,-.65,2,.8),'amount_add':(3.2,-1.95,2,.8),'parts':(3.2,-1.95,2,.8),'query_name':(-.7,1.6,2.3,.42),'key_name':(-.7,.4,2.3,.42)}.get(phase)
                    if focal:
                        x,y,width,height=focal
                        focus=RoundedRectangle(width=width,height=height,corner_radius=.08).set_stroke(GOLD,2).move_to([x,y,0])
                        self.play(FadeIn(focus),run_time=.15)
                        self.wait(.35)
                        self.play(FadeOut(focus),run_time=.15)
                elif previous is not None and previous_kind=='distribution' and p['kind']=='distribution':
                    self.play(FadeOut(previous),FadeIn(group),run_time=.45)
                else:
                    if previous is not None:self.play(FadeOut(previous),run_time=.18)
                    self.play(FadeIn(group,shift=.04*UP),run_time=.5)
                if p.get('scanRows'):
                    rows=list(group[1]);slot=max(0,duration.remaining_seconds-.15)/len(rows)
                    for row in rows:
                        focus=SurroundingRectangle(row,buff=.07).set_stroke(GOLD,1.5)
                        self.play(FadeIn(focus),run_time=.15)
                        self.wait(max(0,slot-.3))
                        self.play(FadeOut(focus),run_time=.15)
            previous=group;previous_kind=p['kind']
