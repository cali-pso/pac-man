"""Etat d'une partie : labyrinthe, Pac-Man, pacgums, super-pacgums,
fantomes, score, vies, timer, mode POWERED (fantomes comestibles).

A placer dans src/game_session.py
"""

from __future__ import annotations

import time
from typing import List, Set, Tuple

from src.entities import EntityState, Ghost, PacMan
from src.maze_loader import Maze

ALL_WALLS = Maze.WALL_N | Maze.WALL_E | Maze.WALL_S | Maze.WALL_W  # 15
GHOST_COLORS = [0xFF0000, 0xFFB8FF, 0x00FFFF, 0xFFB852]
POWER_DURATION = 8.0  # secondes de comestibilite apres un super-pacgum
GHOST_RESPAWN_DELAY = 4.0  # secondes avant qu'un fantome mange revienne


class GameSession:
    def __init__(self, maze: Maze, points_per_pacgum: int = 10,
                 points_per_super_pacgum: int = 50, points_per_ghost: int = 200,
                 lives: int = 3, max_time: int = 90,
                 start_score: int = 0) -> None:
        self.maze = maze
        self.points_per_pacgum = points_per_pacgum
        self.points_per_super_pacgum = points_per_super_pacgum
        self.points_per_ghost = points_per_ghost
        self.lives = lives
        self.max_time = max_time
        self.start_time = time.time()
        self.score = start_score
        self.won = False
        self.game_over = False
        self.last_ate = False
        self.last_ate_super = False

        self.powered = False
        self.power_end = 0.0

        sx, sy = self._find_spawn()
        self.pacman = PacMan(sx, sy)
        self.pacgums: Set[Tuple[int, int]] = self._seed_pacgums()
        self.super_pacgums: Set[Tuple[int, int]] = self._seed_supers()
        self.ghosts: List[Ghost] = self._spawn_ghosts()

    # --- Cases praticables -------------------------------------------------

    def _is_open(self, x: int, y: int) -> bool:
        return (self.maze.cells[y][x] & ALL_WALLS) != ALL_WALLS

    def _find_open_near(self, tx: int, ty: int) -> Tuple[int, int]:
        if self._is_open(tx, ty):
            return (tx, ty)
        for r in range(1, max(self.maze.cols, self.maze.rows)):
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    if max(abs(dx), abs(dy)) != r:
                        continue
                    x, y = tx + dx, ty + dy
                    if 0 <= x < self.maze.cols and 0 <= y < self.maze.rows:
                        if self._is_open(x, y):
                            return (x, y)
        return (tx, ty)

    def _find_spawn(self) -> Tuple[int, int]:
        return self._find_open_near(self.maze.cols // 2, self.maze.rows // 2)

    def _corners(self) -> List[Tuple[int, int]]:
        cols, rows = self.maze.cols, self.maze.rows
        raw = [(0, 0), (cols - 1, 0), (0, rows - 1), (cols - 1, rows - 1)]
        return [self._find_open_near(cx, cy) for (cx, cy) in raw]

    def _seed_pacgums(self) -> Set[Tuple[int, int]]:
        gums: Set[Tuple[int, int]] = set()
        start = (self.pacman.x, self.pacman.y)
        for y in range(self.maze.rows):
            for x in range(self.maze.cols):
                if self._is_open(x, y) and (x, y) != start:
                    gums.add((x, y))
        return gums

    def _seed_supers(self) -> Set[Tuple[int, int]]:
        supers: Set[Tuple[int, int]] = set()
        for pos in self._corners():
            supers.add(pos)
            self.pacgums.discard(pos)
        return supers

    def _spawn_ghosts(self) -> List[Ghost]:
        ghosts: List[Ghost] = []
        for i, (gx, gy) in enumerate(self._corners()):
            ghosts.append(Ghost(gx, gy, GHOST_COLORS[i % len(GHOST_COLORS)]))
        return ghosts

    # --- Timer & power -----------------------------------------------------

    def time_left(self) -> int:
        return max(0, int(self.max_time - (time.time() - self.start_time)))

    def power_time_left(self) -> int:
        return max(0, int(self.power_end - time.time())) if self.powered else 0

    def check_timeout(self) -> None:
        if self.won or self.game_over:
            return
        if self.time_left() <= 0:
            self.game_over = True

    def _enter_power(self) -> None:
        self.powered = True
        self.power_end = time.time() + POWER_DURATION
        for g in self.ghosts:
            g.state = EntityState.POWERED

    def update_power(self) -> bool:
        """Termine le mode POWERED si le temps est ecoule.
        Retourne True si le mode vient de se terminer (pour la musique)."""
        if self.powered and time.time() >= self.power_end:
            self.powered = False
            for g in self.ghosts:
                if g.state != EntityState.DEAD:
                    g.state = EntityState.NORMAL
            return True
        return False

    # --- Collision ---------------------------------------------------------

    def _touch(self, g: Ghost) -> bool:
        """Gere le contact Pac-Man / fantome. Retourne True si Pac-Man meurt."""
        if g.state == EntityState.DEAD:
            return False  # fantome en cours de reapparition : inoffensif
        if not (g.x == self.pacman.x and g.y == self.pacman.y):
            return False
        if self.powered:
            self.score += self.points_per_ghost
            g.state = EntityState.DEAD
            g.dead_until = time.time() + GHOST_RESPAWN_DELAY
            g.reset_position()  # attend au coin pendant le delai
            return False
        self._hit()
        return True

    def _hit(self) -> None:
        self.lives -= 1
        if self.lives <= 0:
            self.lives = 0
            self.game_over = True
        else:
            self.pacman.reset_position()
            for g in self.ghosts:
                g.reset_position()
                g.state = EntityState.NORMAL

    # --- Pac-Man -----------------------------------------------------------

    def try_move(self, dx: int, dy: int) -> bool:
        self.last_ate = False
        self.last_ate_super = False
        if self.won or self.game_over:
            return False
        moved = self.pacman.try_move(
            dx, dy, self.maze.cells, self.maze.rows, self.maze.cols
        )
        if not moved:
            return False
        pos = (self.pacman.x, self.pacman.y)
        if pos in self.pacgums:
            self.pacgums.discard(pos)
            self.score += self.points_per_pacgum
            self.last_ate = True
        elif pos in self.super_pacgums:
            self.super_pacgums.discard(pos)
            self.score += self.points_per_super_pacgum
            self.last_ate_super = True
            self._enter_power()
        if not self.pacgums and not self.super_pacgums:
            self.won = True
        for g in list(self.ghosts):
            if self._touch(g):
                break
        return True

    # --- Fantomes ----------------------------------------------------------

    def _respawn_dead(self) -> None:
        now = time.time()
        for g in self.ghosts:
            if g.state == EntityState.DEAD and now >= getattr(
                    g, "dead_until", 0.0):
                g.state = EntityState.POWERED if self.powered \
                    else EntityState.NORMAL

    def update_ghosts(self) -> None:
        if self.won or self.game_over:
            return
        self._respawn_dead()
        target = (self.pacman.x, self.pacman.y)
        for g in self.ghosts:
            g.prev_x = g.x
            g.prev_y = g.y
            occupied = {(o.x, o.y) for o in self.ghosts if o is not g}
            g.update(self.maze.cells, self.maze.rows, self.maze.cols,
                     target, occupied)
            if self._touch(g):
                return
