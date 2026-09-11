"""Legacy mega-pacgum tunables and helper.

The current game reads the mega spawn chance and score multiplier from the
rule set (config); this module is kept as a reference for the default
values and the per-mode spawn helper.
"""

SPAWN_CHANCE: float = 0.01  # 1% in the concerned modes.
SPAWN_CHANCE_HARDCORE: float = 0.005  # 0.5% in hardcore.
SCORE_MULTIPLIER: float = 1.5  # Score multiplier while mega is active.
SPEED_FACTOR: float = 0.5  # Pac-Man cadence factor (faster).


def spawn_chance_for(mode: str) -> float:
    """Return the mega spawn chance for ``mode`` (0 in Normal)."""
    if mode == "Normal":
        return 0.0
    if mode == "Hardcore":
        return SPAWN_CHANCE_HARDCORE
    return SPAWN_CHANCE
