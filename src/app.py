from typing import Any
from mlx import Mlx
from src.menu_manager import MenuManager
from src.utils import Color, Key, GameState
from src.utils import quit

CELL: int = 40



class App:
    """Encapsule l'instance MLX et l'etat minimal du test."""

    def __init__(self, width: int, height: int, title: str) -> None:
        self.width = width
        self.height = height
        self.mlx = Mlx()
        # mlx_init() retourne le pointeur d'instance, requis partout ensuite.
        self.ptr = self.mlx.mlx_init()
        self.win = self.mlx.mlx_new_window(self.ptr, self.width, self.height, title)
        self.menu = MenuManager(self.mlx, self.ptr, self.win)

    # --- Hooks -------------------------------------------------------------

    def on_key(self, keycode: int, menu: MenuManager) -> None:
        menu.handle_key(keycode)

    # --- Dessin ------------------------------------------------------------

    def draw_grid(self) -> None:
        """Dessine les lignes de la grille (leger : lignes seulement)."""
        for gx in range(0, self.width, CELL):
            for y in range(self.height):
                self.mlx.mlx_pixel_put(self.ptr, self.win, gx, y, Color.GRAY)
        for gy in range(0, self.height, CELL):
            for x in range(self.width):
                self.mlx.mlx_pixel_put(self.ptr, self.win, x, gy, Color.GRAY)

    # --- Boucle ------------------------------------------------------------

    def run(self) -> None:
        # Dessin (nice-to-have : ne doit pas empecher de tester Echap)
        try:
            self.draw_grid()
            self.mlx.mlx_string_put(
                self.ptr, self.win, 16, 24, Color.YELLOW, "ESC pour quitter"
            )
        except Exception as exc:
            print("Dessin ignore (a corriger plus tard):", exc)
        # Certaines versions vulkan ont besoin d'un sync pour afficher.
        try:
            self.mlx.mlx_do_sync(self.ptr)
        except Exception:
            pass

        
        self.mlx.mlx_key_hook(self.win, self.on_key, self.menu)

        self.mlx.mlx_loop(self.ptr)

        # Nettoyage apres sortie de boucle
        try:
            self.mlx.mlx_destroy_window(self.ptr, self.win)
        except Exception:
            pass
        try:
            self.mlx.mlx_release(self.ptr)
        except Exception:
            pass

