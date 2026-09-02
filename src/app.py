from typing import Any, Optional, Tuple
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
        config_parser = ConfigParser()
        self.rulesets = config_parser.load_config("config.json")
        self.state = GameState.INTRO
        self.intro = IntroScene(self.mlx, self.mlx_ptr, self.win_ptr)
        self.menu = MenuManager(
            self.mlx, self.mlx_ptr, self.win_ptr, self.state
        )
        self.maze_loader = MazeLoader()
        self.maze_renderer = MazeRenderer(
            self.mlx, self.mlx_ptr, self.win_ptr, self.width, self.height
        )

        self.session: Optional[GameSession] = None

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

    def _start_game(self, mode: str) -> None:
        self.audio.stop_music()
        self.audio.play_music("level.wav")
        try:
            ruleset = self._ruleset_for(mode)
            maze = self.maze_loader.load(
                (ruleset.width, ruleset.height), ruleset.seed
            )
            self.session = GameSession(maze)
            self.maze_renderer.prepare(maze)
            self.maze_renderer.render(self.session)
        except Exception as exc:
            print(str(exc))

    def _draw_error(self, msg: str) -> None:
        self.mlx.mlx_clear_window(self.mlx_ptr, self.win_ptr)
        self.mlx.mlx_string_put(
            self.mlx_ptr, self.win_ptr, 40, 60, 0xFF4444, "Maze error:"
        )
        self.mlx.mlx_string_put(
            self.mlx_ptr, self.win_ptr, 40, 90, 0xFFFFFF, msg[:140]
        )
        self.mlx.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            40,
            130,
            0x888888,
            "ESC to return to menu",
        )

    # --- Entrees en jeu ----------------------------------------------------

    @staticmethod
    def _dir_for(keycode: int) -> Optional[Tuple[int, int]]:
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
            # Un appui = une case. En maintenant, la repetition auto du
            # systeme fait avancer Pac-Man case par case.
            if self.session.try_move(*d):
                self.maze_renderer.render(self.session)

    # --- Hooks -------------------------------------------------------------

    def _key_hook(self, keycode: int, param: Any = None) -> int:
        if self.state == GameState.INTRO:
            self.intro.skip()
            self._go_to_menu()
            return 0
        elif self.state == GameState.PLAYING:
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
        return 0

    def run(self) -> None:
        self.audio.play_music("intro.wav")
        self.intro.render()

        self.mlx.mlx_key_hook(self.win_ptr, self._key_hook, 0)
        self.mlx.mlx_loop_hook(self.mlx_ptr, self._loop_hook, 0)

        self.mlx.mlx_loop(self.mlx_ptr)

        self.audio.stop_music()
        try:
            self.mlx.mlx_destroy_window(self.mlx_ptr, self.win_ptr)
        except Exception:
            pass
        try:
            self.mlx.mlx_release(self.mlx_ptr)
        except Exception:
            pass
