"""Highscores persistants par mode (un seul fichier JSON).
Robuste aux erreurs de fichier. Contraintes du sujet : top 10 par mode,
noms <= 10 caracteres (alphanumeriques + espaces), scores entiers >= 0.

Format disque : { "Normal": [["Seb", 1200], ...], "Hardcore": [...], ... }

A placer dans src/highscore.py
"""

from __future__ import annotations

import json
import os
from typing import Dict, List, Tuple

MAX_ENTRIES = 10
MAX_NAME_LEN = 10

Entry = Tuple[str, int]

# Ordre des tableaux (utilise pour la bascule gauche/droite au menu)
MODES = ["Normal", "Hardcore", "Shadow", "Roguelite", "2 Players"]


class HighscoreStore:
    def __init__(self, path: str = "highscores.json") -> None:
        self.path = path
        self.by_mode: Dict[str, List[Entry]] = self._load()

    # --- Chargement / sauvegarde ------------------------------------------

    def _load(self) -> Dict[str, List[Entry]]:
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
        try:
            payload = {
                mode: [[n, s] for (n, s) in entries]
                for mode, entries in self.by_mode.items()
            }
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
        except OSError:
            pass

    # --- Operations --------------------------------------------------------

    def qualifies(self, mode: str, score: int) -> bool:
        if score < 0:
            return False
        entries = self.by_mode.get(mode, [])
        if len(entries) < MAX_ENTRIES:
            return True
        return score > entries[-1][1]

    def add(self, mode: str, name: str, score: int) -> None:
        name = clean_name(name) or "PLAYER"
        score = max(0, int(score))
        entries = self.by_mode.setdefault(mode, [])
        entries.append((name, score))
        entries.sort(key=lambda e: e[1], reverse=True)
        self.by_mode[mode] = entries[:MAX_ENTRIES]
        self.save()

    def top(self, mode: str) -> List[Entry]:
        return list(self.by_mode.get(mode, []))


def clean_name(name: str) -> str:
    kept = "".join(c for c in name if c.isalnum() or c == " ")
    return kept[:MAX_NAME_LEN].strip()
