import time
from typing import Any, Optional
from mlx import Mlx
from src.menu_manager import MenuManager
from src.intro import IntroScene
from src.audio import AudioManager
from src.config_parser import ConfigParser
from src.maze_loader import MazeLoader
from src.maze_renderer import MazeRenderer
from src.game_session import GameSession
from src.models import (
    RuleSet,
    ShadowRuleSet,
    HardcoreRuleSet,
    RogueliteRuleSet,
    TwoPlayerRuleSet,
)
from src.utils import GameState, Key

STEP_INTERVAL: float = 0.12  # secondes entre deux deplacements d'une case

# Evenement et masques X11
EV_KEY_RELEASE: int = 3
MASK_KEY_PRESS: int = 1
MASK_KEY_RELEASE: int = 2


class App:

    def __init__(self, width: int, height: int, title: str) -> None:
        self.width = width
        self.height = height
        self.mlx = Mlx()
        self.mlx_ptr = self.mlx.mlx_init()
        self.win_ptr = self.mlx.mlx_new_window(
            self.mlx_ptr, self.width, self.height, title
        )
        self.audio = AudioManager()
        self.state = GameState.INTRO
        self.menu = MenuManager(
            self.mlx, self.mlx_ptr, self.win_ptr, self.state
        )
        self.intro = IntroScene(self.mlx, self.mlx_ptr, self.win_ptr)

        self.maze_renderer = MazeRenderer(
            self.mlx, self.mlx_ptr, self.win_ptr, self.width, self.height
        )
        self.maze_loader: Optional[MazeLoader] = None
        try:
            self.maze_loader = MazeLoader()
        except Exception as exc:
            print("[maze] loader indisponible:", exc)

        self.rulesets = None
        try:
            self.rulesets = ConfigParser().load_config("config.json")
        except Exception as exc:
            print("[config] non chargee, defauts utilises:", exc)

        self.session: Optional[GameSession] = None
        self._last_step: float = 0.0

    # --- Transitions -------------------------------------------------------

    def _go_to_menu(self) -> None:
        self.audio.stop_music()
        self.audio.play_music("menu.wav")
        self.session = None
        self.state = GameState.MAIN_MENU
        self.menu.state = GameState.MAIN_MENU
        self.menu.selected_index = 0
        self.menu.render()

    def _ruleset_for(self, mode: Optional[str]) -> RuleSet:
        table = {
            "Normal": RuleSet,
            "Hardcore": HardcoreRuleSet,
            "Shadow": ShadowRuleSet,
            "Roguelite": RogueliteRuleSet,
            "2 Players": TwoPlayerRuleSet,
        }
        cls = table.get(mode or "Normal", RuleSet)
        default = cls()
        if self.rulesets:
            for rs in self.rulesets:
                if type(rs) is type(default):
                    return rs
        return default

    def _start_game(self, mode: Optional[str]) -> None:
        self.audio.stop_music()
        self.audio.play_music("level.wav")
        if self.maze_loader is None:
            self._draw_error("mazegenerator introuvable (voir install/import)")
            return
        try:
            rs = self._ruleset_for(mode)
            try:
                seed = int(rs.seed)
            except Exception:
                seed = 42
            maze = self.maze_loader.load(rs.width, rs.height, seed=seed)
            self.session = GameSession(maze)
            self.maze_renderer.prepare(maze)
            self.maze_renderer.render(self.session)
            self._last_step = time.time()
        except Exception as exc:
            self._draw_error(str(exc))

    def _draw_error(self, msg: str) -> None:
        self.mlx.mlx_clear_window(self.mlx_ptr, self.win_ptr)
        self.mlx.mlx_string_put(
            self.mlx_ptr, self.win_ptr, 40, 60, 0xFF4444, "Maze error:"
        )
        self.mlx.mlx_string_put(
            self.mlx_ptr, self.win_ptr, 40, 90, 0xFFFFFF, msg[:140]
        )
        self.mlx.mlx_string_put(
            self.mlx_ptr, self.win_ptr, 40, 130, 0x888888,
            "ESC to return to menu",
        )

    # --- Entrees en jeu ----------------------------------------------------

    @staticmethod
    def _dir_for(keycode: int) -> Optional[tuple]:
        if keycode in (Key.UP, Key.W):
            return (0, -1)
        if keycode in (Key.DOWN, Key.S):
            return (0, 1)
        if keycode in (Key.LEFT, Key.A):
            return (-1, 0)
        if keycode in (Key.RIGHT, Key.D):
            return (1, 0)
        return None

    def _handle_play_key(self, keycode: int) -> None:
        if keycode == Key.ESC:
            self._go_to_menu()
            return
        if self.session is None:
            return
        d = self._dir_for(keycode)
        if d is not None:
            self.session.set_direction(*d)

    def _key_release(self, keycode: int, *args: Any) -> int:
        if self.state != GameState.PLAYING or self.session is None:
            return 0
        d = self._dir_for(keycode)
        if d is not None:
            self.session.release_direction(*d)
        return 0

    # --- Hooks -------------------------------------------------------------

    def _key_hook(self, keycode: int, param: Any = None) -> int:
        if self.state == GameState.INTRO:
            self.intro.skip()
            self._go_to_menu()
            return 0
        if self.state == GameState.PLAYING:
            self._handle_play_key(keycode)
            return 0
        prev = self.state
        self.menu.handle_key(keycode, self.state)
        self.state = self.menu.state
        if prev != GameState.PLAYING and self.state == GameState.PLAYING:
            self._start_game(getattr(self.menu, "chosen_mode", None))
        return 0

    def _loop_hook(self, *args: Any) -> int:
        if self.state == GameState.INTRO:
            if self.intro.update():
                self._go_to_menu()
        elif self.state == GameState.PLAYING and self.session is not None:
            now = time.time()
            if now - self._last_step >= STEP_INTERVAL:
                self._last_step = now
                before = (self.session.pac_x, self.session.pac_y)
                self.session.step()
                if (self.session.pac_x, self.session.pac_y) != before:
                    self.maze_renderer.render(self.session)
        return 0

    def run(self) -> None:
        self.audio.play_music("intro.wav")
        self.intro.render()

        try:
            self.mlx.mlx_do_key_autorepeatoff(self.mlx_ptr)
        except Exception:
            pass

        # Appui : hook clavier standard.
        self.mlx.mlx_key_hook(self.win_ptr, self._key_hook, 0)
        # Relachement : KeyRelease (3) avec le BON masque (press|release = 3).
        try:
            self.mlx.mlx_hook(
                self.win_ptr, EV_KEY_RELEASE,
                MASK_KEY_PRESS | MASK_KEY_RELEASE,
                self._key_release, 0,
            )
        except Exception:
            pass
        self.mlx.mlx_loop_hook(self.mlx_ptr, self._loop_hook, 0)

        self.mlx.mlx_loop(self.mlx_ptr)

        try:
            self.mlx.mlx_do_key_autorepeaton(self.mlx_ptr)
        except Exception:
            pass
        self.audio.stop_music()
        try:
            self.mlx.mlx_destroy_window(self.mlx_ptr, self.win_ptr)
        except Exception:
            pass
        try:
            self.mlx.mlx_release(self.mlx_ptr)
        except Exception:
            pass