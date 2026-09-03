HARDCORE_LIVES: int = 1
TIME_FACTOR: float = 0.5
NO_SUPER_PACGUMS: bool = True

def apply_to_ruleset_kwargs(base: dict) -> dict:
    kw = dict(base)
    kw["max_time"] = max(1, int(kw.get("max_time", 90) * TIME_FACTOR))
    kw["lives"] = HARDCORE_LIVES
    return kw