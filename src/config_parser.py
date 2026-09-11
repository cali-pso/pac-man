"""Configuration loading: read the JSON (with comments) into rule sets."""

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
    """Parses the game configuration file into per-mode rule sets."""

    def __init__(self) -> None:
        """Create the parser (stateless)."""

    def load_config(self, config_path: str) -> Dict[str, RuleSet]:
        """Read ``config_path`` and return a rule set per game mode.

        Comments (``#``, ``//`` and ``/* */``) are stripped before the JSON
        is parsed.
        """
        with open(config_path, "r") as f:
            raw_data = f.read()

        raw_data = re.sub(r"/\*.*?\*/", "", raw_data, flags=re.DOTALL)
        raw_data = re.sub(r"(//|#).*", "", raw_data)

        config_dict = json.loads(raw_data)
        rulesets: Dict[str, RuleSet] = {
            "Normal": RuleSet(**config_dict.get("normal_mode", {})),
            "Shadow": ShadowRuleSet(**config_dict.get("shadow_mode", {})),
            "Hardcore": HardcoreRuleSet(
                **config_dict.get("hardcore_mode", {})
            ),
            "Roguelite": RogueliteRuleSet(
                **config_dict.get("roguelite_mode", {})
            ),
            "2 Players": TwoPlayerRuleSet(
                **config_dict.get("2_player_mode", {})
            ),
        }
        return rulesets
