import json
from typing import Set
from models import (
    RuleSet,
    ShadowRuleSet,
    HardcoreRuleSet,
    RogueliteRuleSet,
    TwoPlayerRuleSet,
)


class ConfigParser:
    def __init__(self) -> None:
        pass

    def load_config(self, config_path: str) -> Set[RuleSet]:
        with open(config_path, "r") as f:
            config_dict = json.load(f)
        rulesets = list()
        rulesets.append(RuleSet(**config_dict.get("normal_mode", None)))
        rulesets.append(ShadowRuleSet(**config_dict.get("shadow_mode", None)))
        rulesets.append(
            HardcoreRuleSet(**config_dict.get("hardcore_mode", None))
        )
        rulesets.append(
            RogueliteRuleSet(**config_dict.get("roguelite_mode", None))
        )
        rulesets.append(
            TwoPlayerRuleSet(**config_dict.get("2_player_mode", None))
        )
        return rulesets
