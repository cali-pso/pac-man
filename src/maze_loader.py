from typing import Any, List, Optional, Tuple
from mazegenerator import MazeGenerator


class Maze:
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
        self.cells = cells
        self.rows = len(cells)
        self.cols = len(cells[0]) if cells else 0
        self.entry = entry
        self.exit = exit_

    def has_wall(self, x: int, y: int, side: int) -> bool:
        return bool(self.cells[y][x] & side)


class MazeLoader:
    def __init__(self) -> None:
        pass

    def load(
        self,
        size: Tuple[int, int],
        seed: int = 42,
    ) -> Maze:
        maze_gen = MazeGenerator(
            size=size, perfect=False, seed=seed
        )
        cells = self._extract_cells(maze_gen)
        entry = self._as_xy(maze_gen.maze_entry)
        exit_ = self._as_xy(maze_gen.maze_exit)
        return Maze(cells, entry, exit_)

    def _extract_cells(self, maze_gen: Any) -> List[List[int]]:
        data = maze_gen.maze
        if data:
            return [list(row) for row in data]
        raise AttributeError(
            "Grille du maze introuvable (essaye .maze / .grid / .cells)."
        )

    @staticmethod
    def _as_xy(val: Any) -> Optional[Tuple[int, int]]:
        if val is None:
            return None
        try:
            return (int(val[0]), int(val[1]))
        except Exception:
            return None
