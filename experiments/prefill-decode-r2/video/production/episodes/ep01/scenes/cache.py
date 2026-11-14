from explainer_studio.scene_kit import *

from shared.series import (ACTIVE_COLOR, COLUMN_XS, KV_COLOR, LABEL_SIZE, PICK_Y, STATES, Board, get_cell, get_chip,
                           get_reads, get_state, get_top_line)


class Cache(NarratedScene):
    def construct(self) -> None:
        board = Board(get_state("cp_close"), show_kv=True, columns=4)
        and_chip = get_chip("and", "answer").move_to([COLUMN_XS[4], PICK_Y, 0])
        labels = VGroup()
        for layer in range(2):
            row = board.row(layer, range(4))
            brace = Brace(row, RIGHT, buff=0.15).set_color(KV_COLOR)
            text = Text(f"layer {layer + 1} cache", font_size=26).set_color(KV_COLOR).next_to(brace, RIGHT, buff=0.1)
            labels.add(VGroup(brace, text))
        work = STATES["work"]

        # Beat: the KV cache, one per layer
        with self.play_beat("kv_name") as beat:
            self.play(FadeIn(board.everything()), FadeIn(and_chip), run_time=beat.get_seconds_until(0.3))
            self.play(LaggedStartMap(FadeIn, labels, lag_ratio=0.3), run_time=beat.get_seconds_until(0.8))

        # Beat: what it saved on blue's trip
        made = Text(f"made: {work['decode_made_cache_on']}", font_size=LABEL_SIZE).set_color(ACTIVE_COLOR)
        read = Text(f"read from cache: {work['decode_reused_cache_on']}", font_size=LABEL_SIZE).set_color(KV_COLOR)
        counts = VGroup(made, read).arrange(RIGHT, buff=0.8).to_edge(UP, buff=0.45)
        with self.play_beat("kv_saves") as beat:
            self.play(FadeOut(labels), *(board.cell_to(l, 3, "new") for l in range(2)), FadeIn(made), run_time=beat.get_seconds_until(0.45))
            self.play(*(board.cell_to(l, c, "reused") for l in range(2) for c in range(3)), FadeIn(read), run_time=beat.get_seconds_until(0.9))

        # Beat: the reading still happens
        reads = get_reads(get_state("cp_cache"))
        with self.play_beat("kv_still_reads") as beat:
            self.play(LaggedStartMap(ShowCreation, reads, lag_ratio=0.25), run_time=beat.get_seconds_until(0.8))

        # Beat: what the cache is not
        crossed = VGroup()
        for word in ["stored answers", "the model"]:
            t = Text(word, font_size=LABEL_SIZE).set_color(GREY_B)
            crossed.add(VGroup(t, Line(t.get_left(), t.get_right()).set_stroke(GREY_B, 3)))
        keeps = Text("old keys and values", font_size=LABEL_SIZE).set_color(KV_COLOR)
        not_row = VGroup(*crossed, keeps).arrange(RIGHT, buff=0.7).to_edge(UP, buff=0.45)
        with self.play_beat("kv_not") as beat:
            self.play(FadeOut(VGroup(reads, counts)), *(board.cell_to(l, c, "kv") for l in range(2) for c in range(4)),
                      run_time=beat.get_seconds_until(0.2))
            self.play(FadeIn(crossed, lag_ratio=0.3), run_time=beat.get_seconds_until(0.5))
            self.play(FadeIn(keeps), run_time=beat.get_seconds_until(0.85))

        # Beat: the just-picked token has no entry yet
        fifth = VGroup(*(get_cell("empty", l, 4) for l in range(2)))
        none = Text("no entry yet", font_size=26).set_color(GREY_B).next_to(fifth, DOWN, buff=0.2)
        with self.play_beat("kv_last") as beat:
            self.play(FadeOut(not_row), FadeIn(fifth), FadeIn(none), run_time=beat.get_seconds_until(0.6))

        self.play(FadeOut(VGroup(board.everything(), and_chip, fifth, none)))
