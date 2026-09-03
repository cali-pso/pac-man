from abc import ABC, abstractmethod
from enum import Enum, auto
import random
from typing import List, Optional, Set, Tuple

WALL_N, WALL_E, WALL_S, WALL_W = 1, 2, 4, 8
_DIR_WALL = {
    (0, -1): WALL_N,
    (1, 0): WALL_E,
    (0, 1): WALL_S,
    (-1, 0): WALL_W,
}
_DIRS: List[Tuple[int, int]] = [(0, -1), (1, 0), (0, 1), (-1, 0)]

GHOST_RANDOMNESS = 0.25


class EntityState(Enum):
    NORMAL = auto()
    POWERED = auto()   # fantome comestible
    DEAD = auto()


class Entity(ABC):
    def __init__(self, start_x: int, start_y: int, color: int,
                 playable: bool = False):
        self.x = start_x
        self.y = start_y
        self.spawn_x = start_x
        self.spawn_y = start_y
        self.dir_x, self.dir_y = 0, 0
        self.next_dir_x, self.next_dir_y = 0, 0
        self.color = color
        self.playable = playable
        self.can_move = True
        self.state = EntityState.NORMAL
        self.dead_until = 0.0

    def reset_position(self) -> None:
        self.x = self.spawn_x
        self.y = self.spawn_y
        self.dir_x, self.dir_y = 0, 0
        self.next_dir_x, self.next_dir_y = 0, 0

    @staticmethod
    def can_step(cells: list, x: int, y: int, dx: int, dy: int,
                 rows: int, cols: int) -> bool:
        wall = _DIR_WALL.get((dx, dy))
        if not wall:
            return False
        if cells[y][x] & wall:
            return False
        nx, ny = x + dx, y + dy
        return 0 <= nx < cols and 0 <= ny < rows

    @abstractmethod
    def update(self, cells: list, rows: int, cols: int,
               target: Optional[Tuple[int, int]] = None,
               occupied: Optional[Set[Tuple[int, int]]] = None) -> None:
        ...


class PacMan(Entity):
    def __init__(self, start_x: int, start_y: int):
        super().__init__(start_x, start_y, color=0xFFFF00, playable=True)

    def try_move(self, dx: int, dy: int, cells: list,
                 rows: int, cols: int) -> bool:
        if not self.can_move:
            return False
        if not self.can_step(cells, self.x, self.y, dx, dy, rows, cols):
            return False
        self.dir_x, self.dir_y = dx, dy
        self.x += dx
        self.y += dy
        return True

    def update(self, cells: list, rows: int, cols: int,
               target: Optional[Tuple[int, int]] = None,
               occupied: Optional[Set[Tuple[int, int]]] = None) -> None:
        pass  # pilote au clavier


class Ghost(Entity):
    def __init__(self, start_x: int, start_y: int, color: int):
        super().__init__(start_x, start_y, color=color)

    def update(self, cells: list, rows: int, cols: int,
               target: Optional[Tuple[int, int]] = None,
               occupied: Optional[Set[Tuple[int, int]]] = None) -> None:
        if not self.can_move or self.state == EntityState.DEAD:
            return  # un fantome mort ne bouge pas
        occupied = occupied or set()
        back = (-self.dir_x, -self.dir_y)
        options = [
            d for d in _DIRS
            if self.can_step(cells, self.x, self.y, d[0], d[1], rows, cols)
        ]
        if not options:
            return
        forward = [d for d in options if d != back] or options
        # Evite de se poser sur un autre fantome si possible
        free = [
            d for d in forward
            if (self.x + d[0], self.y + d[1]) not in occupied
        ] or forward

        if target is not None and random.random() > GHOST_RANDOMNESS:
            tx, ty = target
            key = lambda d: abs(self.x + d[0] - tx) + abs(self.y + d[1] - ty)
            # Comestible -> fuit (max distance) ; sinon -> poursuit (min)
            if self.state == EntityState.POWERED:
                choice = max(free, key=key)
            else:
                choice = min(free, key=key)
        else:
            choice = random.choice(free)

        self.dir_x, self.dir_y = choice
        self.x += choice[0]
        self.y += choice[1]
