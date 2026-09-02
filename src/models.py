from pydantic import BaseModel, model_validator
from typing import Any, List


class RuleSet(BaseModel):
    game_mode: str = "normal"
    level: int = 10
    width: int = 30
    height: int = 40
    lives: int = 3
    points_per_pacgum: int = 10
    points_per_super_pacgum: int = 50
    points_per_ghost: int = 200
    seed: Any = 42
    max_level_time: int = 90

    @model_validator(mode="before")
    @classmethod
    def log_missing_defaults(cls, data: Any) -> Any:
        if isinstance(data, dict):
            for field_name, field_info in cls.model_fields.items():
                if field_name not in data:
                    default_val = field_info.default
                    print(
                        f"[INFO] {cls.__name__}: Missing '{field_name}'",
                        f"in config. Using default: {default_val}",
                    )

        return data or {}


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
