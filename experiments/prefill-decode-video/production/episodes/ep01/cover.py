from explainer_studio.scene_kit import *

from shared.series import (OUTPUT_COLOR, TokenGrid, get_input_point, get_output_chip, get_output_point,
                           get_prompt_chip, get_return_path)


class Cover(CoverScene):
    title = "Why does AI write\none token at a time?"

    def get_visual(self):
        grid = TokenGrid()
        columns = VGroup(*(grid.build_column(c, "saved") for c in range(3)))
        empty = grid.build_column(3, "empty")
        chips = VGroup(*(get_prompt_chip(w).move_to(get_input_point(i)) for i, w in enumerate(["The", "sky", "is"])))
        full = get_return_path(2, 3)
        trail = VMobject().pointwise_become_partial(full, 0.1, 0.88).set_stroke(OUTPUT_COLOR, 5, opacity=0.9)
        ghost = get_output_chip("blue").move_to(get_output_point(2)).set_opacity(0.35)
        blue = get_output_chip("blue").move_to(get_input_point(3))
        end = trail.get_end()
        direction = end - trail.point_from_proportion(0.97)
        tip = ArrowTip().set_fill(OUTPUT_COLOR, 1).scale(0.9)
        tip.rotate(angle_of_vector(direction) - tip.get_angle()).move_to(end)
        return VGroup(trail, tip, columns, empty, chips, ghost, blue)
