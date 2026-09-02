from typing import Any
from mlx import Mlx
from src.menu_manager import MenuManager
from src.config_parser import ConfigParser
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
        self.state = GameState.INTRO
        self.menu = MenuManager(
            self.mlx, self.mlx_ptr, self.win_ptr, self.state
        )
        config_parser = ConfigParser()
        self.rulesets = config_parser.load_config("config.json")

    # --- Hooks -------------------------------------------------------------

    def _key_hook_menu(self, keycode: int, menu: MenuManager) -> None:
        menu.handle_key(keycode, self.state)
        self.state = menu.state

    # -----------------------------------------------------------------------

    def _draw_grid(self) -> None:
        for gx in range(0, self.width, CELL):
            for y in range(self.height):
                self.mlx.mlx_pixel_put(
                    self.mlx_ptr, self.win_ptr, gx, y, Color.GRAY
                )
        for gy in range(0, self.height, CELL):
            for x in range(self.width):
                self.mlx.mlx_pixel_put(
                    self.mlx_ptr, self.win_ptr, x, gy, Color.GRAY
                )

    def run(self) -> None:
        try:
            self._draw_grid()
            self.mlx.mlx_string_put(
                self.mlx_ptr,
                self.win_ptr,
                16,
                24,
                Color.YELLOW,
                "ESC to quit, any for menu",
            )
        except Exception as exc:
            print("Dessin ignore (a corriger plus tard):", exc)

        self.menu.render()
        self.mlx.mlx_key_hook(self.win_ptr, self._key_hook_menu, self.menu)

        self.mlx.mlx_loop(self.mlx_ptr)

        # Nettoyage apres sortie de boucle
        try:
            self.mlx.mlx_destroy_window(self.mlx_ptr, self.win_ptr)
        except Exception:
            pass
        try:
            self.mlx.mlx_release(self.mlx_ptr)
        except Exception:
            pass
