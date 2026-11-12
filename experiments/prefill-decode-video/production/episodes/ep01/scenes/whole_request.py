from explainer_studio.scene_kit import *

from shared.series import (ACTIVE_COLOR, KV_COLOR, OUTPUT_COLOR, PROMPT_COLOR, TokenGrid, get_conclusion,
                           get_input_point, get_layer_labels, get_main_question_line, get_note, get_output_chip,
                           get_output_point, get_prompt_chip, get_pulse, get_return_path)


def get_block(text: str, color, width: float, height: float = 0.8, font_size: float = 22) -> VGroup:
    box = RoundedRectangle(width=width, height=height, corner_radius=0.08).set_fill(color, 0.25).set_stroke(color, 2)
    if not text:
        return VGroup(box)
    label = Text(text, font_size=font_size).set_color(WHITE).move_to(box)
    return VGroup(box, label)


def get_bar_blocks(count: int, width: float, gap: float, height: float, color=OUTPUT_COLOR) -> VGroup:
    blocks = VGroup(*(Rectangle(width=width, height=height).set_fill(color, 0.8).set_stroke(width=0)
                      for _ in range(count)))
    return blocks.arrange(RIGHT, buff=gap)


class WholeRequest(NarratedScene):
    def construct(self):
        question_line = get_main_question_line()

        # Beat: here's the whole request
        prefill = get_block("prefill: The sky is → blue", PROMPT_COLOR, 3.6)
        steps = VGroup(*(get_block(t, OUTPUT_COLOR, 1.7, font_size=22)
                         for t in ["blue → and", "and → clear", "clear → .", ". → end"]))
        timeline = VGroup(prefill, *steps).arrange(RIGHT, buff=0.12).move_to([-0.5, 1.4, 0])
        time_arrow = Arrow(timeline.get_corner(DL) + 0.3 * DOWN, timeline.get_corner(DR) + 0.3 * DOWN + 0.6 * RIGHT,
                           buff=0, stroke_width=2).set_stroke(GREY_B)
        time_label = get_note("Step order · widths are illustrative", GREY_B, 22).next_to(time_arrow, DOWN, buff=0.18)
        with self.play_beat("rejoin") as beat:
            self.play(FadeIn(question_line), FadeIn(prefill, shift=0.2 * RIGHT), run_time=0.8)
            self.play(LaggedStart(*(FadeIn(s, shift=0.2 * RIGHT) for s in steps), lag_ratio=0.5),
                      GrowArrow(time_arrow), FadeIn(time_label), run_time=max(1.2, beat.remaining_seconds))

        # Beat: it stops at an end marker or a length limit; the last pick is never processed
        never = get_note("“end” is never fed back", OUTPUT_COLOR, 24).next_to(steps[-1], UP, buff=0.2)
        count = Text("5 picks = 1 from prefill + 4 decode steps", font_size=28).set_color(WHITE)
        count.move_to([-0.3, -0.2, 0])
        with self.play_beat("end_token") as beat:
            self.play(Indicate(steps[-1][1], color=OUTPUT_COLOR), FadeIn(never), run_time=beat.get_seconds_until(0.5))
            self.play(FadeIn(count, shift=0.1 * UP), run_time=0.8)

        # Beat: same prompt, same model; 10 tokens or 100
        row_y = (0.9, -0.7)
        row_labels = VGroup(get_note("10 tokens", WHITE, 28).move_to([-5.7, row_y[0], 0]),
                            get_note("100 tokens", WHITE, 28).move_to([-5.7, row_y[1], 0]))
        with self.play_beat("transfer_q") as beat:
            self.play(FadeOut(VGroup(timeline, time_arrow, time_label, never, count)), run_time=0.6)
            self.play(LaggedStart(*(FadeIn(l, shift=0.2 * RIGHT) for l in row_labels), lag_ratio=0.4),
                      run_time=beat.get_seconds_until(0.9))

        # Beat: what must grow? would the time grow ten times?
        card = get_question_card("What must grow?\nWould the time grow ten times?", width=6.0)
        card.move_to([0.6, -2.5, 0])
        with self.play_beat("transfer_ask") as beat:
            self.play(FadeIn(card, shift=0.1 * UP), run_time=beat.get_seconds_until(0.6))

        # Beat: prefill stays the same: still one pass over the prompt
        pre_blocks = VGroup(*(get_block("prefill", PROMPT_COLOR, 1.6, height=0.6, font_size=22) for _ in range(2)))
        for block, y in zip(pre_blocks, row_y):
            block.move_to([-3.85, y, 0])
        with self.play_beat("transfer_more_steps") as beat:
            self.play(FadeOut(card), run_time=0.5)
            self.play(LaggedStart(*(FadeIn(b, shift=0.2 * RIGHT) for b in pre_blocks), lag_ratio=0.3),
                      run_time=beat.get_seconds_until(0.8))

        # Beat: count every pick, the end marker included
        rule = get_note("count: every pick, end marker included", GREY_A, 26).move_to([0.5, -2.2, 0])
        with self.play_beat("count_rule") as beat:
            self.play(FadeIn(rule), run_time=beat.get_seconds_until(0.6))

        # Beat: first pick from prefill; 9 decode steps, and 99
        row1 = get_bar_blocks(9, 0.34, 0.06, 0.6).next_to(pre_blocks[0], RIGHT, buff=0.1)
        row2 = get_bar_blocks(99, 0.055, 0.032, 0.6).next_to(pre_blocks[1], RIGHT, buff=0.1)
        c1 = get_note("1 + 9", WHITE, 28).next_to(row1, RIGHT, buff=0.3)
        c2 = get_note("1 + 99", WHITE, 28).next_to(row2, UP, buff=0.15).align_to(row2, RIGHT)
        with self.play_beat("transfer_step_count") as beat:
            self.play(Indicate(pre_blocks[0][1], color=PROMPT_COLOR), Indicate(pre_blocks[1][1], color=PROMPT_COLOR),
                      run_time=beat.get_seconds_until(0.3))
            self.play(LaggedStart(*(FadeIn(b) for b in row1), lag_ratio=0.3), FadeIn(c1),
                      run_time=beat.get_seconds_until(0.6))
            self.play(LaggedStart(*(FadeIn(b) for b in row2), lag_ratio=0.05), FadeIn(c2),
                      run_time=max(1.0, beat.remaining_seconds))

        # Beat: ninety more steps, each waiting for the one before
        extra = VGroup(*row2[9:])
        extra_brace = Brace(extra, DOWN, buff=0.12)
        extra_label = get_note("+90 steps, in order", OUTPUT_COLOR, 26).next_to(extra_brace, DOWN, buff=0.1)
        with self.play_beat("transfer_sequential") as beat:
            self.play(FadeOut(rule), run_time=0.4)
            self.play(GrowFromCenter(extra_brace), FadeIn(extra_label), run_time=0.7)
            self.play(LaggedStart(*(Indicate(b, color=ACTIVE_COLOR, scale_factor=1.0) for b in extra), lag_ratio=0.02),
                      run_time=max(1.0, beat.remaining_seconds))

        # Beat: prefill is unchanged; no total-time ratio follows from that fact alone
        guess = get_claim("10x the time?", tag="Guess", width=3.0).move_to([4.3, -2.5, 0])
        prefill_note = get_note("prefill: unchanged", PROMPT_COLOR, 24).move_to([0.8, -2.5, 0])
        with self.play_beat("time_less") as beat:
            self.play(FadeIn(guess), run_time=0.6)
            self.play(*(Indicate(b[0], color=PROMPT_COLOR) for b in pre_blocks), run_time=beat.get_seconds_until(0.6))
            self.play(FadeIn(prefill_note), run_time=0.5)

        # Beat: a longer cache can change the cost of each later step
        late = VGroup(*row2[-30:])
        longer = get_note("longer cache to read", KV_COLOR, 24).next_to(late, UP, buff=0.15).align_to(row2, RIGHT)
        with self.play_beat("time_more") as beat:
            self.play(FadeOut(c2), late.animate.set_fill(KV_COLOR, 1), FadeIn(longer), run_time=beat.get_seconds_until(0.5))

        # Beat: more steps and a bigger cache are certain; exactly ten times, we can't say
        with self.play_beat("transfer_step_cost") as beat:
            self.play(FadeOut(VGroup(prefill_note, extra_brace, extra_label)), run_time=beat.get_seconds_until(0.4))
            verdict = strike_claim(self, guess, "Certain: more steps, bigger cache.\nExact time: depends.",
                                   direction=LEFT, run_time=1.4)

        # Beat: without a cache, a simple version would redo old tokens' work every step
        everything = VGroup(row_labels, pre_blocks, row1, row2, c1, longer, guess, verdict)
        hypo_title = get_note("Hypothetical: no cache", ACTIVE_COLOR, 28)
        hypo_rows = VGroup()
        for k in range(3):
            old = VGroup(*(Square(0.36).set_fill(GREY_C, 0.6).set_stroke(GREY_B, 1) for _ in range(3 + k)))
            old.arrange(RIGHT, buff=0.06)
            new = Square(0.36).set_fill(OUTPUT_COLOR, 0.9).set_stroke(OUTPUT_COLOR, 1).next_to(old, RIGHT, buff=0.12)
            tag = get_note(f"step {k + 1}", GREY_A, 22).next_to(old, LEFT, buff=0.3)
            hypo_rows.add(VGroup(tag, old, new))
        hypo_rows.arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        redo = get_note("grey = old tokens' work, redone", GREY_A, 22)
        hypo = VGroup(hypo_title, hypo_rows, redo).arrange(DOWN, aligned_edge=LEFT, buff=0.35).move_to([-3.4, 0.3, 0])
        with self.play_beat("no_cache_baseline") as beat:
            self.play(FadeOut(everything), run_time=0.6)
            self.play(FadeIn(hypo_title), run_time=0.4)
            self.play(LaggedStart(*(FadeIn(r, shift=0.1 * DOWN) for r in hypo_rows), lag_ratio=0.4), FadeIn(redo),
                      run_time=max(1.0, beat.remaining_seconds))

        # Beat: the cache removes that repeat, not the wait for the previous token
        cache_title = get_note("With a KV cache", KV_COLOR, 28)
        cache_rows = VGroup()
        for k in range(3):
            new = Square(0.36).set_fill(OUTPUT_COLOR, 0.9).set_stroke(OUTPUT_COLOR, 1)
            tag = get_note(f"step {k + 1}", GREY_A, 22).next_to(new, LEFT, buff=0.3)
            cache_rows.add(VGroup(tag, new))
        cache_rows.arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        waits = VGroup(*(Arrow(cache_rows[k][1].get_bottom(), cache_rows[k + 1][1].get_top(), buff=0.04,
                               stroke_width=3).set_stroke(ACTIVE_COLOR) for k in range(2)))
        wait_note = get_note("still waits for\nthe previous token", ACTIVE_COLOR, 22)
        wait_note.next_to(cache_rows, RIGHT, buff=0.5)
        cached = VGroup(cache_title, VGroup(cache_rows, waits, wait_note)).arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        cached.match_y(hypo).set_x(3.2)
        limit = get_conclusion("Cache: no repeated past work. Still: wait for the previous token.", font_size=28)
        with self.play_beat("cache_limit") as beat:
            self.play(*dim(hypo, opacity=0.3), FadeIn(cache_title), FadeIn(cache_rows), run_time=0.8)
            self.play(*(GrowArrow(w) for w in waits), FadeIn(wait_note), run_time=0.8)
            self.play(Write(limit), run_time=max(0.8, beat.get_seconds_until(0.95)))

        # Beat: speculative decoding drafts and checks; another day
        scope = VGroup(get_note("Not covered here:", GREY_B, 28),
                       get_note("speculative decoding (draft a few tokens, then check),", GREY_B, 26),
                       get_note("other model architectures", GREY_B, 26)).arrange(DOWN, buff=0.15)
        with self.play_beat("scope") as beat:
            self.play(FadeOut(VGroup(hypo, cached, limit)), run_time=0.6)
            self.play(FadeIn(scope), run_time=beat.get_seconds_until(0.5))

        # Beat: the prompt goes through together because it's already known
        grid = TokenGrid()
        columns = VGroup(*(grid.build_column(c, "empty") for c in range(3)))
        empty3 = grid.build_column(3, "empty")
        chips = VGroup(*(get_prompt_chip(w).move_to(get_input_point(i)) for i, w in enumerate(["The", "sky", "is"])))
        layer_labels = get_layer_labels()
        with self.play_beat("reframe_known") as beat:
            self.play(FadeOut(scope), run_time=0.5)
            self.play(FadeIn(VGroup(columns, empty3, chips, layer_labels)), run_time=0.8)
            for r in range(3):
                self.play(*(grid.change(r, c, "saved") for c in range(3)), run_time=0.45)

        # Beat: the answer comes one token at a time because each token is the next input
        blue = get_output_chip("blue").move_to(get_output_point(2))
        path = get_return_path(2, 3)
        final = get_conclusion("Known prompt: together.  Each answer token: the next input.", font_size=30)
        with self.play_beat("reframe_chain") as beat:
            self.play(FadeIn(blue, shift=0.2 * UP), run_time=0.6)
            self.play(MoveAlongPath(blue, path), run_time=1.6)
            self.play(Write(final), run_time=beat.get_seconds_until(0.95) or 0.8)

        self.play(FadeOut(VGroup(question_line, grid.get_all(), chips, layer_labels, blue, final)))
