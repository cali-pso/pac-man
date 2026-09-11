"""Pydantic configuration models: the rule set for each game mode."""

from typing import Any, List

from pydantic import BaseModel, model_validator


class RuleSet(BaseModel):
    """Base configuration shared by every game mode."""

    game_mode: str = "normal"
    level: int = Field(gt=9, default=10)
    width: int = 30
    height: int = 40
    lives: int = 3
    points_per_pacgum: int = 10
    points_per_super_pacgum: int = 50
    points_per_ghost: int = 200
    seed: Any = 42
    max_level_time: int = 90
    # Tunable "engine" values (configurable):
    ghost_speed: float = 0.38  # Seconds between two ghost steps.
    pac_speed: float = 0.21  # Seconds between two Pac-Man steps.
    power_duration: float = 8.0  # Super-pacgum duration (edible).
    ghost_respawn_delay: float = 4.0  # Delay before an eaten ghost returns.
    mega_spawn_chance: float = 0.01  # Mega spawn probability per level.
    mega_score_multiplier: float = 1.5  # Score multiplier under mega.

    @model_validator(mode="before")
    @classmethod
    def log_missing_defaults(cls, data: Any) -> Any:
        """Log every config key that is missing and uses its default."""
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
    """Configuration for the Shadow mode (light zone parameters)."""

    flashlight_radius: float = 3.5
    flashlight_radius_min: float = 2.0
    flashlight_radius_max: float = 8.0
    flashlight_reduction_time: float = 1.0
    flashlight_reduction_step: float = 1.1
    flashlight_augmentation_step: float = 0.5
    shine_duration: float = 8.0
    flashlight_augmentation_triggers: List[str] = ["ghosts", "super_pacgum"]


class HardcoreRuleSet(RuleSet):
    """Configuration for the Hardcore mode preset."""

    hardcore_lives: int = 1  # Lives (1 = a single attempt).
    time_factor: float = 0.5  # Level time is multiplied by this factor.
    no_super_pacgums: bool = True  # Remove super-pacgums.


class RogueliteRuleSet(RuleSet):
    """Configuration for the Roguelite mode."""

    bonus_multiplier: int = 1


class TwoPlayerRuleSet(RuleSet):
    """Configuration for the two-player mode."""

    control_switch_time_range: List[int] = [10, 20]
