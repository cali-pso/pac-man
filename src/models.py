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
    # Valeurs "moteur" (configurables) :
    ghost_speed: float = 0.38          # secondes entre 2 pas des fantomes
    pac_speed: float = 0.21            # secondes entre 2 pas de Pac-Man
    power_duration: float = 8.0        # duree du super-pacgum (comestible)
    ghost_respawn_delay: float = 4.0   # delai avant reapparition d'un mange
    mega_spawn_chance: float = 0.01    # proba d'apparition du mega par niveau
    mega_score_multiplier: float = 1.5  # score x ce facteur sous mega

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
    flashlight_radius: float = 3.5          # rayon lumineux de depart
    flashlight_radius_min: float = 2.0      # plancher du rayon
    flashlight_radius_max: float = 8.0      # plafond du rayon
    flashlight_reduction_time: float = 1.0  # intervalle de retrecissement (s)
    flashlight_reduction_step: float = 1.1  # perte de rayon par intervalle
    flashlight_augmentation_step: float = 0.5  # gain de rayon par pacgum
    shine_duration: float = 8.0             # duree du shine (map eclairee)
    flashlight_augmentation_triggers: List[str] = ["ghosts", "super_pacgum"]


class HardcoreRuleSet(RuleSet):
    hardcore_lives: int = 1        # vies (1 = une seule tentative)
    time_factor: float = 0.5       # temps de niveau x ce facteur
    no_super_pacgums: bool = True  # retirer les super-pacgums


class RogueliteRuleSet(RuleSet):
    bonus_multiplier: int = 1


class TwoPlayerRuleSet(RuleSet):
    control_switch_time_range: List[int] = (10, 20)
