from explainer_studio.scene_kit import *

from shared.series import (ACTIVE_COLOR, KV_COLOR, MEMORY_COLOR, OUTPUT_COLOR, PROMPT_COLOR, STRUCTURE_COLOR,
                           get_chip, get_main_question_line, get_note, get_output_chip)


def get_mini_column(color, height: int = 3) -> VGroup:
    cells = VGroup(*(RoundedRectangle(width=0.5, height=0.3, corner_radius=0.05).set_fill(color, 0.5)
                     .set_stroke(color, 1.5) for _ in range(height)))
    return cells.arrange(UP, buff=0.08)


class WorkShape(NarratedScene):
    def construct(self):
        question_line = get_main_question_line()

        # Beat: one wide pass for the prompt, then a chain of small steps
        wide = VGroup(*(get_mini_column(PROMPT_COLOR) for _ in range(6))).arrange(RIGHT, buff=0.12)
        wide_label = get_note("prefill: one wide pass", PROMPT_COLOR, 28).next_to(wide, UP, buff=0.3)
        steps = VGroup(*(get_mini_column(OUTPUT_COLOR) for _ in range(4))).arrange(RIGHT, buff=0.5)
        step_arrows = VGroup(*(Arrow(steps[i].get_right(), steps[i + 1].get_left(), buff=0.06, stroke_width=2.5)
                               .set_stroke(GREY_A) for i in range(3)))
        chain = VGroup(steps, step_arrows)
        chain_label = get_note("decode: a chain of small steps", OUTPUT_COLOR, 28).next_to(chain, UP, buff=0.3)
        left_pic = VGroup(wide_label, wide).move_to([-3.4, 0.2, 0])
        right_pic = VGroup(chain_label, chain).move_to([3.4, 0.2, 0])
        with self.play_beat("seam_shape") as beat:
            self.play(FadeIn(question_line), FadeIn(left_pic, lag_ratio=0.05), run_time=beat.get_seconds_until(0.45))
            self.play(FadeIn(chain_label), LaggedStart(*(FadeIn(s) for s in steps), lag_ratio=0.5),
                      LaggedStart(*(GrowArrow(a) for a in step_arrows), lag_ratio=0.5),
                      run_time=beat.get_seconds_until(0.95))

        # Beat: each small step adds to your wait; what limits one step's speed?
        local_question = Text("What limits one step's speed?", font_size=34).set_color(ACTIVE_COLOR)
        local_question.move_to([0, -2.0, 0])
        with self.play_beat("shape_question") as beat:
            self.play(LaggedStart(*(Indicate(s, color=WHITE, scale_factor=1.15) for s in steps), lag_ratio=0.3),
                      run_time=beat.get_seconds_until(0.5))
            self.play(Write(local_question), run_time=beat.get_seconds_until(0.95))

        # Beat: weights and KV cache sit in memory, apart from the compute units
        gpu = RoundedRectangle(width=8.4, height=3.4, corner_radius=0.2).set_stroke(STRUCTURE_COLOR, 2)
        gpu.move_to([-2.0, 0.4, 0])
        gpu_label = get_note("GPU", GREY_A, 28).next_to(gpu, UP, buff=0.12).align_to(gpu, LEFT)
        memory = RoundedRectangle(width=2.8, height=2.4, corner_radius=0.12)
        memory.set_fill(MEMORY_COLOR, 0.25).set_stroke(MEMORY_COLOR, 2.5).move_to([-4.6, 0.4, 0])
        memory_text = VGroup(Text("GPU memory", font_size=28).set_color(WHITE),
                             Text("weights", font_size=26).set_color(GREY_A),
                             Text("+ KV cache", font_size=26).set_color(KV_COLOR)).arrange(DOWN, buff=0.15)
        memory_text.move_to(memory)
        compute = RoundedRectangle(width=3.2, height=2.4, corner_radius=0.12)
        compute.set_fill(GREY_E, 0.6).set_stroke(GREY_B, 2.5).move_to([0.3, 0.4, 0])
        compute_text = get_note("compute units", GREY_A, 26).next_to(compute.get_top(), DOWN, buff=0.2)
        local_small = Text("What limits one step's speed?", font_size=26).set_color(ACTIVE_COLOR)
        local_small.next_to(question_line, DOWN, buff=0.25)
        with self.play_beat("gpu_picture") as beat:
            self.play(FadeOut(left_pic), FadeOut(right_pic), Transform(local_question, local_small), run_time=0.8)
            self.play(FadeIn(gpu), FadeIn(gpu_label), FadeIn(memory), FadeIn(memory_text),
                      run_time=beat.get_seconds_until(0.55))
            self.play(FadeIn(compute), FadeIn(compute_text), run_time=0.8)

        # Beat: every pass they're read into the compute units; reading takes time too
        read_arrow = Arrow(memory.get_right(), compute.get_left(), buff=0.1, stroke_width=10)
        read_arrow.set_stroke(MEMORY_COLOR)
        read_label = get_note("read", MEMORY_COLOR, 26).next_to(read_arrow, UP, buff=0.1)

        def pulse_along(run_time=1.0):
            dot = Dot(read_arrow.get_start(), radius=0.12).set_fill(WHITE, 1)
            return MoveAlongPath(dot, Line(read_arrow.get_start(), read_arrow.get_end()), run_time=run_time,
                                 remover=True)

        with self.play_beat("read_cost") as beat:
            self.play(GrowArrow(read_arrow), FadeIn(read_label), run_time=beat.get_seconds_until(0.4))
            self.play(pulse_along(1.4))

        # Beat: in prefill each read serves many prompt tokens
        prefill_dots = VGroup(*(Dot(radius=0.13).set_fill(PROMPT_COLOR, 1) for _ in range(8)))
        prefill_dots.arrange_in_grid(2, 4, buff=0.28).move_to(compute.get_center() + 0.3 * DOWN)
        phase_label = get_note("prefill", PROMPT_COLOR, 30).move_to([4.6, 1.8, 0])
        with self.play_beat("prefill_shape") as beat:
            self.play(FadeIn(phase_label), pulse_along(0.9))
            self.play(LaggedStart(*(FadeIn(d, scale=0.5) for d in prefill_dots), lag_ratio=0.08),
                      run_time=beat.get_seconds_until(0.9))

        # Beat: a long prompt tends to keep compute busy
        meter_frame = Rectangle(width=3.2, height=0.32).set_stroke(GREY_B, 1.5).move_to([0.3, -1.85, 0])
        meter_fill = Rectangle(width=3.2, height=0.32).set_fill(PROMPT_COLOR, 0.8).set_stroke(width=0)
        meter_fill.stretch_to_fit_width(0.01).align_to(meter_frame, LEFT).match_y(meter_frame)
        meter_label = get_note("math per read", GREY_A, 24).next_to(meter_frame, LEFT, buff=0.25)
        busy = get_note("high", PROMPT_COLOR, 24).next_to(meter_frame, RIGHT, buff=0.2)
        with self.play_beat("prefill_busy") as beat:
            self.add(meter_fill)
            self.play(FadeIn(meter_frame), FadeIn(meter_label), run_time=0.5)
            self.play(meter_fill.animate.stretch_to_fit_width(2.9).align_to(meter_frame, LEFT), FadeIn(busy),
                      run_time=beat.get_seconds_until(0.9))

        # Beat: in decode, one request brings one new token per step
        decode_dot = Dot(radius=0.13).set_fill(OUTPUT_COLOR, 1).move_to(compute.get_center() + 0.3 * DOWN)
        decode_label = get_note("decode", OUTPUT_COLOR, 30).move_to(phase_label)
        with self.play_beat("decode_shape") as beat:
            self.play(FadeOut(prefill_dots), FadeOut(busy), FadeTransform(phase_label, decode_label),
                      meter_fill.animate.stretch_to_fit_width(0.01).align_to(meter_frame, LEFT), run_time=0.8)
            self.play(FadeIn(decode_dot, scale=0.5), run_time=beat.get_seconds_until(0.8))

        # Beat: in an ordinary model, that token still needs all the weights read, plus its cache
        same_read = get_note("same big read", MEMORY_COLOR, 24).next_to(read_arrow, DOWN, buff=0.12)
        with self.play_beat("whole_read") as beat:
            self.play(pulse_along(1.2), FadeIn(same_read), run_time=1.2)
            self.play(Indicate(memory_text, color=WHITE), run_time=beat.get_seconds_until(0.9))

        # Beat: little math per read; compute finishes fast, then waits
        low = get_note("low", OUTPUT_COLOR, 24).next_to(meter_frame, RIGHT, buff=0.2)
        meter_fill.set_fill(OUTPUT_COLOR, 0.8)
        idle = get_note("waiting…", GREY_B, 24).next_to(decode_dot, DOWN, buff=0.25)
        with self.play_beat("decode_little_math") as beat:
            self.play(meter_fill.animate.stretch_to_fit_width(0.4).align_to(meter_frame, LEFT), FadeIn(low),
                      run_time=0.8)
            self.play(Flash(decode_dot, color=OUTPUT_COLOR), run_time=0.5)
            self.play(compute.animate.set_fill(GREY_E, 0.2), FadeIn(idle), pulse_along(beat.remaining_seconds * 0.8
                                                                                        if beat.remaining_seconds > 1.5 else 1.2))

        # Beat: decode is often limited by memory reads: memory-bound
        bound = VGroup(Text("often limited by memory reads", font_size=28).set_color(WHITE),
                       Text("“memory-bound”", font_size=26).set_color(MEMORY_COLOR)).arrange(DOWN, buff=0.15)
        bound.move_to([4.6, 0.6, 0])
        with self.play_beat("decode_waiting") as beat:
            self.play(FadeIn(bound[0]), run_time=beat.get_seconds_until(0.5))
            self.play(FadeIn(bound[1]), run_time=0.6)

        # Beat: a real server answers many people at once
        requests = VGroup(*(get_chip(f"request {i}", OUTPUT_COLOR, font_size=24) for i in range(1, 5)))
        requests.arrange(DOWN, buff=0.18).move_to([3.9, -0.2, 0])
        with self.play_beat("many_users") as beat:
            self.play(FadeOut(bound), FadeOut(decode_label), FadeOut(idle), compute.animate.set_fill(GREY_E, 0.6),
                      run_time=0.6)
            self.play(LaggedStart(*(FadeIn(r, shift=0.2 * LEFT) for r in requests), lag_ratio=0.25),
                      run_time=beat.get_seconds_until(0.9))

        # Beat: bundling one decode step from each lets one read feed them all
        batch_dots = VGroup(*(Dot(radius=0.13).set_fill(OUTPUT_COLOR, 1) for _ in range(3)))
        targets = VGroup(decode_dot.copy(), *(d.copy() for d in batch_dots)).arrange(RIGHT, buff=0.3)
        targets.move_to(compute.get_center() + 0.3 * DOWN)
        own_cache = get_note("each still reads its own cache", KV_COLOR, 22).next_to(requests, DOWN, buff=0.2)
        with self.play_beat("batching") as beat:
            for d, r in zip(batch_dots, requests[1:]):
                d.move_to(r)
            self.play(decode_dot.animate.move_to(targets[0]),
                      *(d.animate.move_to(t) for d, t in zip(batch_dots, targets[1:])), run_time=1.2)
            self.play(pulse_along(0.9), meter_fill.animate.stretch_to_fit_width(1.3).align_to(meter_frame, LEFT),
                      FadeOut(low), run_time=beat.get_seconds_until(0.85))
            self.play(FadeIn(own_cache), run_time=0.5)

        # Beat: each read used better, but each answer still moves one step at a time
        chains = VGroup()
        for r in requests:
            boxes = VGroup(*(Square(0.22).set_fill(OUTPUT_COLOR, 0.7).set_stroke(OUTPUT_COLOR, 1) for _ in range(4)))
            boxes.arrange(RIGHT, buff=0.12).next_to(r, RIGHT, buff=0.3)
            chains.add(boxes)
        with self.play_beat("batching_chain") as beat:
            self.play(FadeOut(own_cache), run_time=0.3)
            for k in range(4):
                self.play(*(FadeIn(ch[k], scale=0.5) for ch in chains), run_time=min(0.6, beat.remaining_seconds / 5))

        # Beat: tendencies: cache length, batch size, model design and hardware shift the balance
        tend = Text("tendencies, not laws", font_size=30).set_color(WHITE).move_to([0, -2.75, 0])
        factors = VGroup(*(get_fact_chip(t, GREY_A, 24) for t in ["long cache", "batch size", "model design", "hardware"]))
        factors.arrange(RIGHT, buff=0.3).next_to(tend, DOWN, buff=0.2)
        with self.play_beat("caveat_list") as beat:
            self.play(FadeIn(tend), run_time=0.6)
            self.play(LaggedStart(*(FadeIn(f, shift=0.1 * UP) for f in factors), lag_ratio=0.25),
                      run_time=beat.get_seconds_until(0.9))

        self.play(FadeOut(VGroup(question_line, local_question, gpu, gpu_label, memory, memory_text, compute,
                                 compute_text, read_arrow, read_label, same_read, meter_frame, meter_fill, meter_label,
                                 decode_dot, batch_dots, requests, chains, tend, factors)))
