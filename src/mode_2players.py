"""Mode 2 JOUEURS : trois sous-modes traites comme des modes a part entiere.
  - Coop   : meme Pac-Man. J1 (WASD) controle haut/bas, J2 (fleches) g/d.
  - Random : meme Pac-Man. Le controle bascule entre J1 et J2 (aleatoire).
  - Versus : J1 = Pac-Man, J2 = un fantome (a venir).

Clavier uniquement. J1 = WASD, J2 = fleches.

>>> REGLAGES A MODIFIER ICI <<<

A placer dans src/mode_2players.py
"""

from __future__ import annotations

from src.utils import Key

# Sous-modes disponibles dans le sous-menu (Versus ajoute plus tard)
SUBMODES = ["Versus", "Coop", "Random"]

# --- Random : bornes de bascule du controle, en secondes -------------------
SWITCH_MIN: float = 3.0
SWITCH_MAX: float = 15.0
# ---------------------------------------------------------------------------

# Jeux de touches par joueur (keycode -> direction)
P1_KEYS = {
    Key.Wb: (0, -1), Key.Sb: (0, 1), Key.Ab: (-1, 0), Key.Db: (1, 0),
}
P2_KEYS = {
    Key.UP: (0, -1), Key.DOWN: (0, 1), Key.LEFT: (-1, 0), Key.RIGHT: (1, 0),
}

# Coop : J1 (WASD) -> uniquement vertical ; J2 (fleches) -> horizontal
COOP_KEYS = {
    Key.Wb: (0, -1), Key.Sb: (0, 1), Key.LEFT: (-1, 0), Key.RIGHT: (1, 0),
}


def coop_dir(keycode: int):
    return COOP_KEYS.get(keycode)


def player_dir(keycode: int, player: int):
    keys = P1_KEYS if player == 1 else P2_KEYS
    return keys.get(keycode)
