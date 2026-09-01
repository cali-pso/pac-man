from enum import Enum, IntEnum, auto
from typing import Any

class GameState(Enum):
    """GameStates"""

    MAIN_MENU = auto()
    HIGHSCORES = auto()
    INSTRUCTIONS = auto()
    PLAYING = auto()
    PAUSED = auto()


class Color(IntEnum):
    """Colors as 0xRRGGBB"""

    WHITE = 0xFFFFFF
    YELLOW = 0x00FFFF
    CYAN = 0xFFFF00
    GRAY = 0x888888


class Key(IntEnum):
    ESC = 65307
    ENTER = 65293
    SPACE = 32
    UP = 65362
    DOWN = 65364
    LEFT = 65361
    RIGHT = 65363
    W = 119
    A = 97
    S = 115
    D = 100


def quit(mlx, mlx_ptr: Any) -> int:
    """Demande a la boucle MLX de s'arreter proprement."""
    mlx.mlx_loop_exit(mlx_ptr)
    return 0
