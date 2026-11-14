from explainer_studio.scene_kit import *

from shared.series import (ACTIVE_COLOR, ANSWER_COLOR, COLUMN_XS, INPUT_Y, LABEL_SIZE, PICK_Y, ROW_YS, CELL_H, Board,
                           get_cell, get_chip, get_input_slot, get_score_panel, get_state, get_top_line)


class FirstPick(NarratedScene):
    def construct(self) -> None:
        state = get_state("cp_pick_blue")
        board = Board(state, show_kv=False, columns=3)
        panel = get_score_panel(state)
        top_cell = board.cells[(1, 2)]
        rise = Arrow(top_cell.get_top(), panel.rows.get_right() + 0.3 * RIGHT, buff=0.1, stroke_width=4).set_color(GREY_B)

        # Beat: the last position scores every token (toy numbers)
        with self.play_beat("fp_scores") as beat:
            self.play(FadeIn(board.everything()), run_time=beat.get_seconds_until(0.2))
            self.play(GrowArrow(rise), run_time=beat.get_seconds_until(0.45))
            self.play(FadeIn(panel, lag_ratio=0.1), run_time=beat.get_seconds_until(0.8))

        # Beat: the decoding rule picks the highest score
        blue = get_chip(state["scores"]["pick"], "answer").move_to([COLUMN_XS[3], PICK_Y, 0])
        with self.play_beat("fp_pick") as beat:
            self.play(panel.by_token["blue"].bar.animate.set_fill(ACTIVE_COLOR), run_time=beat.get_seconds_until(0.5))
            self.play(FadeIn(blue, scale=1.2), run_time=beat.get_seconds_until(0.85))

        # Beat: picked, not processed: column 4 is empty
        column = VGroup(*(get_cell("empty", layer, 3) for layer in range(2)))
        slot = get_input_slot(3)
        number = Text("4", font_size=LABEL_SIZE).set_color(GREY_B).move_to([COLUMN_XS[3], INPUT_Y - 0.7, 0])
        tag = Text("picked, not processed", font_size=26).set_color(ANSWER_COLOR).next_to(blue, RIGHT, buff=0.25)
        tag.shift_onto_screen(buff=0.4)
        with self.play_beat("fp_not_processed") as beat:
            self.play(FadeIn(column), FadeIn(slot), FadeIn(number), run_time=beat.get_seconds_until(0.5))
            self.play(FadeIn(tag), run_time=beat.get_seconds_until(0.8))

        # Beat: each position scores only the next token
        only=VGroup(Text("Position → slot scored",font_size=26).set_color(ACTIVE_COLOR),Text("The → 2 · already known",font_size=24),Text("sky → 3 · already known",font_size=24),Text("is → 4 · next answer",font_size=24)).arrange(DOWN,aligned_edge=LEFT,buff=0.16).move_to([4.75,-0.1,0])
        with self.play_beat("fp_next_only") as beat:
            self.play(rise.animate.set_color(ACTIVE_COLOR), FadeIn(only), run_time=beat.get_seconds_until(0.6))

        # Beat: the token after blue needs position 4
        fifth = VGroup(DashedVMobject(RoundedRectangle(width=1.25, height=0.72, corner_radius=0.14), num_dashes=18).set_stroke(GREY_C, 2),
                       Text("?", font_size=36).set_color(ANSWER_COLOR)).move_to([COLUMN_XS[4], PICK_Y, 0])
        route=VMobject().set_points_as_corners([blue.get_right()+0.08*RIGHT,np.array([3.05,PICK_Y,0]),np.array([3.05,INPUT_Y,0]),slot.get_right()+0.08*RIGHT]).set_stroke(GREY_B,2)
        needs=VGroup(DashedVMobject(route,num_dashes=35),
            Arrow(slot.get_top()+0.04*UP,column[0].get_bottom()-0.04*UP,buff=0,thickness=2).set_color(GREY_B),
            Arrow(column[0].get_top()+0.04*UP,column[1].get_bottom()-0.04*UP,buff=0,thickness=2).set_color(GREY_B),
            Arrow(column[1].get_top()+0.04*UP,fifth.get_bottom()-0.04*UP,buff=0.04,thickness=2).set_color(GREY_B))
        needs_label=Text("process position 4 first",font_size=26).set_color(GREY_B).move_to([4.6,0.1,0])
        with self.play_beat("fp_settle") as beat:
            self.play(FadeOut(VGroup(panel, rise, only, tag)), run_time=beat.get_seconds_until(0.2))
            self.play(FadeIn(fifth), ShowCreation(needs), FadeIn(needs_label), run_time=beat.get_seconds_until(0.7))

        # Beat: the conclusion, held through the pause
        line = get_top_line("one trip → one new token")
        with self.play_beat("fp_conclusion") as beat:
            self.play(Write(line), run_time=beat.get_seconds_until(0.7))

        self.play(FadeOut(VGroup(board.everything(), blue, column, slot, number, fifth, needs, needs_label, line)))
