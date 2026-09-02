from pydantic import BaseModel
from typing import Any, List, Tuple


class RuleSet(BaseModel):
    game_mode: str = "normal"
    levels: int = 10
    width: int = 30
    height: int = 40
    lives: int = 3
    points_per_pacgum: int = 10
    points_per_super_pacgum: int = 50
    points_per_ghost: int = 200
    seed: Any = 42
    max_level_time: int = 90


class ShadowRuleSet(RuleSet):
    flashlight_radius: int = 3
    flashlight_reduction_time: int = 10
    flashlight_reduction_step: int = 1
    flashlight_augmentation_step: int = 2
    flashlight_augmentation_triggers: List[str] = ["ghosts", "super_pacgum"]


class HardcoreRuleSet(RuleSet):
    pass


class RogueliteRuleSet(RuleSet):
    bonus_multiplier: int = 1


class TwoPlayerRuleSet(RuleSet):
    control_switch_time_range: List[int] = (10, 20)
