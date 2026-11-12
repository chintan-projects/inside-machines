from explainer_studio.scene_kit import *

from shared.series import (ACTIVE_COLOR, CELL_HEIGHT, KV_COLOR, OUTPUT_COLOR, TokenGrid, get_cell_center,
                           get_conclusion, get_input_point, get_layer_labels, get_look_arrow, get_main_question_line,
                           get_note, get_output_chip, get_output_point, get_prompt_chip, get_pulse, get_return_path,
                           get_self_loop)

WORDS = ["The", "sky", "is"]
PANEL_X = 4.75


def get_chain_row(left: str, step: str, right: str) -> Parts:
    a = get_output_chip(left)
    b = get_output_chip(right)
    arrow = Arrow(LEFT, RIGHT, buff=0).set_width(1.3).set_stroke(GREY_A, 3)
    tag = get_note(step, GREY_A, 22)
    row = VGroup(a, arrow, b).arrange(RIGHT, buff=0.15)
    tag.next_to(arrow, UP, buff=0.08)
    parts = Parts(a, arrow, b, tag)
    parts.left_chip, parts.arrow, parts.right_chip, parts.tag = a, arrow, b, tag
    return parts


class Decode(NarratedScene):
    def run_column(self, grid: TokenGrid, column: int, run_time: float = 1.8, with_arrows: bool = False):
        """Process one token up the column: each layer goes active, then saved."""
        per_row = run_time / 3
        for r in range(3):
            anims = [grid.change(r, column, "active")]
            anims += [get_pulse(grid.cells[(r, c)], KV_COLOR, 0.6) for c in range(column)]
            self.play(*anims, run_time=per_row * 0.5)
            self.play(grid.change(r, column, "saved"), run_time=per_row * 0.5)

    def construct(self):
        question_line = get_main_question_line()
        grid = TokenGrid()
        saved_columns = VGroup(*(grid.build_column(c, "saved") for c in range(3)))
        empty_column = grid.build_column(3, "empty")
        chips = VGroup(*(get_prompt_chip(w).move_to(get_input_point(i)) for i, w in enumerate(WORDS)))
        layer_labels = get_layer_labels()
        blue_chip = get_output_chip("blue").move_to(get_output_point(2))
        cache_label = get_note("KV cache (saved)", KV_COLOR, 30)
        cache_label.next_to(saved_columns, UP, buff=0.27).align_to(saved_columns, LEFT)
        prefill_label = Text("PREFILL", font_size=36).set_color(WHITE).next_to(chips, DOWN, buff=0.45)

        # Beat: prefill gave one token and a full cache; now, the next token?
        with self.play_beat("seam_decode") as beat:
            self.play(FadeIn(VGroup(question_line, saved_columns, empty_column, chips, layer_labels, blue_chip,
                                    cache_label, prefill_label)), run_time=0.8)
            self.play(FadeOut(prefill_label), run_time=beat.get_seconds_until(0.6))
            self.play(Indicate(blue_chip.label, color=OUTPUT_COLOR), run_time=1.0)

        # Beat: scores come from the top of the newest token, so blue needs its own climb
        empty_box = SurroundingRectangle(empty_column, buff=0.12).set_stroke(ACTIVE_COLOR, 2.5)
        unknown = Text("?", font_size=44).set_color(ACTIVE_COLOR).move_to(get_output_point(3))
        with self.play_beat("why_feed_back") as beat:
            self.play(ShowCreation(empty_box), FadeIn(unknown, shift=0.2 * UP), run_time=beat.get_seconds_until(0.5))
            self.play(empty_box.animate.set_stroke(ACTIVE_COLOR, 5), rate_func=there_and_back, run_time=0.8)

        # Beat: blue becomes the next input, carried from the top back to the bottom
        path = get_return_path(2, 3)
        trail = path.copy().set_stroke(OUTPUT_COLOR, 2, opacity=0.5)
        input_box = SurroundingRectangle(blue_chip, buff=0.08).set_stroke(ACTIVE_COLOR, 2.5)
        with self.play_beat("blue_input") as beat:
            self.play(FadeOut(unknown), FadeOut(empty_box), run_time=0.4)
            self.play(MoveAlongPath(blue_chip, path), ShowCreation(trail), run_time=beat.get_seconds_until(0.85))
            input_box.move_to(blue_chip)
            self.play(ShowCreation(input_box), FadeOut(trail), run_time=0.5)

        # Beat: only blue is processed; earlier work already saved
        with self.play_beat("only_new") as beat:
            self.play(*dim(chips, opacity=0.3), run_time=beat.get_seconds_until(0.4))
            self.play(
                      *(get_pulse(grid.cells[(r, c)], KV_COLOR, 0.5) for r in range(3) for c in range(3)),
                      run_time=0.9)

        # Beat: in layer one, blue makes its own query, key and value
        qkv = Text("Q  K  V", font_size=22).set_color(ACTIVE_COLOR)
        with self.play_beat("query") as beat:
            self.play(grid.change(0, 3, "active"), run_time=0.6)
            qkv.move_to(grid.cells[(0, 3)])
            self.play(FadeIn(qkv, scale=0.8), run_time=beat.get_seconds_until(0.8))

        # Beat: its query is compared with saved keys and its own, and takes from those values
        arrows = VGroup(get_look_arrow(3, 2, color=ACTIVE_COLOR), get_look_arrow(3, 1, color=ACTIVE_COLOR),
                        get_look_arrow(3, 0, color=ACTIVE_COLOR), get_self_loop(3, color=ACTIVE_COLOR))
        with self.play_beat("match_cache") as beat:
            self.play(*(ShowCreation(a.arc) for a in arrows), *(FadeIn(a.tip) for a in arrows),
                      run_time=beat.get_seconds_until(0.6))
            self.play(*(get_pulse(grid.cells[(0, c)], KV_COLOR, 0.8) for c in range(3)), run_time=0.8)

        # Beat: then its key and value join the cache
        with self.play_beat("append") as beat:
            self.play(FadeOut(arrows), FadeOut(qkv), grid.change(0, 3, "saved"), run_time=0.7)
            for r in (1, 2):
                self.play(grid.change(r, 3, "active"),
                          *(get_pulse(grid.cells[(r, c)], KV_COLOR, 0.6) for c in range(3)), run_time=0.45)
                self.play(grid.change(r, 3, "saved"), run_time=0.45)

        # Beat: old tokens aren't recomputed, but every step still reads the whole cache
        reads_label = get_note("each step reads all\nsaved keys and values", KV_COLOR, 26)
        reads_label.move_to([PANEL_X, 0.15, 0])
        with self.play_beat("still_work") as beat:
            self.play(FadeIn(reads_label), run_time=0.6)
            for r in range(3):
                self.play(LaggedStart(*(get_pulse(grid.cells[(r, c)], WHITE, 0.5) for c in range(4)), lag_ratio=0.2),
                          run_time=0.7)

        # Beat: at the top, blue scores the next token: "and"
        and_chip = get_output_chip("and").move_to(get_output_point(3))
        top = get_cell_center(2, 3) + (CELL_HEIGHT / 2) * UP
        up_arrow = Arrow(top, and_chip.get_bottom(), buff=0.06).set_stroke(GREY_A, 3)
        with self.play_beat("next_and") as beat:
            self.play(FadeOut(reads_label), GrowArrow(up_arrow), run_time=beat.get_seconds_until(0.6))
            self.play(FadeIn(and_chip, shift=0.2 * UP), run_time=0.6)

        # Beat: one token in, one token out: one decode step
        step_label = Text("DECODE step 1", font_size=34).set_color(WHITE).move_to([PANEL_X, 2.25, 0])
        step_sub = get_note("1 token in → 1 token out", GREY_A, 24).next_to(step_label, DOWN, buff=0.15)
        with self.play_beat("decode_name") as beat:
            self.play(FadeOut(up_arrow), Write(step_label), FadeIn(step_sub), run_time=beat.get_seconds_until(0.8))

        # Beat: again: "and" goes in, reads the cache, adds its key and value, gives "clear"
        new_column = grid.build_column(4, "empty")
        path2 = get_return_path(3, 4)
        trail2 = path2.copy().set_stroke(OUTPUT_COLOR, 2, opacity=0.5)
        step2_label = Text("DECODE step 2", font_size=34).set_color(WHITE).move_to(step_label)
        clear_chip = get_output_chip("clear").move_to(get_output_point(4))
        with self.play_beat("step_two") as beat:
            self.play(FadeIn(new_column), FadeOut(input_box), *dim(blue_chip, opacity=0.45),
                      FadeTransform(step_label, step2_label), run_time=0.6)
            self.play(MoveAlongPath(and_chip, path2), ShowCreation(trail2), run_time=1.4)
            input_box2 = SurroundingRectangle(and_chip, buff=0.08).set_stroke(ACTIVE_COLOR, 2.5)
            self.play(FadeOut(trail2), ShowCreation(input_box2), run_time=0.4)
            self.run_column(grid, 4, run_time=2.0)
            self.play(FadeIn(clear_chip, shift=0.2 * UP), run_time=0.6)

        # Beat: step two couldn't start until step one produced "and"
        c_blue, c_and, c_clear = (get_output_chip(t) for t in ("blue", "and", "clear"))
        chain = VGroup(c_blue, c_and, c_clear).arrange(DOWN, buff=0.85).move_to([3.9, 0.35, 0])
        down1 = Arrow(c_blue.get_bottom(), c_and.get_top(), buff=0.08).set_stroke(GREY_A, 3)
        down2 = Arrow(c_and.get_bottom(), c_clear.get_top(), buff=0.08).set_stroke(GREY_A, 3)
        tag1 = get_note("step 1", GREY_A, 22).next_to(down1, LEFT, buff=0.15)
        tag2 = get_note("step 2", GREY_A, 22).next_to(down2, LEFT, buff=0.15)
        and_box = SurroundingRectangle(c_and, buff=0.08).set_stroke(ACTIVE_COLOR, 2.5)
        and_note = get_note("output of step 1,\ninput of step 2", ACTIVE_COLOR, 22).next_to(and_box, RIGHT, buff=0.2)
        wait_note = get_note("waits for “and”", ACTIVE_COLOR, 22).next_to(down2, RIGHT, buff=0.2)
        chain_group = VGroup(chain, down1, down2, tag1, tag2)
        with self.play_beat("dependency") as beat:
            self.play(FadeOut(VGroup(step2_label, step_sub)), FadeIn(c_blue), run_time=0.6)
            self.play(GrowArrow(down1), FadeIn(tag1), FadeIn(c_and, shift=0.2 * DOWN), run_time=0.8)
            self.play(ShowCreation(and_box), FadeIn(and_note), run_time=0.6)
            self.play(GrowArrow(down2), FadeIn(tag2), FadeIn(wait_note), FadeIn(c_clear, shift=0.2 * DOWN),
                      run_time=beat.get_seconds_until(0.95))

        # Beat: each new token is the next step's input
        conclusion = get_conclusion("Each output is the next step's input.")
        with self.play_beat("dependency_conclusion") as beat:
            self.play(Write(conclusion), run_time=beat.get_seconds_until(0.7))
            self.play(FlashAround(and_box, color=ACTIVE_COLOR), run_time=0.8)

        # Beat: the GPU really is parallel; this chain of steps isn't
        old_guess = get_claim("whole answer at once?", tag="Your opening guess", width=3.4)
        old_guess.move_to([4.4, -2.45, 0])
        with self.play_beat("hook_payoff") as beat:
            self.play(FadeIn(old_guess), run_time=0.6)
            strike_claim(self, old_guess, run_time=beat.get_seconds_until(0.8) or 0.8)

        self.play(FadeOut(VGroup(question_line, grid.get_all(), chips, layer_labels, blue_chip, and_chip, clear_chip,
                                 input_box2, cache_label, chain_group, and_box, and_note, wait_note, conclusion, old_guess)))
