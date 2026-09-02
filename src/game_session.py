from __future__ import annotations

from typing import Tuple

from src.maze_loader import Maze

ALL_WALLS = Maze.WALL_N | Maze.WALL_E | Maze.WALL_S | Maze.WALL_W  # 15


class GameSession:
    def __init__(self, maze: Maze) -> None:
        self.maze = maze
        self.pac_x, self.pac_y = self._find_spawn()

    def _is_open(self, x: int, y: int) -> bool:
        return (self.maze.cells[y][x] & ALL_WALLS) != ALL_WALLS

    def _find_spawn(self) -> Tuple[int, int]:
        cx = self.maze.cols // 2
        cy = self.maze.rows // 2
        if self._is_open(cx, cy):
            return (cx, cy)
        for r in range(1, max(self.maze.cols, self.maze.rows)):
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    if max(abs(dx), abs(dy)) != r:
                        continue
                    x, y = cx + dx, cy + dy
                    if 0 <= x < self.maze.cols and 0 <= y < self.maze.rows:
                        if self._is_open(x, y):
                            return (x, y)
        return (cx, cy)

    def _can_move(self, x: int, y: int, dx: int, dy: int) -> bool:
        cell = self.maze.cells[y][x]
        if dx == 1:
            return not (cell & Maze.WALL_E)
        if dx == -1:
            return not (cell & Maze.WALL_W)
        if dy == 1:
            return not (cell & Maze.WALL_S)
        if dy == -1:
            return not (cell & Maze.WALL_N)
        return False

    def try_move(self, dx: int, dy: int) -> bool:
        """Tente d'avancer d'une case. Retourne True si Pac-Man a bouge."""
        if not self._can_move(self.pac_x, self.pac_y, dx, dy):
            return False
        nx, ny = self.pac_x + dx, self.pac_y + dy
        if 0 <= nx < self.maze.cols and 0 <= ny < self.maze.rows:
            self.pac_x, self.pac_y = nx, ny
            return True
        return False
