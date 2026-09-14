"""Shared constants, enumerations and small helpers used across the game."""

from enum import Enum, IntEnum, auto
from typing import Any


WIDTH: int = 1500
HEIGHT: int = 1500


class GameState(Enum):
    """The high-level states the application can be in."""

    INTRO = auto()
    MAIN_MENU = auto()
    MENU_HIGHSCORES = auto()
    MENU_INSTRUCTIONS = auto()
    MODE_MENU = auto()
    PLAYING = auto()
    PAUSED = auto()


class Color(IntEnum):
    """Palette colors, stored as 0xRRGGBB integers."""

    WHITE = 0xFFFFFF
    YELLOW = 0x00FFFF
    CYAN = 0xFFFF00
    GRAY = 0x888888
    GREEN = 0x00AA00


class Key(IntEnum):
    """X11 key codes used by the game input handling."""

    ESC = 65307
    ENTER = 65293
    SPACE = 32
    UP = 65362
    DOWN = 65364
    LEFT = 65361
    RIGHT = 65363
    Wb = 119
    Ab = 97
    Sb = 115
    Db = 100
    Nb = 110
    Ib = 105


def quit(mlx: Any, mlx_ptr: Any) -> int:
    """Ask the MLX loop to stop cleanly and return 0."""
    mlx.mlx_loop_exit(mlx_ptr)
    return 0


def center_x_str(text: str) -> int:
    """Return the X coordinate that horizontally centers ``text``."""
    char_w = 9  # Standard MLX font width.
    return (WIDTH - (len(text) * char_w)) // 2
