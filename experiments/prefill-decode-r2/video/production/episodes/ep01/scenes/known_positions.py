from explainer_studio.scene_kit import *

from shared.series import ACTIVE_COLOR, LABEL_SIZE, PROMPT_COLOR, STATES, COLUMN_XS, INPUT_Y, ROW_YS, CELL_H, Board, get_blocked, get_reads, get_state, get_top_line


class KnownPositions(NarratedScene):
    def construct(self) -> None:
        fmt=lambda v:"["+", ".join(f"{n:.2f}" for n in v)+"]"
        board = Board(get_state("cp_prompt"), show_kv=False)
        chips = board.chip_group()
        note = Text("token pieces are illustrative", font_size=24).set_color(GREY_B).to_corner(DR, buff=0.5)

        # Beat: tokens and positions
        with self.play_beat("kp_tokens") as beat:
            self.play(FadeIn(chips), run_time=beat.get_seconds_until(0.4))
            self.play(LaggedStartMap(FadeIn, board.numbers, lag_ratio=0.3), FadeIn(note), run_time=beat.get_seconds_until(0.9))

        # Beat: a list of numbers per token, all at once
        lists = VGroup()
        for chip,numbers in zip(chips,STATES["prompt_inputs"]):
            lists.add(Text(fmt(numbers),font_size=24).set_color(PROMPT_COLOR).next_to(chip,UP,buff=0.25))
        with self.play_beat("kp_numbers") as beat:
            self.play(FadeIn(lists, shift=0.15 * UP), run_time=beat.get_seconds_until(0.5))

        # Beat: the stack of layers
        example=STATES["layer_example"]
        fmt=lambda v:"["+", ".join(f"{n:.2f}" for n in v)+"]"
        transform_example=VGroup(Text("is input  "+fmt(example["input"]),font_size=26),Text("↓ one transformation",font_size=26).set_color(ACTIVE_COLOR),Text("output  "+fmt(example["output"]),font_size=26)).arrange(DOWN,buff=0.3).move_to([3.1,0.3,0])
        with self.play_beat("kp_layers") as beat:
            self.play(FadeOut(lists), run_time=beat.get_seconds_until(0.2))
            self.play(FadeIn(transform_example),LaggedStartMap(FadeIn, board.grid(), lag_ratio=0.08), FadeIn(board.layer_labels),
                      run_time=beat.get_seconds_until(0.7))

        # Beat: causal look-back, then the forbidden look ahead
        reads = VGroup(*(Arrow([COLUMN_XS[c],INPUT_Y+0.44,0],[COLUMN_XS[2],ROW_YS[0]-CELL_H/2-0.04,0],buff=0.03,thickness=2).set_color(GREY_B) for c in range(3)))
        forbidden=DashedLine([COLUMN_XS[2],INPUT_Y+0.44,0],[COLUMN_XS[1],ROW_YS[0]-CELL_H/2-0.04,0],dash_length=0.08).set_color("#E06C5F")
        stop=Text("×",font_size=34).set_color("#E06C5F").move_to(forbidden.get_center())
        note_inputs=VGroup(Text("Read the layer's inputs",font_size=26),Text("not neighbors' new outputs",font_size=24)).arrange(DOWN,buff=0.16).move_to([3.1,0.4,0])
        blocked=VGroup(forbidden,stop,note_inputs)
        with self.play_beat("kp_lookback") as beat:
            self.play(FadeOut(transform_example),LaggedStartMap(ShowCreation, reads, lag_ratio=0.3), run_time=beat.get_seconds_until(0.45))
            self.play(ShowCreation(blocked[0]), FadeIn(blocked[1:]), run_time=beat.get_seconds_until(0.75))

        # Beat: a layer's two jobs
        example=STATES["layer_example"]
        fmt=lambda v:"["+", ".join(f"{n:.2f}" for n in v)+"]"
        jobs=VGroup(
            Text("is · layer 1 · toy numbers",font_size=26).set_color(PROMPT_COLOR),
            Text("input  "+fmt(example["input"]),font_size=26),
            Text("after attention block",font_size=24).set_color(ACTIVE_COLOR),
            Text(fmt(example["mixed"]),font_size=26),
            Text("after feed-forward block",font_size=24).set_color(ACTIVE_COLOR),
            Text(fmt(example["output"]),font_size=26),
        ).arrange(DOWN,aligned_edge=LEFT,buff=0.19).move_to([3.2,0.2,0])
        with self.play_beat("kp_two_jobs") as beat:
            self.play(FadeOut(VGroup(reads,blocked)),FadeIn(jobs[:2]),run_time=beat.get_seconds_until(0.15))
            self.play(FadeIn(jobs[2:4]),run_time=beat.get_seconds_until(0.5))
        with self.play_beat("kp_ffn") as beat:
            self.play(FadeIn(jobs[4:]),run_time=beat.get_seconds_until(0.8))

        # Beat: all known positions through layer 1 together, then layer 2
        line = get_top_line("known → processed together")
        with self.play_beat("kp_together") as beat:
            self.play(FadeOut(jobs), run_time=0.5)
            for layer in range(2):
                self.play(*(board.cell_to(layer, c, "new") for c in range(3)), run_time=beat.get_seconds_until(0.25 + 0.3 * layer))
                self.play(*(board.cell_to(layer, c, "processed") for c in range(3)), run_time=0.5)
            self.play(FadeIn(line))

        prefill_name = get_top_line("Prefill: process the known prompt")
        with self.play_beat("kp_prefill_name") as beat:
            self.play(FadeOut(line),run_time=0.18)
            self.play(FadeIn(prefill_name),run_time=0.4)
        self.play(FadeOut(prefill_name),run_time=0.3)

        self.play(FadeOut(VGroup(board.everything(), note)))
