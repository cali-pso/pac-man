HARDCORE_LIVES: int = 1
TIME_FACTOR: float = 0.5
NO_SUPER_PACGUMS: bool = True


def apply_to_ruleset_kwargs(base: dict, ruleset: object = None) -> dict:
    """Applique le preset hardcore : temps reduit + vies limitees.
    Les valeurs sont lues sur le ruleset (config), avec repli sur constantes.
    """
    kw = dict(base)
    factor = getattr(ruleset, "time_factor", TIME_FACTOR)
    lives = getattr(ruleset, "hardcore_lives", HARDCORE_LIVES)
    kw["max_time"] = max(1, int(kw.get("max_time", 90) * factor))
    kw["lives"] = lives
    return kw


def no_supers_for(ruleset: object = None) -> bool:
    """Faut-il retirer les super-pacgums ? (config, repli sur constante)"""
    return getattr(ruleset, "no_super_pacgums", NO_SUPER_PACGUMS)
