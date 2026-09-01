import os

from typing import List, Tuple
from mlx import Mlx
from src.utils import Color, Key, GameState
from src.utils import quit





class MenuManager:
    def __init__(
        self, mlx_inst: Mlx, mlx_ptr: object, win_ptr: object
    ) -> None:
        self.mlx = mlx_inst
        self.mlx_ptr = mlx_ptr
        self.win_ptr = win_ptr

        self.state: GameState = GameState.MAIN_MENU
        self.selected_index = 0
        self.options = [
            "Start Game",
            "View Highscores",
            "Instructions",
            "Exit",
        ]

    def render(self) -> None:
        self.mlx.mlx_clear_window(self.mlx_ptr, self.win_ptr)

        if self.state == GameState.MAIN_MENU:
            self._draw_main_menu()
        elif self.state == GameState.HIGHSCORES:
            self._draw_highscores()
        elif self.state == GameState.INSTRUCTIONS:
            self._draw_instructions()
        elif self.state == GameState.PLAYING:
            self._draw_game_placeholder()

    def _draw_main_menu(self) -> None:
        # Title
        self.mlx.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            160,
            60,
            int(Color.YELLOW),
            "=== PAC-MAN ===",
        )

        # Options
        start_y = 120
        spacing = 30
        for i, option in enumerate(self.options):
            is_selected = i == self.selected_index
            color = Color.YELLOW if is_selected else Color.WHITE
            prefix = "> " if is_selected else "  "

            self.mlx.mlx_string_put(
                self.mlx_ptr,
                self.win_ptr,
                140,
                start_y + (i * spacing),
                color,
                f"{prefix}{option}",
            )

    def _draw_highscores(self) -> None:
        self.mlx.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            150,
            40,
            Color.YELLOW,
            "TOP 10 HIGHSCORES",
        )

        mock_scores: List[Tuple[str, int]] = [
            ("Sannaka", 1110),
            ("foliole", 20),
            ("Marmelade", 20),
            ("goldfish", 20),
        ]

        start_y = 80
        for i, (name, score) in enumerate(mock_scores, start=1):
            self.mlx.mlx_string_put(
                self.mlx_ptr,
                self.win_ptr,
                120,
                start_y + (i * 22),
                Color.WHITE,
                f"{i}. {name:<10} - {score} pts",
            )

        self.mlx.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            110,
            260,
            Color.CYAN,
            "Press ESC to return to Menu",
        )

    def _draw_instructions(self) -> None:
        self.mlx.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            160,
            40,
            Color.YELLOW,
            "INSTRUCTIONS",
        )
        lines = [
            "- Move: Arrow keys or WASD",
            "- Eat pacgums to win the level",
            "- Avoid ghosts unless powered up",
            "- Press P to pause game",
        ]
        for i, line in enumerate(lines):
            self.mlx.mlx_string_put(
                self.mlx_ptr,
                self.win_ptr,
                60,
                80 + (i * 25),
                Color.WHITE,
                line,
            )

        self.mlx.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            110,
            260,
            Color.CYAN,
            "Press ESC to return to Menu",
        )

    def _draw_game_placeholder(self) -> None:
        self.mlx.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            120,
            140,
            Color.YELLOW,
            "GAME RUNNING...",
        )
        self.mlx.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            90,
            180,
            Color.GRAY,
            "Press ESC to return to Menu",
        )

    def handle_key(self, keycode: int) -> None:
        """Dispatches key events using the Key IntEnum."""
        if self.state == GameState.MAIN_MENU:
            if keycode in (Key.UP, Key.W):
                self.selected_index = (self.selected_index - 1) % len(
                    self.options
                )
            elif keycode in (Key.DOWN, Key.S):
                self.selected_index = (self.selected_index + 1) % len(
                    self.options
                )
            elif keycode in (Key.ENTER, Key.SPACE):
                self._execute_menu_action()
            elif keycode == Key.ESC:
                quit(self.mlx, self.mlx_ptr)
                

        elif self.state in (
            GameState.HIGHSCORES,
            GameState.INSTRUCTIONS,
            GameState.PLAYING,
        ):
            if keycode == Key.ESC:
                self.state = GameState.MAIN_MENU

        self.render()

    def _execute_menu_action(self) -> None:
        choice = self.options[self.selected_index]
        if choice == "Start Game":
            self.state = GameState.PLAYING
        elif choice == "View Highscores":
            self.state = GameState.HIGHSCORES
        elif choice == "Instructions":
            self.state = GameState.INSTRUCTIONS
        elif choice == "Exit":
            quit(self.mlx, self.mlx_ptr)
