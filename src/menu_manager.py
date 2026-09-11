"""Menu screens: main menu, mode selection, high scores and instructions."""

from typing import List, Optional

from mlx import Mlx
from src.utils import Color, Key, GameState, WIDTH, HEIGHT, quit, center_x_str
from src.highscore import PAGES, HighscoreStore
from src.mode_2players import SUBMODES


class MenuManager:
    """Draws the menus and handles their keyboard navigation."""

    def __init__(
        self,
        mlx_inst: Mlx,
        mlx_ptr: object,
        win_ptr: object,
        state: GameState,
        highscores: Optional[HighscoreStore] = None,
    ) -> None:
        """Store the MLX handles and initialise the menu state."""
        self.mlx = mlx_inst
        self.mlx_ptr = mlx_ptr
        self.win_ptr = win_ptr
        self.highscores = highscores
        self.hs_index = 0

        self.state: GameState = GameState.MAIN_MENU
        self.selected_index = 0
        self.chosen_mode: Optional[str] = None
        self.sub2p = False
        self.sub2p_index = 0
        self.sub2p_options = SUBMODES

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
        """Draw the screen matching the current menu state."""
        if self.state == GameState.PLAYING:
            return
        self.mlx.mlx_clear_window(self.mlx_ptr, self.win_ptr)
        if self.state == GameState.MAIN_MENU:
            self._draw_main_menu()
        elif self.state == GameState.MODE_MENU:
            if self.sub2p:
                self._draw_2p_submenu()
            else:
                self._draw_mode_menu()
        elif self.state == GameState.MENU_HIGHSCORES:
            self._draw_highscores()
        elif self.state == GameState.MENU_INSTRUCTIONS:
            self._draw_instructions()

    # --- Menu lists --------------------------------------------------------

    def _draw_list(
        self, title: str, options: List[str], selected: int
    ) -> None:
        """Draw a centered title and a vertical list with a cursor."""

        self.mlx.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            center_x_str(title),
            int(HEIGHT / 4),
            int(Color.GREEN),
            title,
        )
        start_y = int(HEIGHT / 3)
        spacing = 30
        for i, option in enumerate(options):
            selected_now = i == selected
            color = Color.YELLOW if selected_now else Color.WHITE
            prefix = "> " if selected_now else "  "
            text = f"{prefix}{option}"
            self.mlx.mlx_string_put(
                self.mlx_ptr,
                self.win_ptr,
                center_x_str(text),
                start_y + (i * spacing),
                color,
                text,
            )

    def _draw_main_menu(self) -> None:
        """Draw the main menu."""
        self._draw_list(
            "=== PAC-MAN ===", self.main_options, self.selected_index
        )

    def _draw_mode_menu(self) -> None:
        """Draw the mode-selection menu."""
        self._draw_list(
            "=== CHOOSE MODE ===", self.mode_options, self.selected_index
        )

    def _draw_2p_submenu(self) -> None:
        """Draw the two-player sub-menu."""
        self._draw_list(
            "=== 2 PLAYERS ===", self.sub2p_options, self.sub2p_index
        )
        hint = "ESC to go back"
        self.mlx.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            center_x_str(hint),
            int(HEIGHT / 3) + len(self.sub2p_options) * 30 + 20,
            int(Color.GRAY),
            hint,
        )

    # --- High scores (paged, side by side) ---------------------------------

    @staticmethod
    def _center_at(text: str, center_x: int) -> int:
        """Return the X to center ``text`` around ``center_x`` (9px font)."""
        return max(0, center_x - (len(text) * 9) // 2)

    def _draw_table(self, mode: str, center_x: int, top_y: int) -> None:
        """Draw one high-score table centered around ``center_x``."""
        self.mlx.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            self._center_at(mode, center_x),
            top_y,
            int(Color.YELLOW),
            mode,
        )
        entries = self.highscores.top(mode) if self.highscores else []
        if not entries:
            txt = "(empty)"
            self.mlx.mlx_string_put(
                self.mlx_ptr,
                self.win_ptr,
                self._center_at(txt, center_x),
                top_y + 26,
                int(Color.GRAY),
                txt,
            )
            return
        for i, (name, score) in enumerate(entries, start=1):
            text = f"{i:>2}. {name} - {score}"
            self.mlx.mlx_string_put(
                self.mlx_ptr,
                self.win_ptr,
                self._center_at(text, center_x),
                top_y + i * 20,
                int(Color.WHITE),
                text,
            )

    def _draw_highscores(self) -> None:
        """Draw the current high-score page (one or several tables)."""
        page_title, modes = PAGES[self.hs_index]
        title = f"HIGHSCORES - {page_title}"
        self.mlx.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            center_x_str(title),
            int(HEIGHT / 6),
            int(Color.YELLOW),
            title,
        )
        switch = "<  Left / Right : change page  >"
        self.mlx.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            center_x_str(switch),
            int(HEIGHT / 6) + 22,
            int(Color.GRAY),
            switch,
        )
        top_y = int(HEIGHT / 3)
        if len(modes) == 1:
            self._draw_table(modes[0], WIDTH // 2, top_y)
        else:
            col_w = WIDTH // len(modes)
            for ci, m in enumerate(modes):
                self._draw_table(m, ci * col_w + col_w // 2, top_y)
        footer = "Press ESC to return to Menu"
        self.mlx.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            center_x_str(footer),
            HEIGHT - 30,
            int(Color.CYAN),
            footer,
        )

    def _draw_instructions(self) -> None:
        """Draw the instructions screen."""
        title = "INSTRUCTIONS"
        self.mlx.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            center_x_str(title),
            int(HEIGHT / 4),
            int(Color.YELLOW),
            title,
        )
        lines = [
            "- Move: Arrow keys or WASD",
            "- Eat pacgums to win the level",
            "- Avoid ghosts unless powered up",
            "- ESC to pause",
            "- To activate cheat mode, enter the Konami code",
            "- Konami code: up-up-down-down-left-right-left-right-b-a",
        ]
        start_y = int(HEIGHT / 3)
        for i, line in enumerate(lines):
            self.mlx.mlx_string_put(
                self.mlx_ptr,
                self.win_ptr,
                center_x_str(line),
                start_y + (i * 25),
                int(Color.WHITE),
                line,
            )
        footer = "Press ESC to return to Menu"
        self.mlx.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            center_x_str(footer),
            start_y + 150,
            int(Color.CYAN),
            footer,
        )

    # --- Input -------------------------------------------------------------

    def handle_key(self, keycode: int, state: GameState) -> None:
        """Dispatch a key press to the handler of the current state."""
        if state == GameState.MAIN_MENU:
            if keycode in (Key.UP, Key.Wb):
                self.selected_index = (self.selected_index - 1) % len(
                    self.main_options
                )
            elif keycode in (Key.DOWN, Key.Sb):
                self.selected_index = (self.selected_index + 1) % len(
                    self.main_options
                )
            elif keycode in (Key.ENTER, Key.SPACE):
                self._execute_main_menu_action()
            elif keycode == Key.ESC:
                quit(self.mlx, self.mlx_ptr)

        elif state == GameState.MODE_MENU:
            if self.sub2p:
                self._handle_2p_submenu(keycode)
            else:
                self._handle_mode_menu(keycode)

        elif state == GameState.MENU_HIGHSCORES:
            if keycode in (Key.LEFT, Key.Ab):
                self.hs_index = (self.hs_index - 1) % len(PAGES)
            elif keycode in (Key.RIGHT, Key.Db):
                self.hs_index = (self.hs_index + 1) % len(PAGES)
            elif keycode == Key.ESC:
                self.state = GameState.MAIN_MENU

        elif state in (GameState.MENU_INSTRUCTIONS, GameState.PLAYING):
            self.state = state
            if keycode == Key.ESC:
                self.state = GameState.MAIN_MENU

        self.render()

    def _handle_mode_menu(self, keycode: int) -> None:
        """Handle navigation in the mode-selection menu."""
        if keycode in (Key.UP, Key.Wb):
            self.selected_index = (self.selected_index - 1) % len(
                self.mode_options
            )
        elif keycode in (Key.DOWN, Key.Sb):
            self.selected_index = (self.selected_index + 1) % len(
                self.mode_options
            )
        elif keycode in (Key.ENTER, Key.SPACE):
            self._execute_mode_menu_action()
        elif keycode == Key.ESC:
            self.state = GameState.MAIN_MENU

    def _handle_2p_submenu(self, keycode: int) -> None:
        """Handle navigation in the two-player sub-menu."""
        if keycode in (Key.UP, Key.Wb):
            self.sub2p_index = (self.sub2p_index - 1) % len(self.sub2p_options)
        elif keycode in (Key.DOWN, Key.Sb):
            self.sub2p_index = (self.sub2p_index + 1) % len(self.sub2p_options)
        elif keycode in (Key.ENTER, Key.SPACE):
            self.chosen_mode = self.sub2p_options[self.sub2p_index]
            self.sub2p = False
            self.state = GameState.PLAYING
        elif keycode == Key.ESC:
            self.sub2p = False

    def _execute_main_menu_action(self) -> None:
        """Run the selected main-menu entry."""
        choice = self.main_options[self.selected_index]
        if choice == "Start Game":
            self.state = GameState.MODE_MENU
            self.selected_index = 0
            self.sub2p = False
        elif choice == "View Highscores":
            self.state = GameState.MENU_HIGHSCORES
            self.hs_index = 0
        elif choice == "Instructions":
            self.state = GameState.MENU_INSTRUCTIONS
        elif choice == "Exit":
            quit(self.mlx, self.mlx_ptr)

    def _execute_mode_menu_action(self) -> None:
        """Run the selected mode entry (or open the 2-player sub-menu)."""
        choice = self.mode_options[self.selected_index]
        if choice == "2 Players":
            self.sub2p = True
            self.sub2p_index = 0
        else:
            self.chosen_mode = choice
            self.state = GameState.PLAYING
