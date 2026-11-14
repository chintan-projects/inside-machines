"""r3 film adapter. State and scores come from the same JS mechanism as the page."""
import json
from pathlib import Path

from explainer_studio.scene_kit import *

STATES = json.loads((Path(__file__).parent / 'lesson_states.json').read_text())
TEACHING = json.loads((Path(__file__).parent / 'teaching.json').read_text())
TEAL = '#66D2BB'
GOLD = '#E8BB67'
BLUE = '#89AFFF'
MUTED = '#A8B8BE'
INK = '#162526'


def words(text: str, size: int = 30, color: str = WHITE, width: float = 12) -> Text:
    result = Text(text, font_size=size).set_color(color)
    if result.get_width() > width:
        result.set_width(width)
    return result


def chip(text: str, color: str = BLUE, width: float = 1.5) -> VGroup:
    box = RoundedRectangle(width=width, height=0.64, corner_radius=0.12)
    box.set_stroke(color, 2).set_fill(color, 0.14)
    return VGroup(box, words(text, 30, width=width-0.2).move_to(box))


def token_strip(tokens: list[str], y: float = 2.05) -> VGroup:
    cells = VGroup(*(chip(token, GOLD if index > 2 else BLUE) for index, token in enumerate(tokens)))
    cells.arrange(RIGHT, buff=0.2).move_to([0, y, 0])
    label = words('MODEL INPUT', 20, MUTED).next_to(cells, LEFT, buff=0.35)
    return VGroup(label, cells)


def task_rows(with_blue: bool = False, focus: int = 2) -> VGroup:
    names = ['The', 'sky', 'is', 'blue'] if with_blue else ['The', 'sky', 'is']
    rows = VGroup()
    for index, name in enumerate(names):
        y = 0.9 - index * 0.83
        source = chip(name, GOLD if index == 3 else BLUE).move_to([-3.8, y, 0])
        arrow = Arrow([-2.85, y, 0], [-1.75, y, 0], buff=0.02, thickness=3).set_color(TEAL if index == focus else MUTED)
        target = words(f'slot {index+2}', 31, TEAL if index == focus else WHITE).move_to([-0.7, y, 0])
        status = words(f'already supplied: {names[index+1]}' if index < len(names)-1 else 'first blank to fill', 28,
                       MUTED if index < len(names)-1 else GOLD, width=4.5).move_to([3.1, y, 0])
        rows.add(VGroup(source, arrow, target, status))
    return rows


def model(tokens: list[str], x: float = -2.9, y: float = -0.15, width: float = 5.3, waiting: bool = False) -> VGroup:
    frame = RoundedRectangle(width=width, height=2.9, corner_radius=0.16)
    frame.set_stroke(MUTED, 1.5).set_fill(WHITE, 0.025).move_to([x, y, 0])
    label = words('WAITING · NOT PROCESSED' if waiting else 'ONE PASS · BOTH LAYERS', 24, MUTED, width-0.4).move_to([x, y+1.16, 0])
    rows = VGroup()
    for index in range(2):
        row = RoundedRectangle(width=width-0.5, height=0.62, corner_radius=0.06)
        row.set_stroke(BLUE, 1.5).set_fill(BLUE, 0.1).move_to([x, y+0.45-index*1.03, 0])
        text = words(f'Layer {index+1}   ·   ' + ('waiting' if waiting else ' / '.join(tokens)), 27, width=width-0.85).move_to(row)
        rows.add(VGroup(row, text))
    arrow = Arrow([x, y+0.1, 0], [x, y-0.21, 0], buff=0, thickness=2).set_color(MUTED)
    return VGroup(frame, label, rows, arrow)


def input_sources() -> VGroup:
    group = VGroup()
    for layer, (source, y) in enumerate([('token numbers',0.45),('layer 1 output',-0.55)]):
        text = words(f'L{layer+1} input: {source}',27,BLUE,width=5.2).move_to([-3.1,y,0])
        label = words('prepare two lists',22,TEAL).move_to([-0.55,y+0.32,0])
        arrow = Arrow([-0.7,y,0],[0.35,y,0],buff=0.01,thickness=3).set_color(TEAL)
        group.add(text,label,arrow)
    group.add(words('Finished output → next layer',26,MUTED,width=5.3).move_to([-3.1,-1.5,0]))
    return group


def reading(stage: str, pass_index: int = 1) -> VGroup:
    trace = STATES['cached']['passes'][pass_index]['trace']['layers'][0]
    pairs = STATES['cached']['passes'][pass_index]['cacheByLayer'][0]
    vector = lambda v: '[' + ', '.join(f'{x:.2f}' for x in v) + ']'
    group = VGroup()
    if stage == 'shares':
        group.add(words('Blue’s comparison numbers: ' + vector(trace['query']),29,GOLD).move_to([0,1.2,0]))
    else:
        group.add(words('Share × reading list = contribution',30,TEAL).move_to([0,1.2,0]))
    for index, (name,pair,share) in enumerate(zip(['The','sky','is','blue'],pairs,trace['attention']['weights'])):
        y=0.55-index*0.67
        group.add(words(name,28,BLUE if index<3 else GOLD).move_to([-5.25,y,0]))
        if stage == 'shares':
            group.add(words('match '+vector(pair['key']),27,MUTED).move_to([-2.3,y,0]))
            group.add(Arrow([-0.2,y,0],[0.8,y,0],buff=0.02,thickness=2).set_color(TEAL))
            group.add(words(f'{100*share:.1f}%',32,TEAL).move_to([2.0,y,0]))
        else:
            contribution = [value*share for value in pair['value']]
            group.add(words(f'{100*share:.1f}% × '+vector(pair['value'])+' = '+vector(contribution),28,TEAL if index==0 else WHITE,width=10.2).move_to([0.8,y,0]))
    if stage=='shares':
        group.add(words('Comparison scores → shares adding to 100%',27,MUTED).move_to([0,-2.3,0]))
    else:
        group.add(words('Each reading list contributes its computed share.',27,MUTED).move_to([0,-2.3,0]))
    return group


def tray(count: int = 3, x: float = 3.1, named: bool = False) -> VGroup:
    frame = RoundedRectangle(width=5.4, height=2.9, corner_radius=0.16)
    frame.set_stroke(TEAL, 1.5).set_fill(TEAL, 0.045).move_to([x, -0.15, 0])
    label = words('KV CACHE' if named else 'SAVED PREPARATION', 25, TEAL).move_to([x, 1.02, 0])
    group = VGroup(frame, label)
    for layer in range(2):
        y = 0.3 - layer * 0.86
        group.add(words(f'L{layer+1}', 23, MUTED).move_to([x-2.3, y, 0]))
        for index, token in enumerate(['The', 'sky', 'is', 'blue']):
            xx = x-1.48+index*1.0
            rect = RoundedRectangle(width=0.9, height=0.68, corner_radius=0.06).move_to([xx, y, 0])
            rect.set_stroke(TEAL if index < count else MUTED, 1.5).set_fill(TEAL, 0.12 if index < count else 0)
            name = words(token, 23, WHITE if index < count else MUTED).move_to([xx, y+0.1, 0])
            strips = words(('K · V' if named else '═  ═') if index < count else 'empty', 18, TEAL if index < count else MUTED).move_to([xx, y-0.17, 0])
            group.add(VGroup(rect, name, strips))
    group.add(words('Two lists per position · separate store per layer', 20, TEAL, width=5.0).move_to([x, -1.3, 0]))
    return group


def scores(pass_index: int) -> VGroup:
    data = STATES['cached']['passes'][pass_index]['scores']
    rows = VGroup()
    for index, item in enumerate(data['list']):
        cell = chip(item['token'], GOLD if item['token'] == data['pick'] else MUTED, 1.55)
        cell.move_to([-3.8+index*1.9, 0.0, 0])
        number = words(f"{item['score']:.2f}", 31, GOLD if item['token'] == data['pick'] else WHITE).next_to(cell, DOWN, buff=0.22)
        rows.add(VGroup(cell, number))
    title = words(f"Final result at {'is' if pass_index == 0 else 'blue'} → candidate scores", 32).move_to([0, 0.95, 0])
    chosen = words(f"Choose {data['pick']}  ·  not processed yet", 34, GOLD).move_to([0, -1.32, 0])
    outside = words('CHOOSING HAPPENS AFTER THE LAYERS', 23, MUTED).move_to([0, -2.0, 0])
    return VGroup(title, rows, chosen, outside)


def compare() -> VGroup:
    panels = VGroup()
    for x, keep in [(-3.15, True), (3.15, False)]:
        count = len(STATES['cached' if keep else 'rebuilt']['passes'][1]['positions'])
        frame = RoundedRectangle(width=5.5, height=3.0, corner_radius=0.16).move_to([x, -0.25, 0]).set_stroke(TEAL, 2)
        title = words('Preparation kept' if keep else 'Preparation cleared', 31).move_to([x, 0.78, 0])
        number = words(str(count), 82, TEAL).move_to([x, -0.1, 0])
        text = words('blue' if keep else 'The / sky / is / blue', 29, GOLD).move_to([x, -0.95, 0])
        panels.add(VGroup(frame, title, number, text))
    label = words('Positions through the whole model · not timings', 28, MUTED).move_to([0, -2.25, 0])
    return VGroup(panels, label)


def visual(frame: str, beat: str) -> VGroup:
    if beat.startswith('simple_') or beat.startswith('core_'):
        return simple_visual(frame,beat)
    tokens = ['The','sky','is'] + (['blue'] if frame in ['feed_back','second_choice','whole'] else [])
    group = VGroup(token_strip(tokens))
    caption = ''
    if frame == 'tasks':
        if beat == 'token_numbers':
            group.add(chip('is').move_to([-3,0.1,0]))
            group.add(Arrow([-2,0.1,0],[0,0.1,0],buff=0.01,thickness=3).set_color(TEAL))
            group.add(words('[0.60, 0.40]',48,TEAL).move_to([2.7,0.1,0]))
            group.add(words('fixed toy lookup',28,MUTED).move_to([-1,0.65,0]))
            caption='Token → its starting numbers. No layer has changed them yet.'
        elif beat == 'past_rule':
            target=chip('is').move_to([3,0,0]);group.add(target)
            for index,name in enumerate(['The','sky','is']):
                source=chip(name).move_to([-3,0.9-index*0.9,0]);group.add(source)
                group.add(Arrow(source.get_right(),target.get_left(),buff=0.05,thickness=2).set_color(TEAL))
            caption='Information can come from itself and earlier positions only.'
        elif beat == 'layer_job':
            trace=STATES['cached']['passes'][0]['trace']['layers'][0]
            labels=['is input: [0.60, 0.40]','blend allowed positions','rework this position','changed: [1.26, 1.16] → layer 2']
            for index,text in enumerate(labels):
                group.add(words(text,33,BLUE if index==0 else TEAL).move_to([0,0.95-index*0.88,0]))
            caption='A layer changes numbers. It does not choose a word.'
        elif beat == 'one_pass_stages':
            block = model(['The','sky','is'], x=0, width=8)
            group.add(block)
            caption = 'Together inside a layer. Then onward to the next.'
        else:
            group.add(task_rows(focus=0 if beat == 'supplied_slots' else 2))
            caption = 'Task arrows, not guesses for the supplied words.'
    elif frame == 'first_choice':
        trace=STATES['cached']['passes'][0]['trace']['layers'][0]
        pairs=STATES['cached']['passes'][0]['cacheByLayer'][0]
        fmt=lambda v:'['+', '.join(f'{x:.2f}' for x in v)+']'
        if beat=='layer_start':
            group.add(model(['The','sky','is'],x=0,width=8))
            caption='Each layer reads allowed positions, then reworks locally.'
        elif beat=='matching_setup':
            for index,(name,pair) in enumerate(zip(['The'],pairs[:1])):
                item=STATES['cached']['passes'][0]['traces'][index]['layers'][0]
                label=name+' input '+fmt(item['input'])+' → matching '+fmt(pair['key'])
                group.add(words(label,31,BLUE,width=12).move_to([0,0.8-index*0.9,0]))
            caption='How much should is take from The? Prepare matching numbers.'
        elif beat=='compare_scores':
            group.add(words('is input: [0.60, 0.40]',36,BLUE).move_to([0,0.9,0]))
            group.add(words('[0.60 + 0.50 × 0.40, 0.40]',36,TEAL).move_to([0,0,0]))
            group.add(words('comparison numbers: [0.80, 0.40]',36,GOLD).move_to([0,-0.9,0]))
            caption='Make the comparison pair from this position’s input.'
        elif beat=='compare_result':
            group.add(words('is comparison numbers: '+fmt(trace['query']),32,GOLD).move_to([0,1.1,0]))
            group.add(words('The: (0.80 × 1.00 + 0.40 × 0.50) / √2 = 0.71',30,TEAL,width=12).move_to([0,0.15,0]))
            group.add(words('sky: 0.28                 is: 0.54',32,BLUE).move_to([0,-0.8,0]))
            caption='Comparison scores decide what to read, not the output word.'
        elif beat=='make_shares':
            group.add(words('Fixed conversion: larger score → larger share',30,TEAL).move_to([0,1.1,0]))
            for index,name in enumerate(['The','sky','is']):
                attention=trace['attention']
                text=f"{name}     {attention['scores'][index]:.2f}     →     {100*attention['weights'][index]:.1f}%"
                group.add(words(text,35,BLUE,width=12).move_to([0,0.35-index*0.8,0]))
            caption='Shares of information, totaling 100%. Exact conversion in the detail view.'
        elif beat=='reading_list':
            group.add(reading('take',0))
            caption='Second prepared list: the reading numbers, not layer outputs.'
        elif beat in ['blend_add','local_rework']:
            if beat=='blend_add':
                labels=[('Add contributions → blend '+fmt(trace['attention']['output']),TEAL),
                        ('is input: '+fmt(trace['input']),BLUE),
                        ('+ blend: '+fmt(trace['attention']['output']),TEAL),
                        ('= updated: '+fmt(trace['mixed']),GOLD)]
            else:
                labels=[('current pair: '+fmt(trace['mixed']),BLUE),
                        ('local rework → adjustment '+fmt(trace['feedForward']['delta']),TEAL),
                        ('full precision add ≈ '+fmt(trace['output']),GOLD),
                        ('rounded values; output → layer 2 input',MUTED)]
            for index,(text,color) in enumerate(labels):
                group.add(words(text,32,color,width=12).move_to([0,1.0-index*0.9,0]))
        elif beat=='layer_stack':
            group.add(model(['The','sky','is'],x=0,width=8))
            caption='Layer 1 output [1.26, 1.16] → layer 2 input [1.26, 1.16].'
        elif beat=='choose_outside':
            group.add(scores(0))
        else:
            group.add(input_sources(),tray())
            caption='Keep the matching and reading lists we already used.'
    elif frame == 'feed_back':
        if beat == 'slot_five_owner':
            group.add(task_rows(True, 3))
        elif beat == 'past_unchanged':
            group.add(tray(3,x=0))
            caption = 'Earlier positions never read blue. Their work stays valid.'
        else:
            group.add(model(['blue'],waiting=True),tray(3))
            caption = 'Blue has become input. Its preparation is still empty.'
    elif frame == 'second_choice':
        if beat in ['blend_add','local_rework']:
            trace=STATES['cached']['passes'][1]['trace']['layers'][0]
            fmt=lambda v:'['+', '.join(f'{x:.2f}' for x in v)+']'
            if beat=='blend_add':
                labels=[('Add the four contributions → '+fmt(trace['attention']['output']),TEAL),
                        ('blue input: '+fmt(trace['input']),BLUE),
                        ('+ blend: '+fmt(trace['attention']['output']),TEAL),
                        ('= updated: '+fmt(trace['mixed']),GOLD)]
            else:
                labels=[('current pair: '+fmt(trace['mixed']),BLUE),
                        ('local rework → adjustment '+fmt(trace['feedForward']['delta']),TEAL),
                        ('full precision add ≈ '+fmt(trace['output']),GOLD),
                        ('rounded values; output → layer 2 input',MUTED)]
            for index,(text,color) in enumerate(labels):
                group.add(words(text,32,color,width=12).move_to([0,1.0-index*0.9,0]))
        elif beat in ['match_share','take_values']:
            group.add(reading('shares' if beat=='match_share' else 'take'))
        elif beat == 'read_past':
            group.add(reading('shares'))
            caption='First lists set shares; second lists supply the reading numbers.'
        elif beat == 'choose_and':
            group.add(scores(1))
        else:
            group.add(model(['blue']),tray(4 if beat=='reads_tray' else 3))
            if beat=='reads_tray':
                for y in [0.15,-0.7]:
                    group.add(Arrow([0.35,y,0],[-0.18,y,0],buff=0.01,thickness=3).set_color(TEAL))
            caption = 'Only blue is reprocessed.' if beat=='one_lane' else 'Saved and new lists → blue’s reading step, at each layer.'
    elif frame == 'whole':
        if beat == 'replay_predict':
            group.add(tray(3,x=-3.1),tray(0,x=3.1))
            group.add(words('KEPT: old preparation',27,TEAL).move_to([-3.1,-1.95,0]))
            group.add(words('CLEARED: no preparation',27,GOLD).move_to([3.1,-1.95,0]))
            caption='What must go through the model again?'
        elif beat == 'names_and_scope':
            group.add(tray(4,x=0,named=True))
            caption = 'Keys: matching. Values: what to take. No stored answers.'
        else:
            group.add(compare())
            caption = 'Blue reads the past in both routes.' if beat=='empty_tray_count' else 'Same text → same prepared lists → same choice: and.'
    if caption:
        group.add(words(caption, 28, TEAL, width=12.2).move_to([0,-2.95,0]))
    return group


def simple_visual(frame: str, beat: str) -> VGroup:
    tokens=['The','sky','is'] + (['blue'] if frame in ['feed_back','second_choice','whole'] else [])
    group=VGroup(token_strip(tokens))
    caption=''
    if beat=='core_layer':
        group.add(words('ONE LAYER = ONE PROCESSING STAGE',28,MUTED).move_to([0,1.05,0]))
        group.add(chip('read itself + past',TEAL,width=6).move_to([0,0.2,0]))
        group.add(chip('update working numbers',BLUE,width=6).move_to([0,-1.0,0]))
        group.add(Arrow([0,-0.18,0],[0,-0.6,0],buff=0,thickness=3).set_color(TEAL))
        caption='Working numbers change. Word choice comes afterward.'
    elif beat=='core_preparation':
        source=chip('The input',BLUE,width=2.5).move_to([-3.4,0.7,0])
        saved=chip('two reading lists',TEAL,width=3.7).move_to([2.7,0.7,0])
        result=chip('finished result',BLUE,width=3.6).move_to([-3.4,-1.15,0])
        group.add(source,saved,result,Arrow(source.get_right(),saved.get_left(),buff=0.05,thickness=3).set_color(TEAL))
        group.add(Arrow(source.get_bottom(),result.get_top(),buff=0.05,thickness=3).set_color(BLUE))
        caption='Reading lists come from the input; they are not the finished result.'
    elif beat=='core_stages':
        group.add(model(['The','sky','is'],x=0,width=8))
        caption='Each layer has its own preparation. Results move onward.'
    elif beat=='core_valid':
        for index,text in enumerate(['Earlier positions cannot read blue',
                                     'Their layer-1 results stay unchanged',
                                     'Same layer-2 inputs → same prepared lists']):
            group.add(words(text,33,TEAL,width=12).move_to([0,0.9-index*1.0,0]))
        caption='The old reading data stays valid at both layers.'
    elif beat=='core_reuse':
        group.add(model(['blue']),tray(4))
        caption='Only blue runs. It reads saved past + its own new data.'
    elif beat=='core_next':
        group.add(scores(1))
    elif beat=='core_cache_name':
        group.add(tray(4,x=0,named=True))
        caption='Input-derived reading data. Past is still read.'
    elif beat in ['simple_layers','simple_layer_order']:
        group.add(model(['The','sky','is'],x=0,width=8))
        caption='Each stage: read itself + past → update this position.'
    elif beat=='simple_choice':
        group.add(scores(0))
    elif beat=='simple_not_processed':
        group.add(model(['The','sky','is']))
        group.add(chip('blue',GOLD).move_to([3.2,0,0]))
        group.add(words('chosen outside',29,GOLD).move_to([3.2,-0.8,0]))
        caption='The model processed is. Blue has no result of its own yet.'
    elif beat=='simple_feed':
        group.add(task_rows(True,3))
        caption='Chosen blue goes back in. Its task is slot 5.'
    elif beat=='simple_new_pass':
        group.add(model(['blue'],x=0,width=8))
        caption='Build a result at blue before choosing what follows blue.'
    elif beat in ['simple_prepare','simple_blue_pair']:
        owner='The' if beat=='simple_prepare' else 'blue'
        color=BLUE if owner=='The' else GOLD
        source=chip(owner+' input',color,width=2.3).move_to([-4.1,0.05,0])
        first=chip('matching list',TEAL,width=3.4).move_to([1.7,0.8,0])
        second=chip('reading list',TEAL,width=3.4).move_to([1.7,-0.8,0])
        group.add(source,first,second)
        group.add(Arrow(source.get_right(),first.get_left(),buff=0.05,thickness=3).set_color(TEAL))
        group.add(Arrow(source.get_right(),second.get_left(),buff=0.05,thickness=3).set_color(TEAL))
        group.add(words('one position · one prepared pair',29,WHITE).move_to([0,-1.8,0]))
        caption='The: prepared during the prompt pass.' if owner=='The' else 'Blue: preparing its new pair is part of processing.'
    elif beat=='simple_match':
        shares=STATES['cached']['passes'][1]['trace']['layers'][0]['attention']['weights']
        group.add(words('Current blue + first lists → comparisons → shares',31,TEAL,width=12).move_to([0,1.05,0]))
        x=-5.5
        for name,share,color in zip(['The','sky','is','blue'],shares,[BLUE,TEAL,MUTED,GOLD]):
            rect=Rectangle(width=11*share,height=0.7).set_fill(color,0.55).set_stroke(color,2)
            rect.move_to([x+11*share/2,-0.1,0]);x+=11*share
            group.add(rect)
            group.add(words(f'{name} {100*share:.1f}%',25,WHITE,width=11*share-0.15).move_to(rect))
        caption='First prepared lists help set each position’s share.'
    elif beat=='simple_query':
        source=chip('blue input',GOLD,width=2.5).move_to([-3.4,0.3,0])
        query=chip('query: compare now',GOLD,width=4).move_to([2.3,0.3,0])
        group.add(source,query,Arrow(source.get_right(),query.get_left(),buff=0.05,thickness=3).set_color(GOLD))
        group.add(words('Blue’s saved pair is separate: matching list + reading list',28,TEAL,width=12).move_to([0,-1.25,0]))
        caption='Query does the comparing. Matching lists are compared against.'
    elif beat=='simple_take':
        trace=STATES['cached']['passes'][1]['trace']['layers'][0]
        share=trace['attention']['weights'][0]
        group.add(words(f'The: use {100*share:.1f}% of its second list',35,TEAL).move_to([0,1.0,0]))
        group.add(words('[0.80, 0.00] × 20.1% ≈ [0.16, 0.00]',38,TEAL,width=12).move_to([0,-0.1,0]))
        group.add(words('The + sky + is + blue contributions → one blend',30,WHITE).move_to([0,-1.25,0]))
        caption='Every entry scaled. No entries removed. Values rounded.'
    elif beat=='simple_keep':
        source=chip('blue input',GOLD,width=2.5).move_to([-3.4,0.7,0])
        saved=chip('saved pair stays',TEAL,width=3.7).move_to([2.7,0.7,0])
        result=chip('finished output',BLUE,width=3.6).move_to([-3.4,-1.15,0])
        group.add(source,saved,result,Arrow(source.get_right(),saved.get_left(),buff=0.05,thickness=3).set_color(TEAL))
        group.add(Arrow(source.get_bottom(),result.get_top(),buff=0.05,thickness=3).set_color(BLUE))
        group.add(words('read + local update',25,MUTED).move_to([-0.4,-0.3,0]))
        caption='The prepared pair stays. A different finished result moves onward.'
    elif beat=='simple_mix_result':
        for index,text in enumerate(['Combine the scaled reading contributions',
                                     'Add this blend to blue’s working input',
                                     'Blue’s working numbers change']):
            group.add(words(text,32,TEAL if index<3 else GOLD,width=12).move_to([0,1-index*0.9,0]))
        caption='Working result changes. Saved preparation is a separate object.'
    elif beat=='simple_local':
        for index,text in enumerate(['Only blue’s updated numbers',
                                     'Fixed local function → adjustment',
                                     'Add the adjustment back',
                                     'Finished layer output']):
            group.add(words(text,32,TEAL if index<3 else GOLD,width=12).move_to([0,1-index*0.9,0]))
        caption='No other position is read again during this local operation.'
    elif beat=='simple_next_layer':
        output=chip('L1 finished output',BLUE,width=3.8).move_to([-3.4,0.85,0])
        next_input=chip('L2 input',BLUE,width=2.5).move_to([-3.4,-0.85,0])
        new_pair=chip('L2 prepared pair',TEAL,width=3.7).move_to([2.7,-0.85,0])
        group.add(output,next_input,new_pair)
        group.add(Arrow(output.get_bottom(),next_input.get_top(),buff=0.05,thickness=3).set_color(BLUE))
        group.add(Arrow(next_input.get_right(),new_pair.get_left(),buff=0.05,thickness=3).set_color(TEAL))
        caption='A new layer input makes a separate prepared pair.'
    elif beat=='simple_valid':
        group.add(tray(3,x=0))
        caption='Past → blue is allowed. Blue → earlier positions is blocked.'
    elif beat=='simple_valid_next':
        for index,text in enumerate(['Earlier layer-1 results stay unchanged',
                                     '↓ same inputs to layer 2',
                                     '↓ same prepared pairs at layer 2']):
            group.add(words(text,34,TEAL,width=12).move_to([0,0.9-index*1.0,0]))
        caption='Appending blue cannot change earlier work in either layer.'
    elif beat=='simple_reuse':
        group.add(model(['blue']),tray(4))
        caption='Only blue is processed. Old pairs + its own pair are read.'
    elif beat=='simple_next_choice':
        group.add(scores(1))
    elif beat=='simple_same':
        group.add(compare())
        caption='Same input → same preparation → same choice: and.'
    elif beat=='simple_names':
        group.add(tray(4,x=0,named=True))
        caption='Keys: set shares. Values: what to read. Past is still read.'
    if caption:
        group.add(words(caption,28,TEAL,width=12.4).move_to([0,-2.95,0]))
    return group


class CoreScene(NarratedScene):
    frame_id: str = ''

    def construct(self) -> None:
        frame = next(item for item in TEACHING['core'] if item['id'] == self.frame_id)
        headline = words(frame['title'], 40, width=12.6).move_to([0,3.15,0])
        scope = words('Fixed untrained toy · whole-word tokens here · ordinary next-token generation', 18, MUTED).move_to([0,-3.65,0])
        self.add(headline,scope)
        previous = None
        for item in frame['beats']:
            picture = visual(self.frame_id,item['id'])
            with self.play_beat(item['id']) as beat:
                if previous is not None:
                    self.play(FadeOut(previous),run_time=0.18)
                self.play(FadeIn(picture,shift=0.03*UP),run_time=0.45)
                if item['id']=='simple_feed':
                    token=picture[0][1][3]
                    target=token.get_center().copy()
                    token.move_to([4.9,-2.0,0])
                    path=get_curved_arrow(token.get_center(),target,angle=PI/2,color=GOLD,stroke_width=3)
                    self.play(ShowCreation(path),run_time=0.35)
                    self.play(MoveAlongPath(token,path.arc),run_time=min(2,beat.get_seconds_until(0.8)))
                    self.play(FadeOut(path),run_time=0.2)
            previous = picture
