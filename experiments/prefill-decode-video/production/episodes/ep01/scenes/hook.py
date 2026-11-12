from explainer_studio.scene_kit import *

from shared.series import (OUTPUT_COLOR, PROMPT_COLOR, STRUCTURE_COLOR, get_note, get_output_chip,
                           get_prompt_chip)


class Hook(NarratedScene):
    def construct(self):
        prompt_chips = VGroup(*(get_prompt_chip(t) for t in ["The", "sky", "is"]))
        answer_chips = VGroup(*(get_output_chip(t) for t in ["blue", "and", "clear", "."]))
        row = VGroup(*prompt_chips, *answer_chips).arrange(RIGHT, buff=0.22).move_to(1.4 * UP)
        you = get_note("your prompt", PROMPT_COLOR, 24).next_to(prompt_chips, UP, buff=0.3)
        reply = get_note("the answer, streaming", OUTPUT_COLOR, 24).next_to(answer_chips, UP, buff=0.3)

        # Beat: the answer streams back one piece at a time
        with self.play_beat("stream") as beat:
            self.play(LaggedStartMap(FadeIn, prompt_chips, shift=0.2 * UP, lag_ratio=0.15), FadeIn(you),
                      run_time=1.2)
            self.play(FadeIn(reply), run_time=0.4)
            step = max(0.35, (beat.remaining_seconds - 0.2) / len(answer_chips))
            for chip in answer_chips:
                self.play(FadeIn(chip, shift=0.15 * RIGHT), run_time=min(0.4, step))
                self.wait(max(0.0, step - 0.4))

        # Beat: the GPU does thousands of calculations at once
        gpu_box = RoundedRectangle(width=7.0, height=2.6, corner_radius=0.2).set_stroke(STRUCTURE_COLOR, 2)
        gpu_box.move_to(1.7 * DOWN)
        gpu_label = Text("GPU", font_size=32).set_color(GREY_A).next_to(gpu_box, LEFT, buff=0.3)
        squares = VGroup(*(Square(0.22).set_stroke(GREY_C, 1).set_fill(GREY_D, 0.4) for _ in range(16 * 5)))
        squares.arrange_in_grid(5, 16, buff=0.14).move_to(gpu_box)
        with self.play_beat("gpu_parallel") as beat:
            self.play(FadeIn(gpu_box), FadeIn(gpu_label), FadeIn(squares, lag_ratio=0.01),
                      run_time=beat.get_seconds_until(0.4))
            for _ in range(2):
                self.play(squares.animate.set_fill(WHITE, 0.85), run_time=0.3)
                self.play(squares.animate.set_fill(GREY_D, 0.4), run_time=0.4)

        # Beat: why not the whole answer at once?
        whole = DashedVMobject(SurroundingRectangle(answer_chips, buff=0.12), num_dashes=40)
        whole.set_stroke(OUTPUT_COLOR, 2.5)
        whole_label = Text("whole answer at once?", font_size=30).set_color(OUTPUT_COLOR)
        whole_label.move_to(answer_chips)
        with self.play_beat("prediction") as beat:
            self.play(FadeOut(answer_chips), FadeOut(reply), run_time=0.6)
            self.play(ShowCreation(whole), Write(whole_label), run_time=1.2)
            self.play(squares.animate.set_fill(WHITE, 0.85), run_time=0.3)
            self.play(squares.animate.set_fill(GREY_D, 0.4), run_time=0.5)

        # Beat: follow one tiny request through
        with self.play_beat("promise") as beat:
            self.play(FadeOut(VGroup(gpu_box, gpu_label, squares, whole, whole_label)), run_time=0.8)
            self.play(VGroup(prompt_chips, you).animate.move_to(0.4 * UP), run_time=1.2)

        # Beat: a toy example, illustrative
        toy = get_note("Toy example: illustrative, not a measured model", GREY_B, 26)
        toy.next_to(prompt_chips, DOWN, buff=0.6)
        with self.play_beat("illustrative") as beat:
            self.play(FadeIn(toy, shift=0.1 * UP), run_time=beat.get_seconds_until(0.4))

        self.play(FadeOut(VGroup(prompt_chips, you, toy)))
