"""Roguelite mode: after each level, pick a bonus/malus (anti-streak draw).

Effects accumulate over the run. All ten bonus/malus pairs and the draw
logic live here.
"""

import random
from typing import Dict, List


class RunState:
    """Accumulated modifiers of the current roguelite run."""

    def __init__(self, lives: int) -> None:
        """Initialise a neutral run state with the given number of lives."""
        self.lives = lives
        self.pac_speed_factor = 1.0  # < 1 = faster.
        self.ghost_speed_factor = 1.0  # > 1 = slower ghosts.
        self.power_duration_factor = 1.0
        self.score_multiplier = 1.0
        self.magnet_range = 0  # Pacgum attraction radius (cells).
        self.shields = 0  # Absorbs a collision.
        self.time_bonus = 0  # Seconds added per level.
        self.next_freeze_ghosts = 0.0  # Ghost freeze (next level).
        self.next_freeze_pac = 0.0  # Pac-Man freeze (next level).
        self.reveal_level = 0  # +1 reveal / -1 hide (permanent).

    def summary(self) -> List[str]:
        """Return the active effects as display lines (for the pause menu)."""
        out = [f"Lives: {self.lives}", f"Shields: {self.shields}"]
        if abs(self.pac_speed_factor - 1.0) > 0.01:
            out.append(f"Pac-Man speed: x{1.0 / self.pac_speed_factor:.2f}")
        if abs(self.ghost_speed_factor - 1.0) > 0.01:
            out.append(f"Ghost speed: x{1.0 / self.ghost_speed_factor:.2f}")
        if self.magnet_range:
            out.append(f"Magnet: {self.magnet_range}")
        if abs(self.power_duration_factor - 1.0) > 0.01:
            out.append(f"Super-pacgum: x{self.power_duration_factor:.2f}")
        if self.time_bonus:
            out.append(f"Time/level: {self.time_bonus:+d}s")
        if abs(self.score_multiplier - 1.0) > 0.01:
            out.append(f"Score: x{self.score_multiplier:.2f}")
        if self.reveal_level != 0:
            hidden = max(0, min(3, 1 - self.reveal_level))
            out.append(f"Mystery cards: {hidden}")
        return out


# The ten pairs (bonus / malus). op: mul|add|set; guard: (field, cmp, value).
PAIRS: List[Dict] = [
    {  # 1. Pac-Man speed.
        "bonus": {
            "label": "Pac-Man FASTER",
            "field": "pac_speed_factor",
            "op": "mul",
            "value": 0.85,
            "min": 0.4,
        },
        "malus": {
            "label": "Pac-Man SLOWER",
            "field": "pac_speed_factor",
            "op": "mul",
            "value": 1.15,
            "max": 2.0,
        },
    },
    {  # 2. Lives.
        "bonus": {
            "label": "+1 life",
            "field": "lives",
            "op": "add",
            "value": 1,
            "max": 9,
        },
        "malus": {
            "label": "-1 life",
            "field": "lives",
            "op": "add",
            "value": -1,
            "min": 1,
            "guard": ("lives", ">", 1),
        },
    },
    {  # 3. Ghost speed.
        "bonus": {
            "label": "Ghosts SLOWER",
            "field": "ghost_speed_factor",
            "op": "mul",
            "value": 1.15,
            "max": 2.5,
        },
        "malus": {
            "label": "Ghosts FASTER",
            "field": "ghost_speed_factor",
            "op": "mul",
            "value": 0.85,
            "min": 0.4,
        },
    },
    {  # 4. Pacgum magnet.
        "bonus": {
            "label": "Magnet +1 cell",
            "field": "magnet_range",
            "op": "add",
            "value": 1,
            "max": 4,
        },
        "malus": {
            "label": "Magnet -1 cell",
            "field": "magnet_range",
            "op": "add",
            "value": -1,
            "min": 0,
            "guard": ("magnet_range", ">", 0),
        },
    },
    {  # 5. Shield.
        "bonus": {
            "label": "+1 shield",
            "field": "shields",
            "op": "add",
            "value": 1,
            "max": 5,
        },
        "malus": {
            "label": "-1 shield",
            "field": "shields",
            "op": "add",
            "value": -1,
            "min": 0,
            "guard": ("shields", ">", 0),
        },
    },
    {  # 6. Super-pacgum duration.
        "bonus": {
            "label": "Super-pacgum LONGER",
            "field": "power_duration_factor",
            "op": "mul",
            "value": 1.3,
            "max": 3.0,
        },
        "malus": {
            "label": "Super-pacgum SHORTER",
            "field": "power_duration_factor",
            "op": "mul",
            "value": 0.7,
            "min": 0.4,
            "guard": ("power_duration_factor", ">", 0.5),
        },
    },
    {  # 7. Start time.
        "bonus": {
            "label": "+15 s per level",
            "field": "time_bonus",
            "op": "add",
            "value": 15,
            "max": 120,
        },
        "malus": {
            "label": "-15 s per level",
            "field": "time_bonus",
            "op": "add",
            "value": -15,
            "min": -45,
            "guard": ("time_bonus", ">", -30),
        },
    },
    {  # 8. Reveal / hide a mystery card (permanent).
        "bonus": {
            "label": "Reveal a mystery card (permanent)",
            "field": "reveal_level",
            "op": "add",
            "value": 1,
            "max": 1,
            "guard": ("reveal_level", "<", 1),
        },
        "malus": {
            "label": "Hide one more card (permanent)",
            "field": "reveal_level",
            "op": "add",
            "value": -1,
            "min": -2,
            "guard": ("reveal_level", ">", -2),
        },
    },
    {  # 9. Start-of-level freeze.
        "bonus": {
            "label": "Ghosts frozen 3s",
            "field": "next_freeze_ghosts",
            "op": "set",
            "value": 3.0,
        },
        "malus": {
            "label": "Pac-Man frozen 3s",
            "field": "next_freeze_pac",
            "op": "set",
            "value": 3.0,
        },
    },
    {  # 10. Score.
        "bonus": {
            "label": "Score x2",
            "field": "score_multiplier",
            "op": "mul",
            "value": 2.0,
            "max": 16.0,
        },
        "malus": {
            "label": "Score /2",
            "field": "score_multiplier",
            "op": "mul",
            "value": 0.5,
            "min": 0.25,
            "guard": ("score_multiplier", ">", 0.5),
        },
    },
]


def _compare(op: str, a: float, b: float) -> bool:
    """Return the result of the comparison ``a <op> b``."""
    if op == ">":
        return a > b
    if op == ">=":
        return a >= b
    if op == "<":
        return a < b
    return a <= b


def is_eligible(run: RunState, spec: Dict) -> bool:
    """Return whether a bonus/malus spec is eligible in the current state."""
    guard = spec.get("guard")
    if not guard:
        return True
    field, op, val = guard
    return _compare(op, getattr(run, field), val)


def apply_spec(run: RunState, spec: Dict) -> None:
    """Apply a bonus/malus spec to the run state, clamped to its bounds."""
    field, op, val = spec["field"], spec["op"], spec["value"]
    cur = getattr(run, field)
    if op == "mul":
        new = cur * val
    elif op == "add":
        new = cur + val
    else:  # set
        new = val
    if "min" in spec:
        new = max(spec["min"], new)
    if "max" in spec:
        new = min(spec["max"], new)
    setattr(run, field, new)


def random_temp_effect() -> Dict:
    """Return a random bonus/malus for a super-pacgum (level effect).

    Excludes the reveal/hide pair, which has no temporary meaning.
    """
    idx = random.choice([i for i in range(len(PAIRS)) if i != 7])
    pair = PAIRS[idx]
    if random.random() < 0.5:
        spec, kind = pair["bonus"], "bonus"
    else:
        spec, kind = pair["malus"], "malus"
    return {"kind": kind, "spec": spec, "label": spec["label"]}


class RogueliteEngine:
    """Draws the post-level choices with an anti-streak bias."""

    def __init__(self) -> None:
        """Start with an even bonus/malus bias."""
        self.bonus_bias = 0.5  # Probability of a bonus (drifts on each pick).

    def draw(self, run: RunState) -> List[Dict]:
        """Return three choices; some may be hidden (mystery cards).

        The last cards are hidden by default; ``reveal_level`` shifts how
        many stay hidden.
        """
        n = 3
        indices = random.sample(range(len(PAIRS)), min(n, len(PAIRS)))
        choices: List[Dict] = []
        bias = self.bonus_bias
        for pi in indices:
            pair = PAIRS[pi]
            want_bonus = random.random() < bias
            spec = pair["bonus"] if want_bonus else pair["malus"]
            if not is_eligible(run, spec):
                spec = pair["malus"] if want_bonus else pair["bonus"]
                if not is_eligible(run, spec):
                    spec = pair["bonus"]  # The bonus is always eligible.
            kind = "bonus" if spec is pair["bonus"] else "malus"
            choices.append(
                {
                    "pair": pi,
                    "kind": kind,
                    "spec": spec,
                    "label": spec["label"],
                    "hidden": False,
                }
            )
            bias = min(0.9, max(0.1, bias + (0.1 if not want_bonus else -0.1)))

        hidden = max(0, min(len(choices), 1 - run.reveal_level))
        for i in range(len(choices) - hidden, len(choices)):
            choices[i]["hidden"] = True
        return choices

    def register_pick(self, choice: Dict) -> None:
        """Shift the bias so streaks of bonuses/maluses become rarer."""
        if choice["kind"] == "bonus":
            self.bonus_bias = max(0.15, self.bonus_bias - 0.1)
        else:
            self.bonus_bias = min(0.85, self.bonus_bias + 0.1)

    def apply(self, run: RunState, choice: Dict) -> None:
        """Apply the chosen effect and update the anti-streak bias."""
        apply_spec(run, choice["spec"])
        self.register_pick(choice)
