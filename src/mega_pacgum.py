SPAWN_CHANCE: float = 0.01            # 1 % dans les modes concernes
SPAWN_CHANCE_HARDCORE: float = 0.005  # 0.5 % en hardcore
SCORE_MULTIPLIER: float = 1.5   # score x1.5 sur ce qu'on ramasse ensuite
SPEED_FACTOR: float = 0.5       # cadence de Pac-Man x ce facteur (plus rapide)
# ---------------------------------------------------------------------------


def spawn_chance_for(mode: str) -> float:
    """Chance d'apparition selon le mode (0 en Normal)."""
    if mode == "Normal":
        return 0.0
    if mode == "Hardcore":
        return SPAWN_CHANCE_HARDCORE
    return SPAWN_CHANCE