"""Couche audio neutre : le reste du jeu demande "joue tel son" sans savoir
quelle lib ni quel fichier il y a derriere.

Si aucune lib audio n'est installee OU si le fichier est absent, tout passe
en mode silencieux SANS erreur : le jeu tourne quand meme.

A placer dans src/audio.py

Pour activer le son plus tard :
  1. deposer le fichier (ex. assets/sounds/intro.ogg)
  2. installer une lib :  uv add pygame   (ou :  uv add simpleaudio)
Rien d'autre a changer dans le code.
"""

from __future__ import annotations

import os
from typing import Optional

# --- Detection de la lib audio disponible (best effort) -----------------
_BACKEND: Optional[str] = None
try:
    import pygame  # type: ignore

    _BACKEND = "pygame"
except Exception:
    try:
        import simpleaudio  # type: ignore

        _BACKEND = "simpleaudio"
    except Exception:
        _BACKEND = None


class AudioManager:
    """Gere la musique et les effets. Silencieux si aucun backend/fichier."""

    def __init__(self, sound_dir: str = "assets/sounds") -> None:
        self.sound_dir = sound_dir
        self.enabled = _BACKEND is not None
        self._pygame_ready = False
        self._current = None  # objet play en cours (simpleaudio)

        if _BACKEND == "pygame":
            try:
                pygame.mixer.init()
                self._pygame_ready = True
            except Exception:
                self.enabled = False

    # --- Utilitaires -------------------------------------------------------

    def _find(self, name: str) -> Optional[str]:
        """Cherche un fichier son par nom (sans extension) dans sound_dir.

        Retourne le 1er chemin existant, sinon None.
        """
        for ext in (".ogg", ".mp3", ".wav"):
            path = os.path.join(self.sound_dir, name + ext)
            if os.path.isfile(path):
                return path
        return None

    # --- Musique (boucle de fond) -----------------------------------------

    def play_music(self, name: str, loop: bool = True) -> None:
        """Lance une musique de fond. No-op si indisponible."""
        if not self.enabled:
            return
        path = self._find(name)
        if path is None:
            return
        try:
            if _BACKEND == "pygame" and self._pygame_ready:
                pygame.mixer.music.load(path)
                pygame.mixer.music.play(-1 if loop else 0)
            elif _BACKEND == "simpleaudio" and path.endswith(".wav"):
                wave = simpleaudio.WaveObject.from_wave_file(path)
                self._current = wave.play()
        except Exception:
            # On ne laisse jamais l'audio casser le jeu.
            pass

    def stop_music(self) -> None:
        """Arrete la musique de fond. No-op si indisponible."""
        if not self.enabled:
            return
        try:
            if _BACKEND == "pygame" and self._pygame_ready:
                pygame.mixer.music.stop()
            elif _BACKEND == "simpleaudio" and self._current is not None:
                self._current.stop()
                self._current = None
        except Exception:
            pass

    # --- Effets ponctuels --------------------------------------------------

    def play_sound(self, name: str) -> None:
        """Joue un effet ponctuel (deplacement, konami, etc.)."""
        if not self.enabled:
            return
        path = self._find(name)
        if path is None:
            return
        try:
            if _BACKEND == "pygame" and self._pygame_ready:
                pygame.mixer.Sound(path).play()
            elif _BACKEND == "simpleaudio" and path.endswith(".wav"):
                simpleaudio.WaveObject.from_wave_file(path).play()
        except Exception:
            pass
