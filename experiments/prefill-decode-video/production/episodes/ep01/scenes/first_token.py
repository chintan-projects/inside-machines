from explainer_studio.scene_kit import *

from shared.series import (ACTIVE_COLOR, CELL_HEIGHT, COLUMN_XS, KV_COLOR, OUTPUT_COLOR, OUTPUT_Y, ROW_YS,
                           TokenGrid, get_cell_center, get_input_point, get_layer_labels, get_look_arrow,
                           get_main_question_line, get_note, get_output_chip, get_output_point, get_prompt_chip,
                           get_score_panel, get_self_loop)

WORDS = ["The", "sky", "is"]
PANEL_X = 4.55


def get_slot(letter: str, text: str, width: float = 3.7) -> Parts:
    box = RoundedRectangle(width=width, height=0.62, corner_radius=0.1).set_stroke(GREY_C, 1.5)
    tag = Text(letter, font_size=30).set_color(GREY_B)
    label = Text(text, font_size=24).set_color(GREY_B)
    tag.move_to(box.get_left() + 0.35 * RIGHT)
    label.next_to(tag, RIGHT, buff=0.3)
    slot = Parts(box, tag, label)
    slot.box, slot.tag, slot.label = box, tag, label
    return slot


class FirstToken(NarratedScene):
    def construct(self):
        question_line = get_main_question_line()
        grid = TokenGrid()
        columns = VGroup(*(grid.build_column(c, "processed") for c in range(3)))
        chips = VGroup(*(get_prompt_chip(w).move_to(get_input_point(i)) for i, w in enumerate(WORDS)))
        layer_labels = get_layer_labels()
        question_mark = Text("?", font_size=48).set_color(GREY_A).move_to(get_output_point(1))

        # Beat: where does the answer begin?
        with self.play_beat("seam") as beat:
            self.play(FadeIn(VGroup(question_line, columns, chips, layer_labels)), run_time=0.8)
            self.play(FadeIn(question_mark, shift=0.2 * UP), run_time=beat.get_seconds_until(0.8))

        # Beat: only the last token has gathered from the whole prompt
        last_box = SurroundingRectangle(VGroup(grid.get_column(2), chips[2]), buff=0.12)
        last_box.set_stroke(ACTIVE_COLOR, 2.5)
        gather = VGroup(get_look_arrow(2, 1), get_look_arrow(2, 0), get_self_loop(2))
        with self.play_beat("why_last") as beat:
            self.play(FadeOut(question_mark), ShowCreation(last_box), run_time=0.8)
            self.play(*(ShowCreation(a.arc) for a in gather), *(FadeIn(a.tip) for a in gather),
                      run_time=beat.get_seconds_until(0.8))

        # Beat: its final-layer result becomes a score for each possible next token
        panel = get_score_panel([("blue", 0.62), ("clear", 0.22), ("gray", 0.12)])
        panel.move_to([PANEL_X, 1.4, 0])
        top = get_cell_center(2, 2) + (CELL_HEIGHT / 2) * UP
        to_panel = Arrow(top, panel.get_left() + 0.1 * LEFT, buff=0.1, path_arc=-PI / 4).set_stroke(GREY_A, 3)
        with self.play_beat("last_position") as beat:
            self.play(FadeOut(gather), run_time=0.4)
            self.play(GrowArrow(to_panel), run_time=0.8)
            self.play(FadeIn(panel.title), LaggedStart(*(GrowFromEdge(b, LEFT) for b in panel.bars), lag_ratio=0.2),
                      FadeIn(panel.labels), run_time=beat.get_seconds_until(0.95))

        # Beat: one gets picked: blue, from this same pass
        blue_chip = get_output_chip("blue").move_to(get_output_point(2))
        one_pass = Brace(chips, DOWN, buff=0.15)
        one_pass_label = get_note("one pass", GREY_A, 24).next_to(one_pass, DOWN, buff=0.1)
        with self.play_beat("pick_blue") as beat:
            self.play(panel.bars[0].animate.set_fill(OUTPUT_COLOR, 1), panel.labels[0].animate.set_color(OUTPUT_COLOR),
                      run_time=0.6)
            self.play(TransformFromCopy(panel.labels[0], blue_chip), run_time=beat.get_seconds_until(0.55))
            self.play(FadeOut(panel), FadeOut(to_panel), FadeOut(last_box), run_time=0.5)
            self.play(GrowFromCenter(one_pass), FadeIn(one_pass_label), run_time=0.6)

        # Beat: what from this pass can later steps reuse? Look inside a layer.
        sky_cell = grid.cells[(0, 1)]
        zoom = VGroup(
            get_slot("Q", "query: what it looks for"),
            get_slot("K", "key: what it offers to match"),
            get_slot("V", "value: what it hands over"),
        ).arrange(DOWN, buff=0.18)
        zoom_title = get_note("inside one cell: layer 1, “sky”", GREY_A, 24)
        zoom_frame = SurroundingRectangle(zoom, buff=0.25).set_stroke(GREY_B, 1.5).round_corners(0.12)
        zoom_group = VGroup(zoom_frame, zoom)
        zoom_title.next_to(zoom_frame, UP, buff=0.15)
        VGroup(zoom_group, zoom_title).move_to([PANEL_X, 0.2, 0])
        for slot in zoom:
            slot.label.set_opacity(0)
            slot.tag.set_opacity(0.4)
        zoom_line = DashedLine(sky_cell.get_right(), zoom_frame.get_left(), dash_length=0.08).set_stroke(GREY_C, 1.5)
        with self.play_beat("reuse_question") as beat:
            self.play(FadeOut(one_pass), FadeOut(one_pass_label), run_time=0.4)
            self.play(ShowCreation(zoom_line), FadeIn(zoom_group), FadeIn(zoom_title),
                      sky_cell.animate.set_stroke(WHITE, 4), run_time=beat.get_seconds_until(0.9))

        # Beat: a query: what it's looking for
        with self.play_beat("kv_link") as beat:
            q = zoom[0]
            self.play(q.box.animate.set_stroke(ACTIVE_COLOR, 2.5).set_fill(ACTIVE_COLOR, 0.12),
                      q.tag.animate.set_opacity(1).set_color(ACTIVE_COLOR),
                      q.label.animate.set_opacity(1).set_color(WHITE), run_time=beat.get_seconds_until(0.6))

        # Beat: a key and a value
        with self.play_beat("key_value") as beat:
            for i, fraction in ((1, 0.45), (2, 0.95)):
                slot = zoom[i]
                self.play(slot.box.animate.set_stroke(KV_COLOR, 2.5).set_fill(KV_COLOR, 0.18),
                          slot.tag.animate.set_opacity(1).set_color(KV_COLOR),
                          slot.label.animate.set_opacity(1).set_color(WHITE), run_time=beat.get_seconds_until(fraction))

        # Beat: gathering = comparing your query with earlier keys, and your own
        q_tag = Text("Q", font_size=26).set_color(ACTIVE_COLOR).move_to(grid.cells[(0, 2)])
        match_arrows = VGroup(get_look_arrow(2, 1, color=ACTIVE_COLOR), get_look_arrow(2, 0, color=ACTIVE_COLOR),
                              get_self_loop(2, color=ACTIVE_COLOR))
        with self.play_beat("match_rule") as beat:
            self.play(*dim(zoom_group, zoom_title, opacity=0.3), FadeOut(zoom_line),
                      sky_cell.animate.set_stroke(WHITE, 2), FadeIn(q_tag), run_time=0.7)
            self.play(*(ShowCreation(a.arc) for a in match_arrows), *(FadeIn(a.tip) for a in match_arrows),
                      run_time=beat.get_seconds_until(0.9))

        # Beat: say the query of "is" matches the key of "sky"; "is" takes much of its value
        strong = get_look_arrow(2, 1, color=ACTIVE_COLOR, stroke_width=7)
        strong_label = get_note("strong match (illustrative)", ACTIVE_COLOR, 24)
        strong_label.move_to([COLUMN_XS[2] + 2.3, -1.45, 0])
        start = get_cell_center(0, 1) + (CELL_HEIGHT / 2 + 0.04) * DOWN
        end = get_cell_center(0, 2) + (CELL_HEIGHT / 2 + 0.04) * DOWN
        value_path = ArcBetweenPoints(start, end, angle=PI / 2.6).set_stroke(opacity=0)
        value_dot = Dot(start, radius=0.11).set_fill(KV_COLOR, 1)
        with self.play_beat("kv_example") as beat:
            self.play(FadeTransform(match_arrows[0], strong), FadeIn(strong_label),
                      run_time=beat.get_seconds_until(0.5))
            self.add(value_path)
            self.play(FadeIn(value_dot, scale=0.5), run_time=0.3)
            self.play(MoveAlongPath(value_dot, value_path), run_time=1.2)
            self.play(FadeOut(value_dot), run_time=0.3)

        # Beat: keys and values depend only on itself and earlier tokens; nothing later changes them
        with self.play_beat("never_change") as beat:
            self.play(FadeOut(VGroup(strong, strong_label, match_arrows[1], match_arrows[2], q_tag, value_path)),
                      run_time=0.5)
            for r in range(3):
                self.play(*(grid.change(r, c, "saved") for c in range(3)), run_time=0.6)

        # Beat: later tokens will compare their queries with these keys and take these values
        ghost_box = DashedVMobject(RoundedRectangle(width=2.2, height=0.62, corner_radius=0.14), num_dashes=24)
        ghost_box.set_stroke(OUTPUT_COLOR, 2)
        ghost_label = get_note("a later token", OUTPUT_COLOR, 24).move_to(ghost_box)
        ghost = VGroup(ghost_box, ghost_label).move_to([PANEL_X, -2.2, 0])
        ghost_arrow = DashedLine(ghost.get_left(), grid.cells[(0, 2)].get_right() + 0.1 * RIGHT + 0.0 * DOWN,
                                 dash_length=0.1).set_stroke(OUTPUT_COLOR, 2)
        ghost_tip = ArrowTip().set_fill(OUTPUT_COLOR, 1).scale(0.6)
        ghost_tip.rotate(angle_of_vector(ghost_arrow.get_end() - ghost_arrow.get_start()) - ghost_tip.get_angle())
        ghost_tip.move_to(ghost_arrow.get_end())
        with self.play_beat("why_keep") as beat:
            self.play(FadeIn(ghost), run_time=0.6)
            self.play(ShowCreation(ghost_arrow), FadeIn(ghost_tip), run_time=beat.get_seconds_until(0.7))

        # Beat: old queries are never needed again; the kept keys and values are the KV cache
        cache_box = SurroundingRectangle(VGroup(*(grid.cells[(r, c)] for r in range(3) for c in range(3))), buff=0.15)
        cache_box.set_stroke(KV_COLOR, 2.5)
        cache_label = get_note("KV cache (saved)", KV_COLOR, 30)
        cache_label.next_to(cache_box, UP, buff=0.12).align_to(cache_box, LEFT)
        with self.play_beat("saved") as beat:
            self.play(*undim(zoom_group, zoom_title), run_time=0.4)
            self.play(zoom[0].animate.set_opacity(0.15), run_time=beat.get_seconds_until(0.35))
            self.play(FadeOut(VGroup(zoom_group, zoom_title, ghost, ghost_arrow, ghost_tip)), run_time=0.5)
            self.play(ShowCreation(cache_box), FadeIn(cache_label), run_time=beat.get_seconds_until(0.95))

        # Beat: "cache" might suggest stored answers
        claim = get_claim("The cache holds answers", tag="Intuition", width=3.6)
        claim.move_to([PANEL_X, 0.6, 0])
        with self.play_beat("cache_misread") as beat:
            self.play(FadeIn(claim, shift=0.1 * LEFT), run_time=beat.get_seconds_until(0.6))

        # Beat: each cell is one token's key and value in one layer; no answers, no weights
        with self.play_beat("cache_truth") as beat:
            self.play(Indicate(cache_label), run_time=beat.get_seconds_until(0.4))
            replacement = strike_claim(self, claim, "Saved: keys and values\nof processed tokens", run_time=1.4)

        # Beat: "blue" has no cells yet: picked, not processed
        empty_column = grid.build_column(3, "empty")
        empty_box = SurroundingRectangle(empty_column, buff=0.12).set_stroke(ACTIVE_COLOR, 2.5)
        empty_label = get_note("no cells yet", ACTIVE_COLOR, 24).next_to(empty_box, DOWN, buff=0.15)
        with self.play_beat("blue_empty") as beat:
            self.play(FadeOut(claim), FadeOut(replacement), run_time=0.5)
            self.play(FadeIn(empty_column), Indicate(blue_chip.label), run_time=beat.get_seconds_until(0.5))
            self.play(ShowCreation(empty_box), FadeIn(empty_label), run_time=0.7)

        # Beat: this first pass is called prefill
        prefill_brace = Brace(chips, DOWN, buff=0.15)
        prefill_label = Text("PREFILL", font_size=36).set_color(WHITE).next_to(prefill_brace, DOWN, buff=0.1)
        prefill_note = get_note("prompt in · first token out · cache filled", GREY_A, 24)
        prefill_note.next_to(prefill_label, RIGHT, buff=0.5)
        with self.play_beat("prefill_name") as beat:
            self.play(FadeOut(empty_box), FadeOut(empty_label), run_time=0.4)
            self.play(GrowFromCenter(prefill_brace), Write(prefill_label), run_time=beat.get_seconds_until(0.85))
            self.play(FadeIn(prefill_note), run_time=0.6)

        self.play(FadeOut(VGroup(question_line, grid.get_all(), chips, layer_labels, blue_chip, cache_box, cache_label,
                                 prefill_brace, prefill_label, prefill_note)))
