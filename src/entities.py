from abc import ABC, abstractmethod
from enum import Enum, auto

class EntityState(Enum):
    NORMAL = auto()
    POWERED = auto()
    DEAD = auto()

class Entity(ABC):
    """
    Base blueprint for all moving maze objects.
    Inherits from ABC to prevent direct instantiation of a generic Entity.
    """
    def __init__(self, start_x: int, start_y: int, color: int, playable: bool = False):
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

    def reset_position(self) -> None:
        """Returns the entity to its original starting point."""
        self.x = self.spawn_x
        self.y = self.spawn_y
        self.dir_x, self.dir_y = 0, 0
        self.next_dir_x, self.next_dir_y = 0, 0

    @abstractmethod
    def update(self, maze_cells: list) -> None:
        """
        Must be implemented by subclasses to define specific movement logic.
        """
        pass

class PacMan(Entity):
    def __init__(self, start_x: int, start_y: int):
        # Calls the parent constructor with super()
        # 0xFFFF00 is the PAC_COLOR from the original codebase
        super().__init__(start_x, start_y, color=0xFFFF00, playable=True)

    def update(self, maze_cells: list) -> None:
        # Player-specific grid movement and collision logic goes here
        pass
