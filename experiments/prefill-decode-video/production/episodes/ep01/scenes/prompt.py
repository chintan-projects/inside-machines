from explainer_studio.scene_kit import *

from shared.series import (BLOCKED_COLOR, CELL_HEIGHT, CELL_WIDTH, COLUMN_XS, PROMPT_COLOR, ROW_YS, TokenGrid,
                           get_cell_center, get_conclusion, get_input_point, get_layer_labels, get_look_arrow,
                           get_main_question_line, get_note, get_prompt_chip, get_pulse, get_self_loop)

WORDS = ["The", "sky", "is"]
IDS = ["#791", "#12930", "#318"]  # illustrative token IDs


class Prompt(NarratedScene):
    def construct(self):
        # Close framing for the three-position introduction; shared mechanism coordinates stay unchanged.
        self.frame.set_height(6.4).move_to([-2.8, 0.0, 0.0])
        question_line = get_main_question_line().move_to([-2.8, 2.85, 0.0])
        sentence = Text("The sky is", font_size=44).move_to(get_input_point(1))
        chips = VGroup(*(get_prompt_chip(w).move_to(get_input_point(i)) for i, w in enumerate(WORDS)))
        ids = VGroup(*(get_note(t, GREY_B, 20).next_to(chips[i], DOWN, buff=0.15) for i, t in enumerate(IDS)))
        token_note = get_note("tokens (illustrative split and IDs)", GREY_B, 22)
        token_note.next_to(chips, RIGHT, buff=0.6)

        # Beat: tokens are ID numbers standing for pieces of text
        with self.play_beat("tokens") as beat:
            self.play(FadeIn(sentence), run_time=0.8)
            self.play(FadeTransform(sentence, chips), run_time=beat.get_seconds_until(0.5))
            self.play(FadeIn(ids, lag_ratio=0.2), FadeIn(token_note), run_time=1.0)

        # Beat: a stack of layers, three drawn
        grid = TokenGrid()
        columns = VGroup(*(grid.build_column(c, "empty") for c in range(3)))
        layer_labels = get_layer_labels()
        schematic = get_note("3 layers\n(schematic)", GREY_B, 20)
        schematic.next_to(layer_labels, UP, buff=0.3).align_to(layer_labels, RIGHT)
        with self.play_beat("layers") as beat:
            self.play(FadeOut(ids), FadeOut(token_note), FadeIn(question_line), run_time=0.6)
            self.play(LaggedStart(*(FadeIn(col, shift=0.3 * UP, lag_ratio=0.2) for col in columns), lag_ratio=0.15),
                      FadeIn(layer_labels), run_time=beat.get_seconds_until(0.7))
            self.play(FadeIn(schematic), run_time=0.6)

        # Beat: each layer computes with the learned numbers, the weights
        weights_brace = Brace(VGroup(*(grid.cells[(r, 2)] for r in range(3))), RIGHT, buff=0.25)
        weights_label = get_note("each layer's math uses\nlearned numbers: weights", GREY_A, 24)
        weights_label.next_to(weights_brace, RIGHT, buff=0.2)
        with self.play_beat("weights") as beat:
            self.play(GrowFromCenter(weights_brace), FadeIn(weights_label), run_time=beat.get_seconds_until(0.5))

        # Beat: the whole prompt is known, so all three enter layer 1 together
        up_arrows = VGroup(*(
            Arrow(chips[c].get_top(), get_cell_center(0, c) + (CELL_HEIGHT / 2) * DOWN, buff=0.06)
            .set_stroke(PROMPT_COLOR, 3) for c in range(3)))
        with self.play_beat("known") as beat:
            self.play(FadeOut(weights_brace), FadeOut(weights_label), run_time=0.5)
            self.play(*(GrowArrow(a) for a in up_arrows), run_time=beat.get_seconds_until(0.6))
            self.play(*(get_pulse(grid.cells[(0, c)]) for c in range(3)),
                      *(grid.change(0, c, "processed") for c in range(3)), run_time=0.8)

        # Beat: attention gathers from itself and earlier tokens
        is_arrows = VGroup(get_look_arrow(2, 1), get_look_arrow(2, 0), get_self_loop(2))
        attention_label = get_note("attention", WHITE, 28).move_to([COLUMN_XS[2] + 1.9, -1.45, 0])
        with self.play_beat("look_back") as beat:
            self.play(FadeOut(up_arrows), run_time=0.5)
            for arrow in is_arrows:
                self.play(ShowCreation(arrow.arc), FadeIn(arrow.tip), run_time=0.7)
            self.play(FadeIn(attention_label), run_time=0.5)

        # Beat: never from later ones: "sky" sees "The" and itself, not "is"
        sky_arrows = VGroup(get_look_arrow(1, 0), get_self_loop(1))
        forward = get_look_arrow(1, 2, color=BLOCKED_COLOR)
        mid = forward.arc.point_from_proportion(0.5)
        cross = VGroup(Line(mid + 0.16 * (UL), mid + 0.16 * (DR)), Line(mid + 0.16 * (UR), mid + 0.16 * (DL)))
        cross.set_stroke(BLOCKED_COLOR, 5)
        with self.play_beat("no_future") as beat:
            self.play(FadeOut(is_arrows), run_time=0.5)
            self.play(*(ShowCreation(a.arc) for a in sky_arrows), *(FadeIn(a.tip) for a in sky_arrows),
                      Indicate(chips[1].label), run_time=1.0)
            self.play(ShowCreation(forward.arc), FadeIn(forward.tip), run_time=beat.get_seconds_until(0.75))
            self.play(ShowCreation(cross), run_time=0.4)

        # Beat: built for writing, where later words don't exist yet
        future_column = VGroup(grid.get_column(2), chips[2])
        with self.play_beat("why_no_future") as beat:
            self.play(*dim(future_column, opacity=0.15), run_time=beat.get_seconds_until(0.5))

        # Beat: the rule stays even on a known prompt: a causal mask
        mask_label = get_note("causal mask:\nitself and earlier only", BLOCKED_COLOR, 24)
        mask_label.next_to(attention_label, DOWN, buff=0.25).align_to(attention_label, LEFT)
        with self.play_beat("mask_name") as beat:
            self.play(*undim(future_column), run_time=0.8)
            self.play(FadeIn(mask_label, shift=0.1 * UP), FlashAround(cross, color=BLOCKED_COLOR),
                      run_time=beat.get_seconds_until(0.9))

        # Beat: layers go in order
        between = VGroup()
        for r in range(2):
            for c in range(3):
                start = get_cell_center(r, c) + (CELL_HEIGHT / 2) * UP
                end = get_cell_center(r + 1, c) + (CELL_HEIGHT / 2) * DOWN
                between.add(Arrow(start, end, buff=0.03, stroke_width=3).set_stroke(GREY_A))
        with self.play_beat("layer_order") as beat:
            self.play(FadeOut(VGroup(sky_arrows, forward, cross, attention_label, mask_label)), run_time=0.5)
            for r in range(1, 3):
                self.play(*(GrowArrow(between[(r - 1) * 3 + c]) for c in range(3)), run_time=0.6)
                self.play(*(get_pulse(grid.cells[(r, c)]) for c in range(3)),
                          *(grid.change(r, c, "processed") for c in range(3)), run_time=0.7)

        # Beat: "together" means across known tokens, never looking ahead
        conclusion = get_conclusion("Known tokens: together, none looking ahead.").move_to([-2.8, -2.82, 0.0])
        with self.play_beat("parallel_conclusion") as beat:
            self.play(FadeOut(between), run_time=0.4)
            self.play(Write(conclusion), run_time=beat.get_seconds_until(0.8))

        self.play(FadeOut(VGroup(grid.get_all(), chips, layer_labels, schematic, conclusion, question_line)))
