"""Keep the real two-input calculation visible; reveal one reached step at a time."""
from explainer_studio.scene_kit import *


def draw_workbench(w: dict, make_text, make_card, blue: str, teal: str, gold: str, muted: str) -> VGroup:
    phase=w['phase'];group=VGroup()
    for y,who,start,rule,result,ready,role,active in [
        (.95,'sky',w['readerInput'],'× '+w['readerRule'],w['query'],True,w['readerLabel'],phase in ['query','query_name']),
        (-.25,w['source'],w['sourceInput'],'× '+w['sourceRule'],w['key'],w['sourceReady'],w['sourceLabel'],phase in ['key','key_name'])]:
        color=teal if active else blue
        a=make_card(start,blue,1.7).move_to([-4.9,y,0]);b=make_card(rule,color,1.7).move_to([-2.8,y,0]);c=make_card(result if ready else '?',color,1.7).move_to([-.7,y,0])
        group.add(a,b,c,make_text(who+' input',26,blue,width=1.9).move_to([-4.9,y+.65,0]),make_text(role,26,color,width=2).move_to([-.7,y+.65,0]))
        group.add(Arrow(a.get_right(),b.get_left(),buff=.03,thickness=2).set_color(muted),Arrow(b.get_right(),c.get_left(),buff=.03,thickness=2).set_color(muted))
        group.add(Arrow(c.get_right(),[2.1,.6,0],buff=.04,thickness=2).set_color(muted))
    color=gold if phase=='match' else teal
    product=make_card(w['match'] if w['matchReady'] else '?',color,2.1).set_height(.65).move_to([3.2,.6,0])
    group.add(product,make_text('multiply prepared numbers',28,color,width=4).move_to([3.2,1.35,0]),make_text('match' if w['matchReady'] else 'product',26,color,width=3).move_to([5.1,.6,0]))
    if w['positiveReady']:
        positive=make_card(w['positive'],gold if phase=='amount_positive' else teal,2.1).set_height(.65).move_to([3.2,-.65,0])
        group.add(positive,Arrow(product.get_bottom(),positive.get_top(),buff=.04,thickness=2).set_color(muted),make_text('positive part',26,teal,width=2.4).move_to([5.25,-.05,0]))
        if w['amountReady']:
            amount=make_card(w['parts'],gold,2.1).set_height(.65).move_to([3.2,-1.95,0])
            group.add(amount,Arrow(positive.get_bottom(),amount.get_top(),buff=.04,thickness=2).set_color(muted),make_text('+ 1',28,teal,width=2).move_to([5.1,-1.3,0]),make_text('amount for '+w['source'],28,gold,width=3.5).move_to([3.2,-2.6,0]))
    group.add(make_text('The value '+w['keptValue']+' stays ready for reading',28,blue,width=6.5).move_to([-3.2,-1.25,0]))
    if w['previousParts']:
        group.add(make_text('Already complete: The amount '+w['previousParts'],28,teal,width=6.5).move_to([-3.2,-1.8,0]))
    if w['completedResult']:group.add(make_text('Completed Sky result '+w['completedResult']+' stays ready',28,blue,width=6.5).move_to([-3.2,-2.2,0]))
    return group
