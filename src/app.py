from typing import Any
from mlx import Mlx
from src.menu_manager import MenuManager
from src.intro import IntroScene
from src.audio import AudioManager
from src.utils import Color, Key, GameState

CELL: int = 40


class App:
    """
    Master class that initializes the Mlx instance and orchestrates the loop
    """

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

    # --- Transitions -------------------------------------------------------

    def _go_to_menu(self) -> None:
        self.audio.stop_music()
        self.audio.play_music("menu")
        self.state = GameState.MAIN_MENU
        self.menu.state = GameState.MAIN_MENU
        self.menu.selected_index = 0
        self.menu.render()

    # --- Hooks -------------------------------------------------------------

    def _key_hook(self, keycode: int, param: Any = None) -> int:
        if self.state == GameState.INTRO:
            self.intro.skip()
            self._go_to_menu()
            return 0
        self.menu.handle_key(keycode, self.state)
        self.state = self.menu.state
        return 0
 
    def _loop_hook(self, *args: Any) -> int:
        if self.state == GameState.INTRO:
            if self.intro.update():
                self._go_to_menu()
        return 0

    # -----------------------------------------------------------------------

    def run(self) -> None:
        self.audio.play_music("intro")
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
