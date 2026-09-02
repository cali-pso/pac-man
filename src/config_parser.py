import json
import re
from typing import Dict
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

    def load_config(self, config_path: str) -> Dict[str, RuleSet]:
        with open(config_path, "r") as f:
            raw_data = f.read()

        raw_data = re.sub(r"/\*.*?\*/", "", raw_data, flags=re.DOTALL)
        raw_data = re.sub(r"(//|#).*", "", raw_data)

        config_dict = json.loads(raw_data)
        rulesets = {
            "Normal": RuleSet(**config_dict.get("normal_mode", None)),
            "Shadow": ShadowRuleSet(**config_dict.get("shadow_mode", None)),
            "Hardcore": HardcoreRuleSet(
                **config_dict.get("hardcore_mode", None)
            ),
            "Roguelite": RogueliteRuleSet(
                **config_dict.get("roguelite_mode", None)
            ),
            "2 Players": TwoPlayerRuleSet(
                **config_dict.get("2_player_mode", None)
            ),
        }
        return rulesets
