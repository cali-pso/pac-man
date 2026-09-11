"""Intro cinematic: a few ASCII story slides shown before the menu."""

import time
from typing import Any, List, Tuple

from mlx import Mlx
from src.utils import HEIGHT, center_x_str

# Colors in 0xRRGGBB format.
C_YELLOW: int = 0xFFFF00
C_RED: int = 0xFF0000
C_PINK: int = 0xFF9CCE
C_CYAN: int = 0x00FFFF
C_ORANGE: int = 0xFFB852
C_WHITE: int = 0xFFFFFF
C_GREEN: int = 0x33CC66
C_GRAY: int = 0x888888

# How long each slide is displayed, in seconds.
SLIDE_SECONDS: float = 4

# A block is (kind, data, color, line_height).
Block = Tuple[str, Any, Any, int]
Slide = List[Block]


def art(lines: List[str], color: int, line_h: int = 16) -> Block:
    """Build an ASCII-art block."""
    return ("art", lines, color, line_h)


def lst(rows: List[Tuple[str, int]], line_h: int = 24) -> Block:
    """Build a colored list block (each row has its own color)."""
    return ("list", rows, None, line_h)


def text(rows: List[Tuple[str, int]], line_h: int = 26) -> Block:
    """Build a text block (each line has its own color)."""
    return ("text", rows, None, line_h)


PAC: List[str] = [
    "    ______",
    "   /      \\",
    "  /   ____/",
    "  |   /",
    "  |   \\___",
    "  \\       \\",
    "   \\______/",
]

PAC_SMALL: List[str] = [
    "  ____",
    " / _  \\",
    " |  __/",
    " \\___/",
]


def build_slides() -> List[Slide]:
    """Build the intro slides (all text is original)."""
    return [
        [
            art(PAC, C_YELLOW),
            text([("P A C - M A N", C_GREEN)], 32),
            text([("The Waka Chronicles", C_CYAN)], 26),
        ],
        [
            text(
                [
                    ("Long ago, in a maze of neon and shadow,", C_WHITE),
                    ("a small round hero awoke with a hunger", C_WHITE),
                    ("that could never, ever be satisfied.", C_WHITE),
                ]
            ),
            art(PAC_SMALL, C_YELLOW),
        ],
        [
            text([("But the maze is not empty...", C_WHITE)], 30),
            lst(
                [
                    ("[oo]  Blinky  - always on your tail", C_RED),
                    ("[oo]  Pinky   - loves an ambush", C_PINK),
                    ("[oo]  Inky    - impossible to read", C_CYAN),
                    ("[oo]  Clyde   - marches to his own tune", C_ORANGE),
                ]
            ),
        ],
        [
            art(PAC, C_YELLOW),
            text(
                [
                    ("Chase the score. Clear every pac-gum.", C_WHITE),
                    ("Fear the ghosts. Trust your reflexes.", C_WHITE),
                    ("WAKA-WAKA!", C_YELLOW),
                ],
                28,
            ),
        ],
    ]


class IntroScene:
    """Displays and advances the intro cinematic."""

    def __init__(
        self, mlx_inst: Mlx, mlx_ptr: object, win_ptr: object
    ) -> None:
        """Store the MLX handles and build the slides."""
        self.mlx = mlx_inst
        self.mlx_ptr = mlx_ptr
        self.win_ptr = win_ptr
        self.slides: List[Slide] = build_slides()
        self.index: int = 0
        self.started_at: float = time.time()
        self.finished: bool = False
        self._rendered_index: int = -1

    def reset(self) -> None:
        """Restart the intro from the first slide."""
        self.index = 0
        self.started_at = time.time()
        self.finished = False
        self._rendered_index = -1

    def _put(self, x: int, y: int, color: int, s: str) -> None:
        """Draw a string at (x, y) with the given color."""
        self.mlx.mlx_string_put(self.mlx_ptr, self.win_ptr, x, y, color, s)

    def _slide_height(self, slide: Slide) -> int:
        """Return the total pixel height of a slide."""
        total = 0
        for _kind, data, _color, line_h in slide:
            total += len(data) * line_h + 10
        return total

    def render(self) -> None:
        """Draw the current slide, vertically centered."""
        self.mlx.mlx_clear_window(self.mlx_ptr, self.win_ptr)
        slide = self.slides[self.index]

        y = max(30, (HEIGHT - self._slide_height(slide)) // 2)

        for kind, data, color, line_h in slide:
            if kind == "art":
                longest_line = max(data, key=len)
                block_x = max(10, center_x_str(longest_line))
                for s in data:
                    self._put(block_x, y, color, s)
                    y += line_h

            elif kind == "list":
                longest_line = max((s for s, _c in data), key=len)
                block_x = max(10, center_x_str(longest_line))
                for s, c in data:
                    self._put(block_x, y, c, s)
                    y += line_h

            else:  # text: each line centered individually.
                for s, c in data:
                    x = max(10, center_x_str(s))
                    self._put(x, y, c, s)
                    y += line_h

            y += 10

        progress = f"[{self.index + 1}/{len(self.slides)}]"
        self._put(center_x_str(progress), HEIGHT - 55, C_GRAY, progress)

        hint = "press any key to skip"
        self._put(center_x_str(hint), HEIGHT - 30, C_GRAY, hint)
        self._rendered_index = self.index

    def update(self) -> bool:
        """Advance the slides over time; return True when finished."""
        if self.finished:
            return True
        if time.time() - self.started_at >= SLIDE_SECONDS:
            self.started_at = time.time()
            self.index += 1
            if self.index >= len(self.slides):
                self.finished = True
                return True
        if self.index != self._rendered_index:
            self.render()
        return False

    def skip(self) -> None:
        """End the intro immediately (a key was pressed)."""
        self.finished = True
