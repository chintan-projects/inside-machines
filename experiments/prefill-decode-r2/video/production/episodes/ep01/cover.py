from explainer_studio.scene_kit import *

from shared.series import ANSWER_COLOR, COLUMN_XS, INPUT_Y, Board, get_chip, get_state


class Cover(CoverScene):
    title = "Why does AI write\none token at a time?"

    def get_visual(self) -> VGroup:
        board = Board(get_state("cp_pick_blue"))
        blue = get_chip("blue", "answer").move_to([COLUMN_XS[3], INPUT_Y, 0])
        ghost = board.chips[3].copy().set_opacity(0.35)
        path = get_curved_arrow(board.chips[3].get_right() + 0.1 * RIGHT, blue.get_right() + 0.1 * RIGHT,
                                angle=-PI / 1.6, color=ANSWER_COLOR, stroke_width=5, tip_size=0.26)
        return VGroup(board.grid(), VGroup(*(board.chips[c] for c in range(3))), ghost, path, blue)
