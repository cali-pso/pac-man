from __future__ import annotations
import os
from typing import Optional
import pygame


class AudioManager:
    """Gere la musique et les effets. Silencieux si aucun backend/fichier."""

    def __init__(self, sound_dir: str = "src/assets/sounds/") -> None:
        self.sound_dir = sound_dir
        self.enabled = True
        self._pygame_ready = False

        try:
            pygame.mixer.init()
            self._pygame_ready = True
        except Exception:
            self.enabled = False

    def _find(self, name: str) -> Optional[str]:
        """Construit le chemin d'un son et verifie qu'il existe."""
        path = os.path.join(self.sound_dir, name)
        return path if os.path.isfile(path) else None

    # --- Musique (boucle de fond) -----------------------------------------

    def play_music(self, name: str, loop: bool = True) -> None:
        if not self.enabled:
            return
        path = self._find(name)
        if path is None:
            return
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(-1 if loop else 0)
        except Exception:
            pass

    def stop_music(self) -> None:
        if not self.enabled:
            return
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

    # --- Effets ponctuels --------------------------------------------------

    def play_sound(self, name: str) -> None:
        if not self.enabled:
            return
        path = self._find(name)
        if path is None:
            return
        try:
            pygame.mixer.Sound(path).play()
        except Exception:
            pass
