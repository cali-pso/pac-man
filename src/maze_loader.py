"""Adapter around the assigned A-Maze-ing package.

Wraps ``MazeGenerator`` and exposes a simple ``Maze`` object (a grid of
wall-bit cells plus entry/exit coordinates) for the rest of the game.
"""

import random
from typing import Any, List, Optional, Tuple

from mazegenerator import MazeGenerator


class Maze:
    """A generated maze: a grid of cells with walls encoded as bits."""

    WALL_N = 1
    WALL_E = 2
    WALL_S = 4
    WALL_W = 8

    def __init__(
        self,
        cells: List[List[int]],
        entry: Optional[Tuple[int, int]] = None,
        exit_: Optional[Tuple[int, int]] = None,
    ) -> None:
        """Store the cell grid and the entry/exit coordinates."""
        self.cells = cells
        self.rows = len(cells)
        self.cols = len(cells[0]) if cells else 0
        self.entry = entry
        self.exit = exit_

    def has_wall(self, x: int, y: int, side: int) -> bool:
        """Return whether cell (x, y) has a wall on the given side."""
        return bool(self.cells[y][x] & side)


class MazeLoader:
    """Loads mazes from the external generator into ``Maze`` objects."""

    def __init__(self) -> None:
        """Create the loader (stateless)."""

    def load(self, size: Tuple[int, int], seed: int = 42) -> Maze:
        """Generate a maze of the given size and seed, and adapt it.

        The generator seeds Python's global RNG for reproducibility, so we
        reset it afterwards to keep the rest of the game non-deterministic.
        """
        maze_gen = MazeGenerator(size=size, perfect=False, seed=seed)
        random.seed()
        cells = self._extract_cells(maze_gen)
        entry = self._as_xy(maze_gen.maze_entry)
        exit_ = self._as_xy(maze_gen.maze_exit)
        return Maze(cells, entry, exit_)

    def _extract_cells(self, maze_gen: Any) -> List[List[int]]:
        """Return the generator grid as a list of lists of ints."""
        data = maze_gen.maze
        if data:
            return [list(row) for row in data]
        raise AttributeError("Maze grid not found on the generator.")

    @staticmethod
    def _as_xy(val: Any) -> Optional[Tuple[int, int]]:
        """Convert a coordinate-like value into an (x, y) tuple, or None."""
        if val is None:
            return None
        try:
            return (int(val[0]), int(val[1]))
        except Exception:
            return None
