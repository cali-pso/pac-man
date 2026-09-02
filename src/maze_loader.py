from typing import Any, List, Optional, Tuple

_MazeGenerator: Any = None
try:
    from mazegenerator import MazeGenerator as _MazeGenerator  # type: ignore
except Exception:
    try:
        import mazegenerator as _mg  # type: ignore
        _MazeGenerator = getattr(_mg, "MazeGenerator", None)
    except Exception:
        _MazeGenerator = None


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
        if _MazeGenerator is None:
            raise ImportError(
                "Paquet 'mazegenerator' introuvable. Verifie l'install "
                "(uv add ...whl) et le nom d'import reel du module."
            )
        self._Gen = _MazeGenerator

    def load(
        self,
        width: int,
        height: int,
        seed: int = 42,
        perfect: bool = False,
    ) -> Maze:
        gen = self._build(width, height, seed, perfect)
        cells = self._extract_cells(gen)
        entry = self._as_xy(getattr(gen, "maze_entry", None))
        exit_ = self._as_xy(getattr(gen, "maze_exit", None))
        return Maze(cells, entry, exit_)

    def _build(self, width: int, height: int, seed: int,
               perfect: bool) -> Any:
        try:
            return self._Gen(size=(width, height), perfect=perfect, seed=seed)
        except TypeError:
            for kwargs in (
                {"size": (width, height), "perfect": perfect},
                {"size": (width, height)},
            ):
                try:
                    g = self._Gen(**kwargs)
                    if hasattr(g, "generate"):
                        try:
                            g.generate(seed=seed)
                        except TypeError:
                            try:
                                g.generate(seed)
                            except Exception:
                                pass
                    return g
                except TypeError:
                    continue
            raise

    def _extract_cells(self, gen: Any) -> List[List[int]]:
        for attr in ("maze", "grid", "cells"):
            data = getattr(gen, attr, None)
            if callable(data):
                try:
                    data = data()
                except Exception:
                    data = None
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
