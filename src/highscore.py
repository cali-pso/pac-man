"""Persistent per-mode high-score storage (a single JSON file).

Robust to file errors. Keeps a top 10 per mode; names are at most 10
characters (alphanumeric and spaces) and scores are non-negative integers.
"""

import json
import os
from typing import Dict, List, Tuple

MAX_ENTRIES = 10
MAX_NAME_LEN = 10

Entry = Tuple[str, int]

# Storage keys / table order.
MODES = ["Normal", "Hardcore", "Shadow", "Roguelite",
         "Versus", "Coop", "Random"]

# High-score screen pages: (title, [modes shown side by side]).
PAGES = [
    ("Normal", ["Normal"]),
    ("Hardcore", ["Hardcore"]),
    ("Shadow", ["Shadow"]),
    ("Roguelite", ["Roguelite"]),
    ("2 Players", ["Versus", "Coop", "Random"]),
]


class HighscoreStore:
    """Loads, holds and saves the per-mode high-score tables."""

    def __init__(self, path: str = "highscores.json") -> None:
        """Load the tables from ``path`` (empty tables if unavailable)."""
        self.path = path
        self.by_mode: Dict[str, List[Entry]] = self._load()

    def _load(self) -> Dict[str, List[Entry]]:
        """Read and sanitise the tables, or return empty ones on error."""
        data: Dict[str, List[Entry]] = {m: [] for m in MODES}
        if not os.path.isfile(self.path):
            return data
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except (OSError, json.JSONDecodeError):
            return data
        if isinstance(raw, dict):
            for mode, entries in raw.items():
                data.setdefault(mode, [])
                data[mode] = self._sanitize(entries)
        return data

    def _sanitize(self, raw: object) -> List[Entry]:
        """Return a clean, sorted, truncated list of (name, score)."""
        clean: List[Entry] = []
        if isinstance(raw, list):
            for item in raw:
                try:
                    name = clean_name(str(item[0]))
                    score = int(item[1])
                except (TypeError, ValueError, IndexError, KeyError):
                    continue
                if name and score >= 0:
                    clean.append((name, score))
        clean.sort(key=lambda e: e[1], reverse=True)
        return clean[:MAX_ENTRIES]

    def save(self) -> None:
        """Write all tables to disk, ignoring write errors."""
        try:
            payload = {
                mode: [[n, s] for (n, s) in entries]
                for mode, entries in self.by_mode.items()
            }
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
        except OSError:
            pass

    def qualifies(self, mode: str, score: int) -> bool:
        """Return whether ``score`` enters the top 10 of ``mode``."""
        if score < 0:
            return False
        entries = self.by_mode.get(mode, [])
        if len(entries) < MAX_ENTRIES:
            return True
        return score > entries[-1][1]

    def add(self, mode: str, name: str, score: int) -> None:
        """Insert a score, sort, truncate to the top 10, and save."""
        name = clean_name(name) or "PLAYER"
        score = max(0, int(score))
        entries = self.by_mode.setdefault(mode, [])
        entries.append((name, score))
        entries.sort(key=lambda e: e[1], reverse=True)
        self.by_mode[mode] = entries[:MAX_ENTRIES]
        self.save()

    def top(self, mode: str) -> List[Entry]:
        """Return a copy of the top-10 list for ``mode``."""
        return list(self.by_mode.get(mode, []))


def clean_name(name: str) -> str:
    """Keep only alphanumerics and spaces, truncated to 10 characters."""
    kept = "".join(c for c in name if c.isalnum() or c == " ")
    return kept[:MAX_NAME_LEN].strip()
