"""Audio manager for background music and sound effects (pygame)."""

from __future__ import annotations

import os
from typing import Optional

import pygame


class AudioManager:
    """Plays music and sound effects; stays silent if audio is unavailable."""

    def __init__(self, sound_dir: str = "src/assets/sounds/") -> None:
        """Initialise the pygame mixer, disabling audio on failure."""
        self.sound_dir = sound_dir
        self.enabled = True
        self._pygame_ready = False
        try:
            pygame.mixer.init()
            self._pygame_ready = True
        except Exception:
            self.enabled = False

    def _find(self, name: str) -> Optional[str]:
        """Return the path of a sound file if it exists, else None."""
        path = os.path.join(self.sound_dir, name)
        return path if os.path.isfile(path) else None

    def play_music(self, name: str, loop: bool = True) -> None:
        """Load and play a background music track (looping by default)."""
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
        """Stop the currently playing background music."""
        if not self.enabled:
            return
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

    def play_sound(self, name: str) -> None:
        """Play a one-shot sound effect."""
        if not self.enabled:
            return
        path = self._find(name)
        if path is None:
            return
        try:
            pygame.mixer.Sound(path).play()
        except Exception:
            pass
