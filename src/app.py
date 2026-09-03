import random
import time
from typing import Any, Optional, Tuple
from mlx import Mlx
from src.menu_manager import MenuManager
from src.intro import IntroScene
from src.audio import AudioManager
from src.config_parser import ConfigParser
from src.maze_loader import MazeLoader
from src.maze_renderer import MazeRenderer
from src.game_session import GameSession
from src.highscore import HighscoreStore
from src.utils import GameState, Key, center_x_str

GHOST_INTERVAL: float = 0.28   # cadence des fantomes
STEP_INTERVAL: float = 0.11    # cadence de Pac-Man en maintien (sa "vitesse")
HOLD_GRACE: float = 0.15       # delai sans repetition avant de considerer relache
BACKSPACE: int = 65288


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
        self.highscores = HighscoreStore("highscores.json")
        self.state = GameState.INTRO
        self.intro = IntroScene(self.mlx, self.mlx_ptr, self.win_ptr)
        self.menu = MenuManager(
            self.mlx, self.mlx_ptr, self.win_ptr, self.state, self.highscores
        )
        self.maze_loader = MazeLoader()
        self.maze_renderer = MazeRenderer(
            self.mlx, self.mlx_ptr, self.win_ptr, self.width, self.height
        )

        self.session: Optional[GameSession] = None
        self._last_ghost: float = 0.0
        self._finish_handled: bool = False
        self._entering_name: bool = False
        self._name_buffer: str = ""
        self._current_mode: str = "Normal"
        self._level: int = 1
        self._total_levels: int = 1
        # Deplacement Pac-Man (maintien)
        self._move_dir: Tuple[int, int] = (0, 0)
        self._repeating: bool = False
        self._move_until: float = 0.0
        self._last_step: float = 0.0

    # --- Transitions -------------------------------------------------------

    def _reset_move(self) -> None:
        self._move_dir = (0, 0)
        self._repeating = False
        self._move_until = 0.0
        self._last_step = 0.0

    def _go_to_menu(self) -> None:
        self.audio.stop_music()
        self.audio.play_music("menu.wav")
        self.session = None
        self._entering_name = False
        self._name_buffer = ""
        self._reset_move()
        self.state = GameState.MAIN_MENU
        self.menu.state = GameState.MAIN_MENU
        self.menu.selected_index = 0
        self.menu.render()

    def _start_game(self, mode: str) -> None:
        self.audio.stop_music()
        self.audio.play_music("level.wav")
        self._current_mode = mode
        try:
            ruleset = self.rulesets[mode]
            maze = self.maze_loader.load(
                (ruleset.width, ruleset.height), ruleset.seed
            )
            self._level = 1
            self._total_levels = max(1, int(getattr(ruleset, "level", 10)))
            self.session = GameSession(
                maze,
                ruleset.points_per_pacgum,
                ruleset.points_per_super_pacgum,
                ruleset.points_per_ghost,
                ruleset.lives,
                ruleset.max_level_time,
            )
            self.session.level = self._level
            self._finish_handled = False
            self._entering_name = False
            self._name_buffer = ""
            self._reset_move()
            self.maze_renderer.prepare(maze)
            self._render_game()
            self._last_ghost = time.time()
        except Exception as exc:
            print(str(exc))

    # --- Progression de niveau --------------------------------------------

    def _next_level(self) -> None:
        self._level += 1
        ruleset = self.rulesets[self._current_mode]
        seed = random.randint(1, 2_000_000_000)  # niveaux 2+ : aleatoire
        maze = self.maze_loader.load((ruleset.width, ruleset.height), seed)
        self.session = GameSession(
            maze,
            ruleset.points_per_pacgum,
            ruleset.points_per_super_pacgum,
            ruleset.points_per_ghost,
            self.session.lives,
            ruleset.max_level_time,
            start_score=self.session.score,
        )
        self.session.level = self._level
        self.maze_renderer.prepare(maze)
        self._last_ghost = time.time()
        self._render_game()

    def _progress(self) -> None:
        s = self.session
        if s is None:
            return
        if s.won and self._level < self._total_levels:
            self._next_level()
            return
        if s.won or s.game_over:
            self._on_finish()
        self._render_game()

    # --- Fin de partie -----------------------------------------------------

    def _on_finish(self) -> None:
        if self._finish_handled or self.session is None:
            return
        self._finish_handled = True
        self.audio.stop_music()
        if self.session.game_over:
            self.audio.play_sound("death.wav")
        self._entering_name = self.highscores.qualifies(
            self._current_mode, self.session.score)
        self._name_buffer = ""

    # --- Rendu -------------------------------------------------------------

    def _put_center(self, text: str, y: int, color: int) -> None:
        self.mlx.mlx_string_put(
            self.mlx_ptr, self.win_ptr, center_x_str(text), y, color, text
        )

    def _render_game(self) -> None:
        if self.session is None:
            return
        if self.session.won or self.session.game_over:
            self._render_finish()
            return
        self.maze_renderer.render(self.session)

    def _render_finish(self) -> None:
        self.mlx.mlx_clear_window(self.mlx_ptr, self.win_ptr)
        s = self.session
        cy = self.height // 2
        if self._entering_name:
            self._put_center("NEW HIGHSCORE!", cy - 60, 0xFFFF00)
            self._put_center(f"Score: {s.score}", cy - 30, 0xFFFFFF)
            self._put_center(f"Name: {self._name_buffer}_", cy, 0x00FFFF)
            self._put_center(
                "Type your name  -  ENTER to confirm  -  ESC to skip",
                cy + 40, 0x888888,
            )
        else:
            if s.won:
                self._put_center(f"YOU WIN!  Score: {s.score}", cy - 10,
                                 0xFFFF00)
            else:
                self._put_center(f"GAME OVER  Score: {s.score}", cy - 10,
                                 0xFF4444)
            self._put_center("Press ESC to return to menu", cy + 20, 0x888888)
        try:
            self.mlx.mlx_do_sync(self.mlx_ptr)
        except Exception:
            pass

    def _finished(self) -> bool:
        return self.session is not None and (
            self.session.won or self.session.game_over
        )

    # --- Deplacement Pac-Man ----------------------------------------------

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

    def _step_pac(self) -> None:
        if self.session is None or self._finished():
            return
        dx, dy = self._move_dir
        if dx == 0 and dy == 0:
            return
        if self.session.try_move(dx, dy):
            if self.session.last_ate:
                self.audio.play_sound("pacgum.wav")
            elif self.session.last_ate_super:
                self.audio.play_sound("super_pacgum.wav")
                self.audio.stop_music()
                self.audio.play_music("super_active.wav")
            else:
                self.audio.play_sound("move.wav")  # deplacement sans manger
            self._progress()

    # --- Entrees -----------------------------------------------------------

    def _handle_name_key(self, keycode: int) -> None:
        if keycode == Key.ENTER:
            if self.session is not None:
                self.highscores.add(
                    self._current_mode, self._name_buffer,
                    self.session.score)
            self._go_to_menu()
        elif keycode == Key.ESC:
            self._go_to_menu()
        elif keycode == BACKSPACE:
            self._name_buffer = self._name_buffer[:-1]
            self._render_finish()
        elif 32 <= keycode <= 126:
            ch = chr(keycode)
            if (ch.isalnum() or ch == " ") and len(self._name_buffer) < 10:
                self._name_buffer += ch
                self._render_finish()

    def _handle_play_key(self, keycode: int) -> None:
        if self._entering_name:
            self._handle_name_key(keycode)
            return
        if self._finished():
            if keycode == Key.ESC:
                self._go_to_menu()
            return
        if keycode == Key.ESC:
            self._go_to_menu()
            return
        if self.session is None:
            return
        d = self._dir_for(keycode)
        if d is None:
            return
        now = time.time()
        if d != self._move_dir:
            # Nouvelle direction (tap ou changement) : un pas immediat.
            self._move_dir = d
            self._repeating = False
            self._last_step = now
            self._step_pac()
        else:
            # Meme direction re-pressee = auto-repeat -> maintien.
            self._repeating = True
            self._move_until = now + HOLD_GRACE

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
            self._start_game(self.menu.chosen_mode)
        return 0

    def _loop_hook(self, *args: Any) -> int:
        if self.state == GameState.INTRO:
            if self.intro.update():
                self._go_to_menu()
            return 0
        if (self.state == GameState.PLAYING and self.session is not None
                and not self._finished()):
            now = time.time()
            # Pac-Man en maintien : avance a SA cadence tant que ca repete
            if self._repeating and self._move_dir != (0, 0):
                if now >= self._move_until:
                    self._repeating = False
                    self._move_dir = (0, 0)
                elif now - self._last_step >= STEP_INTERVAL:
                    self._last_step = now
                    self._step_pac()
            # Fin du mode POWERED
            if self.session is not None and not self._finished():
                if self.session.update_power():
                    self.audio.stop_music()
                    self.audio.play_music("level.wav")
            # Fantomes
            if (self.session is not None and not self._finished()
                    and now - self._last_ghost >= GHOST_INTERVAL):
                self._last_ghost = now
                self.session.check_timeout()
                if not self.session.game_over:
                    self.session.update_ghosts()
                self._progress()
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
