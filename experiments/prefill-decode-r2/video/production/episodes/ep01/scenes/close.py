from explainer_studio.scene_kit import *

from shared.series import ACTIVE_COLOR, ANSWER_COLOR, COLUMN_XS, INPUT_Y, PICK_Y, LABEL_SIZE, PROMPT_COLOR, STATES, Board, get_input_slot, get_state, get_top_line


class Close(NarratedScene):
    def construct(self) -> None:
        board = Board(get_state("cp_close"), show_kv=True)
        work = STATES["work"]

        # Beat: known tokens go together
        known = Text("known: together", font_size=LABEL_SIZE).set_color(PROMPT_COLOR).next_to(board.column(1), UP, buff=0.3)
        with self.play_beat("cl_known") as beat:
            self.play(FadeIn(board.everything()), run_time=beat.get_seconds_until(0.3))
            self.play(*(FlashAround(board.column(c), color=PROMPT_COLOR) for c in range(3)), FadeIn(known), run_time=beat.get_seconds_until(0.8))

        # Beat: picked tokens go one at a time
        picked = Text("picked: one at a time", font_size=LABEL_SIZE).set_color(ANSWER_COLOR).to_edge(UP, buff=0.45).shift(1.5 * RIGHT)
        with self.play_beat("cl_unknown") as beat:
            self.play(FlashAround(board.column(3), color=ANSWER_COLOR), run_time=beat.get_seconds_until(0.4))
            self.play(FlashAround(board.chips[4], color=ANSWER_COLOR), FadeIn(picked), run_time=beat.get_seconds_until(0.8))

        # Beat: transfer question: cache off before blue goes in
        off = get_top_line("cache off")
        marks = Text("?   ?", font_size=48).set_color(ACTIVE_COLOR).next_to(off, RIGHT, buff=0.5)
        waiting_slot=get_input_slot(3)
        with self.play_beat("cl_transfer_ask") as beat:
            self.play(FadeOut(VGroup(known,picked,board.chips[4],board.chips[3])),*(board.cell_to(l,3,"empty") for l in range(2)),run_time=0.25)
            board.chips[3].move_to([COLUMN_XS[3],PICK_Y,0])
            self.play(FadeIn(board.chips[3]),FadeIn(waiting_slot),run_time=0.3)
            self.play(FadeIn(off), *(board.cell_to(l, c, "cleared") for l in range(2) for c in range(3)), run_time=beat.get_seconds_until(0.6))
            self.play(FadeIn(marks), run_time=beat.get_seconds_until(0.9))

        # Beat: the reveal: rebuilt, same pick, more work
        count = Text(f"made: {work['decode_made_cache_off']} instead of {work['decode_made_cache_on']}", font_size=LABEL_SIZE)
        same = Text(f"pick: {STATES['picks'][1]}, unchanged", font_size=LABEL_SIZE).set_color(ANSWER_COLOR)
        result = VGroup(count, same).arrange(RIGHT, buff=0.8).to_edge(UP, buff=0.45)
        feed_route=get_curved_arrow([COLUMN_XS[3],PICK_Y,0],[COLUMN_XS[3],INPUT_Y,0],angle=-PI/1.5,color=ANSWER_COLOR)
        with self.play_beat("cl_transfer_reveal") as beat:
            self.play(FadeOut(VGroup(off,marks,waiting_slot)),MoveAlongPath(board.chips[3],feed_route.arc),run_time=0.8)
            board.chips[3].move_to([COLUMN_XS[3],INPUT_Y,0])
            self.play(*(board.cell_to(l,3,"new") for l in range(2)),*(board.cell_to(l,c,"rebuilt") for l in range(2) for c in range(3)),run_time=beat.get_seconds_until(0.3))
            self.play(FadeIn(count), *(board.cell_to(l,c,"kv") for l in range(2) for c in range(4)),run_time=beat.get_seconds_until(0.6))
            self.play(FadeIn(same),FadeIn(board.chips[4]),run_time=beat.get_seconds_until(0.85))

        # Beat: reframe
        chips = board.chip_group()
        row = chips.copy().arrange(RIGHT, buff=0.3).move_to(0.6 * DOWN)
        sentence = Text("It can't read a word it hasn't chosen yet.", font_size=44).next_to(row, UP, buff=0.8)
        with self.play_beat("cl_reframe") as beat:
            self.play(FadeOut(VGroup(board.grid(), board.numbers, board.layer_labels, result)), run_time=beat.get_seconds_until(0.2))
            self.play(Transform(chips, row), run_time=beat.get_seconds_until(0.5))
            self.play(Write(sentence), run_time=beat.get_seconds_until(0.9))

        self.play(FadeOut(VGroup(chips, sentence)))
