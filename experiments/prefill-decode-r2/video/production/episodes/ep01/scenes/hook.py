from explainer_studio.scene_kit import *

from shared.series import COLUMN_XS, INPUT_Y, LABEL_SIZE, PROMPT_COLOR, ANSWER_COLOR, get_chip


class Hook(NarratedScene):
    def construct(self) -> None:
        prompt = VGroup(*(get_chip(w) for w in ["The", "sky", "is"])).arrange(RIGHT, buff=0.3)
        answer = VGroup(get_chip("blue", "answer"), get_chip("and", "answer")).arrange(RIGHT, buff=0.3)
        dots = Text("…", font_size=48).set_color(GREY_B)
        row = VGroup(prompt, answer, dots).arrange(RIGHT, buff=0.45).move_to(0.3 * UP)

        # Beat: the stream
        with self.play_beat("hook_stream") as beat:
            self.play(LaggedStartMap(FadeIn, prompt, shift=0.2 * UP, lag_ratio=0.15), run_time=beat.get_seconds_until(0.35))
            self.play(FadeIn(answer[0], shift=0.2 * LEFT), run_time=beat.get_seconds_until(0.6))
            self.play(FadeIn(answer[1], shift=0.2 * LEFT), run_time=beat.get_seconds_until(0.8))
            self.play(FadeIn(dots))

        # Beat: read together vs one at a time
        prompt_brace = Brace(prompt, DOWN, buff=0.2).set_color(PROMPT_COLOR)
        prompt_label = Text("read together", font_size=LABEL_SIZE).set_color(PROMPT_COLOR).next_to(prompt_brace, DOWN)
        answer_brace = Brace(answer, DOWN, buff=0.2).set_color(ANSWER_COLOR)
        answer_label = Text("one at a time", font_size=LABEL_SIZE).set_color(ANSWER_COLOR).next_to(answer_brace, DOWN)
        with self.play_beat("hook_question") as beat:
            self.play(GrowFromCenter(prompt_brace), FadeIn(prompt_label), run_time=beat.get_seconds_until(0.4))
            self.play(GrowFromCenter(answer_brace), FadeIn(answer_label), run_time=beat.get_seconds_until(0.8))

        # Beat: the guess, held through the pause
        slots = VGroup()
        for chip in answer:
            box = DashedVMobject(chip.box.copy().set_fill(opacity=0), num_dashes=18).set_stroke(ANSWER_COLOR, 2)
            mark = Text("?", font_size=40).set_color(ANSWER_COLOR).move_to(chip)
            slots.add(VGroup(box, mark))
        question = Text("Both in one trip?", font_size=48).set_color(WHITE).to_edge(UP, buff=0.8)
        with self.play_beat("hook_guess") as beat:
            self.play(FadeOut(VGroup(prompt_brace, prompt_label, answer_brace, answer_label, dots)),
                      FadeTransform(answer, slots), run_time=beat.get_seconds_until(0.3))
            self.play(Write(question), run_time=beat.get_seconds_until(0.7))

        # Beat: follow one request; prompt chips move to where the board will put them
        targets = VGroup(*(prompt[i].copy().move_to([COLUMN_XS[i], INPUT_Y, 0]) for i in range(3)))
        with self.play_beat("hook_follow") as beat:
            self.play(FadeOut(VGroup(question, slots)), run_time=beat.get_seconds_until(0.3))
            self.play(Transform(prompt, targets), run_time=beat.get_seconds_until(0.9))

        self.play(FadeOut(prompt))
