from explainer_studio.scene_kit import *
from shared.series import (ROW_YS, CELL_H, ACTIVE_COLOR, ANSWER_COLOR, BLOCKED_COLOR, COLUMN_XS, INPUT_Y, KV_COLOR, LABEL_SIZE,
                           PICK_Y, STATES, Board, get_chip, get_reads, get_score_panel, get_state, get_top_line)


class FeedBack(NarratedScene):
    def construct(self) -> None:
        board = Board(get_state("cp_feed_blue"), show_kv=True)
        for column in range(3):
            for layer in range(2):
                board.cells[(layer, column)] = board.cells[(layer, column)][0].copy().set_stroke(WHITE, 2).set_fill(WHITE, 0.10)
        blue_in = board.chips[3]
        blue_top = get_chip("blue", "answer").move_to([COLUMN_XS[3], PICK_Y, 0])
        self.add(board.grid(), VGroup(*(board.chips[c] for c in range(3))), board.numbers, board.layer_labels, blue_top)
        route = get_curved_arrow(blue_top.get_center(), blue_in.get_center(),
                                 angle=-PI/1.5, color=ANSWER_COLOR, stroke_width=4)
        with self.play_beat("fb_input") as beat:
            self.play(ShowCreation(route), run_time=beat.get_seconds_until(0.4))
            self.play(MoveAlongPath(blue_top,route.arc),run_time=beat.get_seconds_until(0.9))
            blue_top.move_to(blue_in)

        example = STATES["numeric_example"]
        fmt = lambda vector: "[" + ", ".join(f"{n:.2f}" for n in vector) + "]"
        label = Text("The · layer 1", font_size=26).set_color(KV_COLOR)
        key = Text(fmt(example["key"]), font_size=24)
        value = Text(fmt(example["value"]), font_size=24)
        contents = VGroup(label, key, value).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to([4.5,0.3,0])
        frame = SurroundingRectangle(contents,buff=0.22).set_stroke(KV_COLOR,1.5)
        inset = VGroup(frame,contents)
        saved_marks=VGroup(*(VGroup(*(Line([-0.35,yy,0],[0.35,yy,0]).set_stroke(KV_COLOR,3) for yy in [-0.08,0.08])).move_to(board.cells[(l,c)]) for l in range(2) for c in range(3)))
        with self.play_beat("fb_kv") as beat:
            self.play(FadeOut(route),FadeIn(saved_marks),
                      run_time=beat.get_seconds_until(0.3))
            self.play(FlashAround(board.cells[(0,0)],color=KV_COLOR), FadeIn(inset), run_time=beat.get_seconds_until(0.85))
        with self.play_beat("fb_value") as beat:
            key_named=Text("key   "+fmt(example["key"]),font_size=24).move_to(key)
            value_named=Text("value "+fmt(example["value"]),font_size=24).move_to(value)
            self.play(Transform(key,key_named),run_time=beat.get_seconds_until(0.40))
            self.play(Transform(value,value_named),FadeOut(saved_marks),*(board.cell_to(l,c,"kv") for l in range(2) for c in range(3)),run_time=beat.get_seconds_until(0.9))
        with self.play_beat("fb_own") as beat:
            self.play(FadeOut(inset),board.cell_to(0,3,"new"),run_time=beat.get_seconds_until(0.8))

        reads=get_reads(get_state("cp_process_blue"))
        fresh=get_top_line("Blue query: "+fmt(STATES["decode_example"]["query"]))
        weights=STATES["decode_example"]["attention"]["weights"]
        mix=Text("Mix values: " + " + ".join(f"{w:.2f} × {name}" for w,name in zip(weights,["The","sky","is","blue"])),font_size=28).set_color(KV_COLOR).move_to([0,1.7,0])
        with self.play_beat("fb_query") as beat:
            self.play(Write(fresh),run_time=beat.get_seconds_until(0.25))
            self.play(LaggedStartMap(ShowCreation,reads,lag_ratio=0.18),FadeIn(mix),run_time=beat.get_seconds_until(0.85))
        with self.play_beat("fb_reads") as beat:
            self.play(*(board.cell_to(0,c,"reused") for c in range(3)),run_time=beat.get_seconds_until(0.7))
        barrier=DashedLine([COLUMN_XS[3],INPUT_Y+0.44,0],[COLUMN_XS[2],ROW_YS[0]-CELL_H/2-0.04,0],dash_length=0.08).set_stroke(BLOCKED_COLOR,2)
        stop=Text("×",font_size=34).set_color(BLOCKED_COLOR).move_to(barrier.get_center())
        never=get_top_line("Later tokens cannot change earlier results")
        with self.play_beat("fb_still_valid") as beat:
            self.play(FadeOut(VGroup(reads,fresh,mix)),*(board.cell_to(0,c,"kv") for c in range(3)),run_time=beat.get_seconds_until(0.2))
            self.play(FadeIn(barrier),FadeIn(stop),Write(never),run_time=beat.get_seconds_until(0.85))

        detail=STATES["decode_example"]
        forward=Text("Blue · layer 1: "+fmt(detail["mixed"])+" → "+fmt(detail["output"]),font_size=28).set_color(ANSWER_COLOR).move_to([0,1.9,0])
        up=Arrow([COLUMN_XS[3],ROW_YS[0]+CELL_H/2+0.03,0],[COLUMN_XS[3],ROW_YS[1]-CELL_H/2-0.03,0],buff=0.01,thickness=2).set_color(ANSWER_COLOR)
        with self.play_beat("fb_ffn") as beat:
            self.play(FadeOut(VGroup(barrier,stop,never)),FadeIn(forward),run_time=beat.get_seconds_until(0.45))
            self.play(GrowArrow(up),run_time=beat.get_seconds_until(0.85))
        state=get_state("cp_pick_and");panel=get_score_panel(state)
        and_chip=get_chip(state["scores"]["pick"],"answer").move_to([COLUMN_XS[4],PICK_Y,0])
        with self.play_beat("fb_pick_and") as beat:
            self.play(FadeOut(VGroup(forward,up)),board.cell_to(0,3,"kv"),run_time=beat.get_seconds_until(0.15))
            self.play(board.cell_to(1,3,"new"),run_time=beat.get_seconds_until(0.35))
            self.play(board.cell_to(1,3,"kv"),FadeIn(panel),run_time=beat.get_seconds_until(0.65))
            self.play(panel.by_token["and"].bar.animate.set_fill(ACTIVE_COLOR),FadeIn(and_chip,scale=1.1),run_time=beat.get_seconds_until(0.95))
        loop=get_top_line("Decode: pick, feed back, process, pick")
        with self.play_beat("fb_loop") as beat:
            self.play(FadeOut(panel),run_time=beat.get_seconds_until(0.2))
            self.play(Write(loop),run_time=beat.get_seconds_until(0.8))
        self.play(FadeOut(VGroup(board.grid(),VGroup(*(board.chips[c] for c in range(3))),blue_top,
                                 board.numbers,board.layer_labels,and_chip,loop)))
