"""Hardcore mode preset: fewer lives, reduced time, no super-pacgums.

Default values act as fallbacks; in game they come from ``config.json``
(the ``hardcore_mode`` section) through the ``HardcoreRuleSet``.
"""

HARDCORE_LIVES: int = 1
TIME_FACTOR: float = 0.5
NO_SUPER_PACGUMS: bool = True


def apply_to_ruleset_kwargs(base: dict, ruleset: object = None) -> dict:
    """Return session kwargs with the hardcore preset applied.

    Reduces the level time and limits the lives, reading the values from
    the rule set (config) and falling back to the module constants.
    """
    kw = dict(base)
    factor = getattr(ruleset, "time_factor", TIME_FACTOR)
    lives = getattr(ruleset, "hardcore_lives", HARDCORE_LIVES)
    kw["max_time"] = max(1, int(kw.get("max_time", 90) * factor))
    kw["lives"] = lives
    return kw


def no_supers_for(ruleset: object = None) -> bool:
    """Return whether super-pacgums must be removed (config, then default)."""
    return getattr(ruleset, "no_super_pacgums", NO_SUPER_PACGUMS)
