import time
import struct
from typing import Optional

from src.entities import EntityState
from src.game_session import GameSession
from src.maze_loader import Maze

WALL_COLOR: int = 0x5555FF
PAC_COLOR: int = 0xFFFF00
GUM_COLOR: int = 0xF0C0A0
SUPER_COLOR: int = 0xFFFFFF
FRIGHT_COLOR: int = 0x2222EE  # fantome comestible
BG_COLOR: int = 0x000000
HUD_COLOR: int = 0xFFFFFF
MARGIN: int = 30
THICK: int = 2
TOP_PAD: int = 34  # bande du haut reservee au HUD


class MazeRenderer:
    def __init__(
        self,
        mlx_inst: object,
        mlx_ptr: object,
        win_ptr: object,
        screen_w: int,
        screen_h: int,
    ) -> None:
        self.mlx = mlx_inst
        self.mlx_ptr = mlx_ptr
        self.win_ptr = win_ptr
        self.screen_w = screen_w
        self.screen_h = screen_h

        self._img: Optional[object] = None
        self._mvb: Optional[memoryview] = None
        self._template: Optional[bytearray] = None
        self._ready = False
        self.cell = 0
        self.iw = 0
        self.ih = 0
        self.mox = 0  # origine du labyrinthe dans l'image
        self.moy = 0
        self.size_line = 0
        self.bpp_bytes = 4
        self.endian = 0
        self._pac_b = b""
        self._gum_b = b""
        self._super_b = b""
        self._load_sprites()

    def _load_sprites(self) -> None:
        self.sprites = {"pacman": {}, "ghosts": {}}
        dirs = ["up", "down", "left", "right"]

        ghost_files = {
            0xFF0000: "blinky",
            0xFFB8FF: "pinky",
            0x00FFFF: "inky",
            0xFFB852: "clyde",
        }
        self.ghost_mapping = ghost_files
        for d in dirs:
            self.sprites["pacman"][d] = []
            for i in range(1, 4):
                path = f"src/assets/pacman-art/pacman-{d}/{i}.png"
                img = self.mlx.mlx_png_file_to_image(self.mlx_ptr, path)
                self.sprites["pacman"][d].append({"ptr": img[0], "w": img[1], "h": img[2]})
                
        # Same structural approach for ghosts:
        for name in ghost_files.values():
            path = f"src/assets/pacman-art/ghosts/{name}.png"
            img = self.mlx.mlx_png_file_to_image(self.mlx_ptr, path)
            self.sprites["ghosts"][name] = {"ptr": img[0], "w": img[1], "h": img[2]}
        path_blue = "src/assets/pacman-art/ghosts/blue_ghost.png"
        self.sprites["ghosts"]["powered"] = self.mlx.mlx_png_file_to_image(
            self.mlx_ptr, path_blue
        )

    def _flush(self) -> None:
        try:
            self.mlx.mlx_do_sync(self.mlx_ptr)
        except Exception:
            pass

    @staticmethod
    def _pack(color: int, endian: int) -> bytes:
        fmt = "<I" if endian == 0 else ">I"
        return struct.pack(fmt, 0xFF000000 | (color & 0xFFFFFF))

    def prepare(self, maze: Maze) -> None:
        self._ready = False
        self.mlx.mlx_clear_window(self.mlx_ptr, self.win_ptr)
        cols, rows = maze.cols, maze.rows
        if cols == 0 or rows == 0:
            return

        # Image plein ecran : HUD + labyrinthe + entites, tout rafraichi.
        iw = self.screen_w
        ih = self.screen_h
        avail_w = self.screen_w - 2 * MARGIN
        avail_h = self.screen_h - 2 * MARGIN - TOP_PAD
        cell = max(6, min(avail_w // cols, avail_h // rows))
        maze_w = cell * cols
        maze_h = cell * rows
        mox = (self.screen_w - maze_w) // 2
        moy = TOP_PAD + ((self.screen_h - TOP_PAD) - maze_h) // 2

        if self._img is not None:
            try:
                self.mlx.mlx_destroy_image(self.mlx_ptr, self._img)
            except Exception:
                pass

        img = self.mlx.mlx_new_image(self.mlx_ptr, iw, ih)
        data, bpp, size_line, endian = self.mlx.mlx_get_data_addr(img)
        bpp_bytes = bpp // 8

        wall_b = self._pack(WALL_COLOR, endian)
        bg_b = self._pack(BG_COLOR, endian)
        buf = bytearray(bg_b * (size_line * ih // bpp_bytes))

        def hline(x0: int, x1: int, y: int) -> None:
            if y < 0 or y >= ih:
                return
            x0 = max(0, x0)
            x1 = min(iw, x1)
            if x1 <= x0:
                return
            base = y * size_line + x0 * bpp_bytes
            buf[base : base + (x1 - x0) * bpp_bytes] = wall_b * (x1 - x0)

        def vline(x: int, y0: int, y1: int) -> None:
            if x < 0 or x >= iw:
                return
            y0 = max(0, y0)
            y1 = min(ih, y1)
            for yy in range(y0, y1):
                off = yy * size_line + x * bpp_bytes
                buf[off : off + bpp_bytes] = wall_b

        def hband(x0: int, x1: int, y: int) -> None:
            for t in range(THICK):
                hline(x0, x1, y + t)

        def vband(x: int, y0: int, y1: int) -> None:
            for t in range(THICK):
                vline(x + t, y0, y1)

        for y in range(rows):
            for x in range(cols):
                v = maze.cells[y][x]
                px = mox + x * cell
                py = moy + y * cell
                if v & Maze.WALL_N:
                    hband(px, px + cell, py)
                if v & Maze.WALL_W:
                    vband(px, py, py + cell)
                if x == cols - 1 and (v & Maze.WALL_E):
                    vband(px + cell, py, py + cell)
                if y == rows - 1 and (v & Maze.WALL_S):
                    hband(px, px + cell, py + cell)

        # buf contient fond noir + murs (statique). On garde aussi une
        # version fond-noir-seul pour le mode shadow (murs dynamiques).
        self._img = img
        self._mvb = data.cast("B")
        self._maze = maze
        self._bg_b = bg_b
        self._wall_b = wall_b
        self._template = buf  # fond + murs (mode normal)
        self.cell = cell
        self.iw = iw
        self.ih = ih
        self.mox = mox
        self.moy = moy
        self.size_line = size_line
        self.bpp_bytes = bpp_bytes
        self.endian = endian
        self._pac_b = self._pack(PAC_COLOR, endian)
        self._gum_b = self._pack(GUM_COLOR, endian)
        self._super_b = self._pack(SUPER_COLOR, endian)
        self._ready = True

    def _fill_dot(
        self, work: bytearray, cx: int, cy: int, r: int, color: bytes
    ) -> None:
        sl = self.size_line
        bb = self.bpp_bytes
        for dy in range(-r, r + 1):
            yy = cy + dy
            if yy < 0 or yy >= self.ih:
                continue
            span = int((r * r - dy * dy) ** 0.5)
            x0 = max(0, cx - span)
            x1 = min(self.iw - 1, cx + span)
            if x1 < x0:
                continue
            base = yy * sl + x0 * bb
            work[base : base + (x1 - x0 + 1) * bb] = color * (x1 - x0 + 1)

    def _draw_walls(self, work: bytearray, visible) -> None:
        """Dessine les murs dans work. visible(x, y) filtre par cellule
        (None-safe : si visible est None, tout est dessine)."""
        maze = self._maze
        cell = self.cell
        mox, moy = self.mox, self.moy
        sl = self.size_line
        bb = self.bpp_bytes
        wb = self._wall_b
        iw, ih = self.iw, self.ih

        def hband(x0, x1, y):
            x0 = max(0, x0)
            x1 = min(iw, x1)
            for t in range(THICK):
                yy = y + t
                if 0 <= yy < ih and x1 > x0:
                    base = yy * sl + x0 * bb
                    work[base : base + (x1 - x0) * bb] = wb * (x1 - x0)

        def vband(x, y0, y1):
            y0 = max(0, y0)
            y1 = min(ih, y1)
            for t in range(THICK):
                xx = x + t
                if 0 <= xx < iw:
                    for yy in range(y0, y1):
                        off = yy * sl + xx * bb
                        work[off : off + bb] = wb

        for y in range(maze.rows):
            for x in range(maze.cols):
                if visible is not None and not visible(x, y):
                    continue
                v = maze.cells[y][x]
                px = mox + x * cell
                py = moy + y * cell
                if v & Maze.WALL_N:
                    hband(px, px + cell, py)
                if v & Maze.WALL_W:
                    vband(px, py, py + cell)
                if x == maze.cols - 1 and (v & Maze.WALL_E):
                    vband(px + cell, py, py + cell)
                if y == maze.rows - 1 and (v & Maze.WALL_S):
                    hband(px, px + cell, py + cell)

    def render(
        self, session: GameSession, pac_prog: float, ghost_prog: float
    ) -> None:
        if not self._ready or self._mvb is None:
            return
        cell = self.cell
        half = cell // 2
        mox, moy = self.mox, self.moy

        # Mode shadow : ne revele que ce qui est dans la zone lumineuse.
        shadow = getattr(session, "shadow", None)
        px, py = session.pacman.x, session.pacman.y

        def visible(ex: int, ey: int) -> bool:
            return shadow is None or shadow.is_visible(ex, ey, px, py)

        if shadow is None:
            # Mode normal : murs deja graves dans le template (rapide).
            work = bytearray(self._template)
        else:
            # Mode shadow : fond noir + murs dessines selon la zone lumineuse.
            work = bytearray(
                self._bg_b * (self.size_line * self.ih // self.bpp_bytes)
            )
            self._draw_walls(work, visible)

        # Pacgums
        gum_r = max(1, cell // 8)
        for gx, gy in session.pacgums:
            if visible(gx, gy):
                self._fill_dot(
                    work,
                    mox + gx * cell + half,
                    moy + gy * cell + half,
                    gum_r,
                    self._gum_b,
                )

        # Super-pacgums (plus gros)
        super_r = max(2, cell // 3)
        for gx, gy in session.super_pacgums:
            if visible(gx, gy):
                self._fill_dot(
                    work,
                    mox + gx * cell + half,
                    moy + gy * cell + half,
                    super_r,
                    self._super_b,
                )

        n = min(len(self._mvb), len(work))
        self._mvb[:n] = work[:n]
        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr, self.win_ptr, self._img, 0, 0
        )

        # Lerp helper
        def lerp(p0: int, p1: int, t: float) -> float:
            return p0 + (p1 - p0) * t

        p_x = lerp(session.pacman.prev_x, session.pacman.x, pac_prog)
        p_y = lerp(session.pacman.prev_y, session.pacman.y, pac_prog)

        dx, dy = session.pacman.dir_x, session.pacman.dir_y
        d_str = "right"
        if dx == -1:
            d_str = "left"
        elif dy == -1:
            d_str = "up"
        elif dy == 1:
            d_str = "down"

        frame = int(time.time() * 10) % 3
        pac_sprite = self.sprites["pacman"][d_str][frame]["ptr"]
        draw_px = int(self.mox + p_x * self.cell)
        draw_py = int(self.moy + p_y * self.cell)
        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr, self.win_ptr, pac_sprite, draw_px, draw_py
        )

        # Draw Ghost Sprites
        for g in getattr(session, "ghosts", []):
            if g.state == EntityState.DEAD or not visible(g.x, g.y):
                continue

            g_x = lerp(g.prev_x, g.x, ghost_prog)
            g_y = lerp(g.prev_y, g.y, ghost_prog)

            sprite_name = (
                "powered"
                if g.state == EntityState.POWERED
                else self.ghost_mapping.get(g.color, "blinky")
            )
            ghost_sprite = self.sprites["ghosts"][sprite_name]["ptr" if sprite_name != "powered" else 0]

            draw_gx = int(self.mox + g_x * self.cell)
            draw_gy = int(self.moy + g_y * self.cell)
            self.mlx.mlx_put_image_to_window(
                self.mlx_ptr, self.win_ptr, ghost_sprite, draw_gx, draw_gy
            )

        # HUD dans la bande du haut (au-dessus du labyrinthe, rafraichi)
        hud = (
            f"Level: {getattr(session, 'level', 1)}   "
            f"Score: {session.score}   Lives: {session.lives}   "
            f"Gums: {len(session.pacgums)}   "
            f"Super: {len(session.super_pacgums)}   "
            f"Time: {session.time_left()}"
        )
        if session.powered:
            hud += f"   Power: {session.power_time_left()}"
        if shadow is not None:
            hud += f"   Light: {shadow.radius:.1f}"
            if shadow.shine_active():
                hud += f"   SHINE: {shadow.shine_time_left()}"
        self.mlx.mlx_string_put(
            self.mlx_ptr, self.win_ptr, self.mox, 18, HUD_COLOR, hud
        )
        self._flush()
