"""Etat d'une partie : labyrinthe, Pac-Man, pacgums, super-pacgums,
fantomes, score, vies, timer, mode POWERED (fantomes comestibles).

A placer dans src/game_session.py
"""

from __future__ import annotations

import random
import time
from typing import List, Optional, Set, Tuple

from src.entities import Entity, EntityState, Ghost, PacMan
from src.maze_loader import Maze
from src import mega_pacgum

ALL_WALLS = Maze.WALL_N | Maze.WALL_E | Maze.WALL_S | Maze.WALL_W  # 15
GHOST_COLORS = [0xFF0000, 0xFFB8FF, 0x00FFFF, 0xFFB852]
POWER_DURATION = 8.0  # secondes de comestibilite apres un super-pacgum
GHOST_RESPAWN_DELAY = 4.0  # secondes avant qu'un fantome mange revienne


class GameSession:
    def __init__(
        self,
        maze: Maze,
        points_per_pacgum: int = 10,
        points_per_super_pacgum: int = 50,
        points_per_ghost: int = 200,
        lives: int = 3,
        max_time: int = 90,
        start_score: int = 0,
        no_supers: bool = False,
        mode: str = "Normal",
        power_duration: float = POWER_DURATION,
        ghost_respawn_delay: float = GHOST_RESPAWN_DELAY,
    ) -> None:
        self.maze = maze
        self.points_per_pacgum = points_per_pacgum
        self.points_per_super_pacgum = points_per_super_pacgum
        self.points_per_ghost = points_per_ghost
        self.lives = lives
        self.max_time = max_time
        self.no_supers = no_supers
        self.mode = mode
        self.power_duration = power_duration
        self.ghost_respawn_delay = ghost_respawn_delay
        self.start_time = time.time()
        self._paused_at = 0.0
        self.score = start_score
        self.won = False
        self.game_over = False
        self.last_ate = False
        self.last_ate_super = False

        self.powered = False
        self.power_end = 0.0

        # Mega pacgum
        self.mega_pos: Optional[Tuple[int, int]] = None
        self.mega_active = False
        self.last_ate_mega = False
        self._mega_frozen_left = 0

        # Versus : fantome pilote par le joueur 2
        self.player_ghost_index: Optional[int] = None
        self.ghost_dir: Tuple[int, int] = (0, 0)
        self.ghost_next_dir: Tuple[int, int] = (0, 0)

        sx, sy = self._find_spawn()
        self.pacman = PacMan(sx, sy)
        self.pacgums: Set[Tuple[int, int]] = self._seed_pacgums()
        self.super_pacgums: Set[Tuple[int, int]] = self._seed_supers()
        self.ghosts: List[Ghost] = self._spawn_ghosts()
        self._maybe_spawn_mega()

        # cheats
        self.cheat = False
        self.invicible = False

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
                if self._is_open(x, y) and (x, y) != start and random.random() < 0.80:
                    gums.add((x, y))
        return gums

    def _seed_supers(self) -> Set[Tuple[int, int]]:
        if self.no_supers:
            return set()  # mode hardcore : pas de super-pacgums
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

    # --- Pause -------------------------------------------------------------

    def pause(self) -> None:
        """Gele le temps (timer, power, reapparition des fantomes)."""
        if self._paused_at == 0.0:
            self._paused_at = time.time()

    def resume(self) -> None:
        """Reprend : decale tous les horodatages de la duree de pause."""
        if self._paused_at == 0.0:
            return
        delta = time.time() - self._paused_at
        self.start_time += delta
        self.power_end += delta
        for g in self.ghosts:
            g.dead_until += delta
        self._paused_at = 0.0

    def _maybe_spawn_mega(self) -> None:
        """Tire au sort l'apparition du mega selon le mode."""
        if random.random() >= mega_pacgum.spawn_chance_for(self.mode):
            return
        # Le place sur une case de pacgum au hasard (donc atteignable).
        if self.pacgums:
            pos = random.choice(list(self.pacgums))
            self.pacgums.discard(pos)
            self.mega_pos = pos

    # --- Timer & power -----------------------------------------------------

    def time_left(self) -> int:
        if self.mega_active:
            return self._mega_frozen_left  # timer gele par le mega
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
        self.power_end = time.time() + self.power_duration
        for g in self.ghosts:
            if g.state != EntityState.DEAD:
                g.state = EntityState.POWERED  # ne ressuscite pas les morts

    def update_power(self) -> bool:
        """Termine le mode POWERED si le temps est ecoule.
        Retourne True si le mode vient de se terminer (pour la musique)."""
        if self.powered and time.time() >= self.power_end:
            self.powered = False
            for g in self.ghosts:
                if g.state != EntityState.DEAD:
                    g.state = (
                        EntityState.POWERED
                        if self.mega_active
                        else EntityState.NORMAL
                    )
            return True
        return False

    def _score_mult(self) -> float:
        return mega_pacgum.SCORE_MULTIPLIER if self.mega_active else 1.0

    # --- Collision ---------------------------------------------------------

    def resolve_collisions(self, pac_fx: float, pac_fy: float,
                           ghost_prog: float) -> bool:
        """Collision basee sur les positions AFFICHEES (interpolees), pour
        coller a ce que le joueur voit. Retourne True si Pac-Man est mort."""
        if self.won or self.game_over or self.invicible:
            return False
        for g in self.ghosts:
            if g.state == EntityState.DEAD:
                continue
            gfx = g.prev_x + (g.x - g.prev_x) * ghost_prog
            gfy = g.prev_y + (g.y - g.prev_y) * ghost_prog
            if abs(gfx - pac_fx) < 0.5 and abs(gfy - pac_fy) < 0.5:
                if self._resolve_contact(g):
                    return True
        return False

    def _resolve_contact(self, g: Ghost) -> bool:
        """Contact confirme : mange le fantome (power/mega) ou perd une vie.
        Retourne True si Pac-Man meurt."""
        if self.powered or self.mega_active:
            self.score += int(self.points_per_ghost * self._score_mult())
            g.state = EntityState.DEAD
            if self.mega_active:
                g.dead_until = float("inf")  # mega : ne revient pas du niveau
            else:
                g.dead_until = time.time() + self.ghost_respawn_delay
            g.reset_position()
            return False
        self._hit()
        return True

    def _eat_mega(self) -> None:
        """Effets du mega : gel du timer, fantomes figes+comestibles, x1.5."""
        self.mega_pos = None
        self.mega_active = True
        self.last_ate_mega = True
        self._mega_frozen_left = max(
            0, int(self.max_time - (time.time() - self.start_time))
        )
        for g in self.ghosts:
            g.state = EntityState.POWERED  # comestibles
            g.can_move = False  # figes
            g.dir_x, g.dir_y = 0, 0

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
            self.ghost_dir = (0, 0)
            self.ghost_next_dir = (0, 0)

    # --- Pac-Man -----------------------------------------------------------

    def try_move(self, dx: int, dy: int) -> bool:
        self.last_ate = False
        self.last_ate_super = False
        self.last_ate_mega = False
        if self.won or self.game_over:
            return False
        moved = self.pacman.try_move(
            dx, dy, self.maze.cells, self.maze.rows, self.maze.cols
        )
        if not moved:
            return False
        pos = (self.pacman.x, self.pacman.y)
        mult = self._score_mult()
        if pos == self.mega_pos:
            self._eat_mega()
        elif pos in self.pacgums:
            self.pacgums.discard(pos)
            self.score += int(self.points_per_pacgum * mult)
            self.last_ate = True
        elif pos in self.super_pacgums:
            self.super_pacgums.discard(pos)
            self.score += int(self.points_per_super_pacgum * mult)
            self.last_ate_super = True
            self._enter_power()
        if not self.pacgums and not self.super_pacgums:
            self.won = True
        return True

    # --- Fantomes ----------------------------------------------------------

    def _respawn_dead(self) -> None:
        now = time.time()
        for g in self.ghosts:
            if g.state == EntityState.DEAD and now >= getattr(
                g, "dead_until", 0.0
            ):
                g.state = (
                    EntityState.POWERED if self.powered else EntityState.NORMAL
                )
                if getattr(g, "is_player", False):
                    self.ghost_dir = (0, 0)
                    self.ghost_next_dir = (0, 0)

    def set_player_ghost(self, index: int) -> None:
        """Designe le fantome pilote par J2 (Versus). Change a chaque niveau."""
        for gi, g in enumerate(self.ghosts):
            g.is_player = (gi == index)
        if 0 <= index < len(self.ghosts):
            self.player_ghost_index = index
        self.ghost_dir = (0, 0)
        self.ghost_next_dir = (0, 0)

    def set_ghost_direction(self, dx: int, dy: int) -> None:
        """Direction voulue par J2 pour son fantome (buffer de virage)."""
        self.ghost_next_dir = (dx, dy)

    def _move_player_ghost(self, g: Ghost) -> None:
        if not g.can_move or g.state == EntityState.DEAD:
            return
        cells, rows, cols = self.maze.cells, self.maze.rows, self.maze.cols
        nx, ny = self.ghost_next_dir
        if (nx or ny) and Entity.can_step(cells, g.x, g.y, nx, ny, rows, cols):
            self.ghost_dir = self.ghost_next_dir
        dx, dy = self.ghost_dir
        if (dx or dy) and Entity.can_step(cells, g.x, g.y, dx, dy, rows, cols):
            g.dir_x, g.dir_y = dx, dy
            g.x += dx
            g.y += dy

    def update_ghosts(self) -> None:
        if self.won or self.game_over:
            return
        self._respawn_dead()
        target = (self.pacman.x, self.pacman.y)
        for i, g in enumerate(self.ghosts):
            g.prev_x = g.x
            g.prev_y = g.y
            if getattr(g, "is_player", False):
                self._move_player_ghost(g)  # Versus : pilote par J2
                continue
            occupied = {(o.x, o.y) for o in self.ghosts if o is not g}
            g.update(
                self.maze.cells,
                self.maze.rows,
                self.maze.cols,
                target,
                occupied,
            )
