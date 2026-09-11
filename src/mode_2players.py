"""Two-player mode: three self-contained sub-modes and their key maps.

Keyboard only. Player 1 uses WASD, player 2 uses the arrow keys.
"""

from typing import Dict, Optional, Tuple

from src.utils import Key

# Sub-modes shown in the two-player sub-menu.
SUBMODES = ["Versus", "Coop", "Random"]

# Random sub-mode: control-switch bounds, in seconds.
SWITCH_MIN: float = 3.0
SWITCH_MAX: float = 15.0

# Per-player key maps (key code -> direction).
P1_KEYS: Dict[int, Tuple[int, int]] = {
    Key.Wb: (0, -1),
    Key.Sb: (0, 1),
    Key.Ab: (-1, 0),
    Key.Db: (1, 0),
}
P2_KEYS: Dict[int, Tuple[int, int]] = {
    Key.UP: (0, -1),
    Key.DOWN: (0, 1),
    Key.LEFT: (-1, 0),
    Key.RIGHT: (1, 0),
}

# Coop: player 1 (WASD) moves vertically, player 2 (arrows) horizontally.
COOP_KEYS: Dict[int, Tuple[int, int]] = {
    Key.Wb: (0, -1),
    Key.Sb: (0, 1),
    Key.LEFT: (-1, 0),
    Key.RIGHT: (1, 0),
}


def coop_dir(keycode: int) -> Optional[Tuple[int, int]]:
    """Return the coop direction for ``keycode``, or None."""
    return COOP_KEYS.get(keycode)


def player_dir(keycode: int, player: int) -> Optional[Tuple[int, int]]:
    """Return the direction for ``keycode`` for the given player, or None."""
    keys = P1_KEYS if player == 1 else P2_KEYS
    return keys.get(keycode)
