import random
from typing import Dict, List


class RunState:
    """Modificateurs cumules de la partie roguelite en cours."""

    def __init__(self, lives: int) -> None:
        self.lives = lives
        self.pac_speed_factor = 1.0       # <1 = plus rapide
        self.ghost_speed_factor = 1.0     # >1 = fantomes plus lents
        self.power_duration_factor = 1.0
        self.score_multiplier = 1.0
        self.magnet_range = 0             # cases d'attraction des pacgums
        self.shields = 0                  # absorbe une collision
        self.time_bonus = 0               # secondes ajoutees par niveau
        self.next_freeze_ghosts = 0.0     # gel des fantomes (prochain niveau)
        self.next_freeze_pac = 0.0        # gel de Pac-Man (prochain niveau)
        self.reveal_level = 0             # +1 revele / -1 cache (permanent)

    def summary(self) -> List[str]:
        """Liste des effets actifs, pour l'ecran de pause."""
        out = [f"Vies: {self.lives}", f"Boucliers: {self.shields}"]
        if abs(self.pac_speed_factor - 1.0) > 0.01:
            out.append(f"Vitesse Pac-Man: x{1.0 / self.pac_speed_factor:.2f}")
        if abs(self.ghost_speed_factor - 1.0) > 0.01:
            out.append(
                f"Vitesse fantomes: x{1.0 / self.ghost_speed_factor:.2f}")
        if self.magnet_range:
            out.append(f"Aimant: {self.magnet_range}")
        if abs(self.power_duration_factor - 1.0) > 0.01:
            out.append(f"Super-pacgum: x{self.power_duration_factor:.2f}")
        if self.time_bonus:
            out.append(f"Temps/niveau: {self.time_bonus:+d}s")
        if abs(self.score_multiplier - 1.0) > 0.01:
            out.append(f"Score: x{self.score_multiplier:.2f}")
        if self.reveal_level != 0:
            hidden = max(0, min(3, 1 - self.reveal_level))
            out.append(f"Cartes mystere: {hidden}")
        return out


# --- Les 10 paires (bonus / malus). op: mul|add|set ; guard: (champ, cmp, v)
PAIRS: List[Dict] = [
    {  # 1. Vitesse de Pac-Man
        "bonus": {"label": "Pac-Man plus RAPIDE",
                  "field": "pac_speed_factor", "op": "mul", "value": 0.85,
                  "min": 0.4},
        "malus": {"label": "Pac-Man plus LENT",
                  "field": "pac_speed_factor", "op": "mul", "value": 1.15,
                  "max": 2.0},
    },
    {  # 2. Vies
        "bonus": {"label": "+1 vie",
                  "field": "lives", "op": "add", "value": 1, "max": 9},
        "malus": {"label": "-1 vie",
                  "field": "lives", "op": "add", "value": -1, "min": 1,
                  "guard": ("lives", ">", 1)},
    },
    {  # 3. Vitesse des fantomes
        "bonus": {"label": "Fantomes plus LENTS",
                  "field": "ghost_speed_factor", "op": "mul", "value": 1.15,
                  "max": 2.5},
        "malus": {"label": "Fantomes plus RAPIDES",
                  "field": "ghost_speed_factor", "op": "mul", "value": 0.85,
                  "min": 0.4},
    },
    {  # 4. Aimant a pacgums
        "bonus": {"label": "Aimant +1 case",
                  "field": "magnet_range", "op": "add", "value": 1, "max": 4},
        "malus": {"label": "Aimant -1 case",
                  "field": "magnet_range", "op": "add", "value": -1, "min": 0,
                  "guard": ("magnet_range", ">", 0)},
    },
    {  # 5. Bouclier
        "bonus": {"label": "+1 bouclier",
                  "field": "shields", "op": "add", "value": 1, "max": 5},
        "malus": {"label": "-1 bouclier",
                  "field": "shields", "op": "add", "value": -1, "min": 0,
                  "guard": ("shields", ">", 0)},
    },
    {  # 6. Duree du super-pacgum
        "bonus": {"label": "Super-pacgum plus LONG",
                  "field": "power_duration_factor", "op": "mul", "value": 1.3,
                  "max": 3.0},
        "malus": {"label": "Super-pacgum plus COURT",
                  "field": "power_duration_factor", "op": "mul", "value": 0.7,
                  "min": 0.4,
                  "guard": ("power_duration_factor", ">", 0.5)},
    },
    {  # 7. Temps de depart
        "bonus": {"label": "+15 s par niveau",
                  "field": "time_bonus", "op": "add", "value": 15, "max": 120},
        "malus": {"label": "-15 s par niveau",
                  "field": "time_bonus", "op": "add", "value": -15,
                  "min": -45,
                  "guard": ("time_bonus", ">", -30)},
    },
    {  # 8. Revele / cache une carte mystere (PERMANENT)
        "bonus": {"label": "Revele une carte mystere (permanent)",
                  "field": "reveal_level", "op": "add", "value": 1, "max": 1,
                  "guard": ("reveal_level", "<", 1)},
        "malus": {"label": "Cache une carte de plus (permanent)",
                  "field": "reveal_level", "op": "add", "value": -1, "min": -2,
                  "guard": ("reveal_level", ">", -2)},
    },
    {  # 9. Gel en debut de niveau
        "bonus": {"label": "Fantomes geles 3s",
                  "field": "next_freeze_ghosts", "op": "set", "value": 3.0},
        "malus": {"label": "Pac-Man gele 3s",
                  "field": "next_freeze_pac", "op": "set", "value": 3.0},
    },
    {  # 10. Score
        "bonus": {"label": "Score x2",
                  "field": "score_multiplier", "op": "mul", "value": 2.0,
                  "max": 16.0},
        "malus": {"label": "Score /2",
                  "field": "score_multiplier", "op": "mul", "value": 0.5,
                  "min": 0.25,
                  "guard": ("score_multiplier", ">", 0.5)},
    },
]

_CMP = {
    ">": lambda a, b: a > b,
    ">=": lambda a, b: a >= b,
    "<": lambda a, b: a < b,
    "<=": lambda a, b: a <= b,
}


def is_eligible(run: RunState, spec: Dict) -> bool:
    guard = spec.get("guard")
    if not guard:
        return True
    field, cmp, val = guard
    return _CMP[cmp](getattr(run, field), val)


def apply_spec(run: RunState, spec: Dict) -> None:
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
    """Un bonus/malus aleatoire pour un super-pacgum (effet sur le niveau).
    Exclut la paire revele/cache (sans effet temporaire)."""
    idx = random.choice([i for i in range(len(PAIRS)) if i != 7])
    pair = PAIRS[idx]
    if random.random() < 0.5:
        spec, kind = pair["bonus"], "bonus"
    else:
        spec, kind = pair["malus"], "malus"
    return {"kind": kind, "spec": spec, "label": spec["label"]}


class RogueliteEngine:
    """Tirage des choix avec biais anti-serie."""

    def __init__(self) -> None:
        self.bonus_bias = 0.5  # proba d'un bonus (glisse a chaque choix)

    def draw(self, run: RunState) -> List[Dict]:
        """Retourne 3 choix : {pair, kind, spec, label, hidden}.
        Par defaut la 3e carte est mystere (hidden). 'reveal' en revele une,
        'hide' en cache une de plus."""
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
                    spec = pair["bonus"]  # le bonus est toujours eligible
            kind = "bonus" if spec is pair["bonus"] else "malus"
            choices.append({"pair": pi, "kind": kind, "spec": spec,
                            "label": spec["label"], "hidden": False})
            bias = min(0.9, max(0.1, bias + (0.1 if not want_bonus else -0.1)))

        # Cartes cachees : 1 par defaut, ajuste par reveal_level (permanent)
        hidden = max(0, min(len(choices), 1 - run.reveal_level))
        for i in range(len(choices) - hidden, len(choices)):
            choices[i]["hidden"] = True
        return choices

    def register_pick(self, choice: Dict) -> None:
        # anti-serie : prendre un bonus rend les bonus plus rares ensuite
        if choice["kind"] == "bonus":
            self.bonus_bias = max(0.15, self.bonus_bias - 0.1)
        else:
            self.bonus_bias = min(0.85, self.bonus_bias + 0.1)

    def apply(self, run: RunState, choice: Dict) -> None:
        apply_spec(run, choice["spec"])
        self.register_pick(choice)
