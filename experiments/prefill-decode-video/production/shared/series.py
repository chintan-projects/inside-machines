"""Shared code of the series: concept colours from series-bible.md, token chips, and the layer-by-position grid.

The grid: token positions are columns, layers are rows (row 0 = layer 1, at the bottom). Input chips sit under the
grid, sampled chips above it. A cell's state follows the invariant from the series bible: it is teal ("saved") only
once its token has been processed at that layer.
"""

from explainer_studio.scene_kit import *

# Concept colours (series-bible.md)
PROMPT_COLOR = BLUE_C
OUTPUT_COLOR = GOLD_C
ACTIVE_COLOR = YELLOW
KV_COLOR = TEAL
BLOCKED_COLOR = RED_C
STRUCTURE_COLOR = GREY_B
MEMORY_COLOR = PURPLE_C

MAIN_QUESTION = "Why is the prompt read together, but the answer written one token at a time?"

# Grid geometry (frame units)
COLUMN_XS = [-4.9, -3.3, -1.7, -0.1, 1.5]
ROW_YS = [-0.75, 0.15, 1.05]
INPUT_Y = -2.0
OUTPUT_Y = 2.25
CELL_WIDTH = 1.1
CELL_HEIGHT = 0.6
CHIP_HEIGHT = 0.62
CHIP_FONT_SIZE = 30
LABEL_SIZE = 26
NOTE_SIZE = 22


def get_main_question_line() -> Text:
    """The faint main-question line, always in the same place at the top."""
    line = Text(MAIN_QUESTION, font_size=NOTE_SIZE).set_color(GREY_B)
    line.set_opacity(0.75)
    return line.to_edge(UP, buff=0.3)


def get_chip(text: str, color=PROMPT_COLOR, font_size: float = CHIP_FONT_SIZE, min_width: float = 1.0) -> Parts:
    """A token chip: rounded box in the concept colour with its text. Parts: .box, .label."""
    label = Text(text, font_size=font_size).set_color(WHITE)
    box = RoundedRectangle(width=max(label.get_width() + 0.4, min_width), height=CHIP_HEIGHT, corner_radius=0.14)
    box.set_fill(color, 0.22).set_stroke(color, 2.5)
    label.move_to(box)
    chip = Parts(box, label)
    chip.box, chip.label = box, label
    return chip


def get_prompt_chip(text: str) -> Parts:
    return get_chip(text, PROMPT_COLOR)


def get_output_chip(text: str) -> Parts:
    return get_chip(text, OUTPUT_COLOR)


def get_cell_center(row: int, column: int) -> np.ndarray:
    return np.array([COLUMN_XS[column], ROW_YS[row], 0.0])


def get_input_point(column: int) -> np.ndarray:
    return np.array([COLUMN_XS[column], INPUT_Y, 0.0])


def get_output_point(column: int) -> np.ndarray:
    return np.array([COLUMN_XS[column], OUTPUT_Y, 0.0])


def get_cell(row: int, column: int, state: str = "empty") -> VMobject:
    """One grid cell. States: empty (dashed grey), processed (white outline), active (yellow outline),
    saved (teal fill: a saved key + value)."""
    rect = RoundedRectangle(width=CELL_WIDTH, height=CELL_HEIGHT, corner_radius=0.1)
    rect.move_to(get_cell_center(row, column))
    if state == "empty":
        dashed = DashedVMobject(rect, num_dashes=18).set_stroke(GREY_C, 2)
        return dashed
    if state == "processed":
        return rect.set_stroke(WHITE, 2).set_fill(WHITE, 0.08)
    if state == "active":
        return rect.set_stroke(ACTIVE_COLOR, 3.5).set_fill(ACTIVE_COLOR, 0.10)
    if state == "saved":
        return rect.set_stroke(KV_COLOR, 2.5).set_fill(KV_COLOR, 0.55)
    raise ValueError(state)


def get_layer_labels() -> VGroup:
    labels = VGroup()
    for row, y in enumerate(ROW_YS):
        label = Text(f"layer {row + 1}", font_size=NOTE_SIZE + 2).set_color(GREY_B)
        label.move_to([COLUMN_XS[0] - CELL_WIDTH / 2 - 0.25, y, 0], aligned_edge=RIGHT)
        labels.add(label)
    return labels


class TokenGrid:
    """The grid's live cells by (row, column). `change` returns an animation and records the new cell."""

    def __init__(self):
        self.cells: dict[tuple[int, int], VMobject] = {}
        self.states: dict[tuple[int, int], str] = {}

    def build_column(self, column: int, state: str = "empty") -> VGroup:
        group = VGroup()
        for row in range(len(ROW_YS)):
            cell = get_cell(row, column, state)
            self.cells[(row, column)] = cell
            self.states[(row, column)] = state
            group.add(cell)
        return group

    def get_column(self, column: int) -> VGroup:
        return VGroup(*(self.cells[(row, column)] for row in range(len(ROW_YS)) if (row, column) in self.cells))

    def get_row(self, row: int, columns) -> VGroup:
        return VGroup(*(self.cells[(row, c)] for c in columns))

    def get_all(self) -> VGroup:
        return VGroup(*self.cells.values())

    def change(self, row: int, column: int, state: str) -> Animation:
        old = self.cells[(row, column)]
        new = get_cell(row, column, state)
        self.cells[(row, column)] = new
        self.states[(row, column)] = state
        return FadeTransform(old, new)


def get_pulse(cell: Mobject, color=WHITE, opacity: float = 0.7) -> Animation:
    """A brief flash over a cell: a filled copy that fades out while growing."""
    flash = RoundedRectangle(width=CELL_WIDTH, height=CELL_HEIGHT, corner_radius=0.1).move_to(cell)
    flash.set_fill(color, opacity).set_stroke(color, 0)
    return FadeOut(flash, scale=1.18)


def get_look_arrow(from_column: int, to_column: int, row: int = 0, color=STRUCTURE_COLOR,
                   stroke_width: float = 3) -> Parts:
    """A curved arrow under a grid row, from one cell's bottom to another's: 'looks at'."""
    start = get_cell_center(row, from_column) + (CELL_HEIGHT / 2 + 0.04) * DOWN
    end = get_cell_center(row, to_column) + (CELL_HEIGHT / 2 + 0.04) * DOWN
    # Arcs bulge downward whichever way they run.
    angle = -PI / 2.6 if from_column > to_column else PI / 2.6
    span = abs(from_column - to_column)
    angle *= 1.0 / max(1, span) ** 0.5
    return get_curved_arrow(start, end, angle=angle, color=color, stroke_width=stroke_width, tip_size=0.16)


def get_self_loop(column: int, row: int = 0, color=STRUCTURE_COLOR) -> Parts:
    """A small loop under a cell: 'looks at itself'."""
    center = get_cell_center(row, column) + (CELL_HEIGHT / 2 + 0.04) * DOWN
    start = center + 0.28 * LEFT
    end = center + 0.28 * RIGHT
    return get_curved_arrow(start, end, angle=PI * 1.2, color=color, stroke_width=2.5, tip_size=0.13)


def get_return_path(from_column: int, to_column: int) -> VMobject:
    """The path a sampled chip takes from above column `from_column` back to the input row under `to_column`,
    around the right side of the grid."""
    right_x = COLUMN_XS[-1] + CELL_WIDTH / 2 + 0.75
    points = [
        get_output_point(from_column),
        np.array([right_x - 0.3, OUTPUT_Y + 0.05, 0]),
        np.array([right_x, 0.15, 0]),
        np.array([right_x - 0.3, INPUT_Y - 0.05, 0]),
        get_input_point(to_column),
    ]
    path = VMobject().set_points_smoothly(points)
    return path.set_stroke(OUTPUT_COLOR, 0, opacity=0)


def get_score_panel(entries: list[tuple[str, float]], winner_index: int = 0, width: float = 3.4) -> Parts:
    """Illustrative next-token scores: a title, then one row per candidate (label + bar). Parts: .title, .rows,
    .bars, .labels."""
    title = Text("next-token scores (illustrative)", font_size=NOTE_SIZE).set_color(GREY_A)
    rows, bars, labels = VGroup(), VGroup(), VGroup()
    for text, value in entries:
        label = Text(text, font_size=LABEL_SIZE).set_color(WHITE)
        bar = Rectangle(width=max(0.08, value * (width - 1.3)), height=0.28)
        bar.set_fill(GREY_B, 0.8).set_stroke(width=0)
        label_slot = Rectangle(width=1.1, height=0.4).set_opacity(0)
        label.move_to(label_slot, aligned_edge=LEFT)
        row = VGroup(label_slot, label, bar)
        bar.next_to(label_slot, RIGHT, buff=0.15)
        rows.add(row)
        bars.add(bar)
        labels.add(label)
    rows.arrange(DOWN, aligned_edge=LEFT, buff=0.18)
    panel = Parts(title, rows).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
    panel.title, panel.rows, panel.bars, panel.labels = title, rows, bars, labels
    return panel


def get_conclusion(text: str, color=WHITE, font_size: float = 30) -> Text:
    sentence = Text(text, font_size=font_size).set_color(color)
    return sentence.to_edge(DOWN, buff=0.35)


def get_note(text: str, color=GREY_B, font_size: float = NOTE_SIZE) -> Text:
    return Text(text, font_size=font_size).set_color(color)


class SeriesEndCreditsScene(EndCreditsScene):
    pass
