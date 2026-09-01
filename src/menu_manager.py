from typing import List, Tuple
from mlx import Mlx
from src.utils import Color, Key, GameState, WIDTH, HEIGHT, quit


class MenuManager:
    def __init__(
        self,
        mlx_inst: Mlx,
        mlx_ptr: object,
        win_ptr: object,
        state: GameState,
    ) -> None:
        self.mlx = mlx_inst
        self.mlx_ptr = mlx_ptr
        self.win_ptr = win_ptr

        self.state: GameState = GameState.MAIN_MENU
        self.selected_index = 0
        self.main_options = [
            "Start Game",
            "View Highscores",
            "Instructions",
            "Exit",
        ]
        self.mode_options = [
            "Normal",
            "Hardcore",
            "Shadow",
            "Roguelite",
            "2 Players",
        ]

    def render(self) -> None:
        self.mlx.mlx_clear_window(self.mlx_ptr, self.win_ptr)

        if self.state == GameState.MAIN_MENU:
            self._draw_main_menu()
        elif self.state == GameState.MODE_MENU:
            self._draw_mode_menu()
        elif self.state == GameState.MENU_HIGHSCORES:
            self._draw_highscores()
        elif self.state == GameState.MENU_INSTRUCTIONS:
            self._draw_instructions()
        elif self.state == GameState.PLAYING:
            self._draw_game_placeholder()

    def _draw_main_menu(self) -> None:
        # Title
        self.mlx.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            int(WIDTH / 1.95 - WIDTH / 7.8),
            int(HEIGHT / 4),
            int(Color.GREEN),
            "=== PAC-MAN ===",
        )

        # Options
        start_y = int(HEIGHT / 3)
        spacing = 30
        for i, option in enumerate(self.main_options):
            is_selected = i == self.selected_index
            color = Color.YELLOW if is_selected else Color.WHITE
            prefix = "> " if is_selected else "  "

            self.mlx.mlx_string_put(
                self.mlx_ptr,
                self.win_ptr,
                int(WIDTH / 1.95 - WIDTH / 8),
                start_y + (i * spacing),
                color,
                f"{prefix}{option}",
            )


    def _draw_mode_menu(self) -> None:
        # Title
        self.mlx.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            int(WIDTH / 1.95 - WIDTH / 7.8),
            int(HEIGHT / 4),
            int(Color.GREEN),
            "=== CHOOSE MODE ===",
        )

        # Options
        start_y = int(HEIGHT / 3)
        spacing = 30
        for i, option in enumerate(self.mode_options):
            is_selected = i == self.selected_index
            color = Color.YELLOW if is_selected else Color.WHITE
            prefix = "> " if is_selected else "  "

            self.mlx.mlx_string_put(
                self.mlx_ptr,
                self.win_ptr,
                int(WIDTH / 1.95 - WIDTH / 8),
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

    def _draw_game_placeholder(self, mode: str) -> None:
        self.mlx.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            120,
            140,
            Color.YELLOW,
            f"New {mode} game running...",
        )
        self.mlx.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            90,
            180,
            Color.GRAY,
            "Press ESC to return to main menu",
        )

    def handle_key(self, keycode: int, state: GameState) -> None:
        """Dispatches key events using the Key IntEnum."""

        if state == GameState.MAIN_MENU:
            if keycode in (Key.UP, Key.W):
                self.selected_index = (self.selected_index - 1) % len(
                    self.main_options
                )
            elif keycode in (Key.DOWN, Key.S):
                self.selected_index = (self.selected_index + 1) % len(
                    self.main_options
                )
            elif keycode in (Key.ENTER, Key.SPACE):
                self._execute_main_menu_action()
            elif keycode == Key.ESC:
                quit(self.mlx, self.mlx_ptr)

        elif state == GameState.MODE_MENU:
            if keycode in (Key.UP, Key.W):
                self.selected_index = (self.selected_index - 1) % len(
                    self.mode_options
                )
            elif keycode in (Key.DOWN, Key.S):
                self.selected_index = (self.selected_index + 1) % len(
                    self.mode_options
                )
            elif keycode in (Key.ENTER, Key.SPACE):
                self._execute_mode_menu_action()
            elif keycode == Key.ESC:
                self.state = GameState.MAIN_MENU

        elif state in (
            GameState.MENU_HIGHSCORES,
            GameState.MENU_INSTRUCTIONS,
            GameState.PLAYING,
        ):
            self.state = state
            if keycode == Key.ESC:
                self.state = GameState.MAIN_MENU

        self.render()

    def _execute_main_menu_action(self) -> None:
        choice = self.main_options[self.selected_index]
        if choice == "Start Game":
            self.state = GameState.MODE_MENU
            self.selected_index = 0
        elif choice == "View Highscores":
            self.state = GameState.MENU_HIGHSCORES
        elif choice == "Instructions":
            self.state = GameState.MENU_INSTRUCTIONS
        elif choice == "Exit":
            quit(self.mlx, self.mlx_ptr)

    def _execute_mode_menu_action(self) -> None:
        choice = self.mode_options[self.selected_index]
        self.state = GameState.PLAYING

