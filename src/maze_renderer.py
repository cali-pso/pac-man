import struct
from typing import Optional

from src.game_session import GameSession
from src.maze_loader import Maze

WALL_COLOR: int = 0x5555FF
ENTRY_COLOR: int = 0xFFAA00
PAC_COLOR: int = 0xFFFF00
BG_COLOR: int = 0x000000
MARGIN: int = 40
THICK: int = 2


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
        self.ox = 0
        self.oy = 0
        self.size_line = 0
        self.bpp_bytes = 4
        self.endian = 0
        self._pac_b = b""

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

        avail_w = self.screen_w - 2 * MARGIN
        avail_h = self.screen_h - 2 * MARGIN
        cell = max(6, min(avail_w // cols, avail_h // rows))
        iw = cell * cols + THICK + 1
        ih = cell * rows + THICK + 1
        ox = (self.screen_w - cell * cols) // 2
        oy = (self.screen_h - cell * rows) // 2

        if self._img is not None:
            try:
                self.mlx.mlx_destroy_image(self.mlx_ptr, self._img)
            except Exception:
                pass

        img = self.mlx.mlx_new_image(self.mlx_ptr, iw, ih)
        data, bpp, size_line, endian = self.mlx.mlx_get_data_addr(img)
        bpp_bytes = bpp // 8

        wall_b = self._pack(WALL_COLOR, endian)
        entry_b = self._pack(ENTRY_COLOR, endian)
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
            buf[base:base + (x1 - x0) * bpp_bytes] = wall_b * (x1 - x0)

        def vline(x: int, y0: int, y1: int) -> None:
            if x < 0 or x >= iw:
                return
            y0 = max(0, y0)
            y1 = min(ih, y1)
            for yy in range(y0, y1):
                off = yy * size_line + x * bpp_bytes
                buf[off:off + bpp_bytes] = wall_b

        def hband(x0: int, x1: int, y: int) -> None:
            for t in range(THICK):
                hline(x0, x1, y + t)

        def vband(x: int, y0: int, y1: int) -> None:
            for t in range(THICK):
                vline(x + t, y0, y1)

        for y in range(rows):
            for x in range(cols):
                v = maze.cells[y][x]
                px = x * cell
                py = y * cell
                if v & Maze.WALL_N:
                    hband(px, px + cell, py)
                if v & Maze.WALL_W:
                    vband(px, py, py + cell)
                if x == cols - 1 and (v & Maze.WALL_E):
                    vband(px + cell, py, py + cell)
                if y == rows - 1 and (v & Maze.WALL_S):
                    hband(px, px + cell, py + cell)

        self._img = img
        self._mvb = data.cast("B")
        self._template = buf
        self.cell = cell
        self.iw = iw
        self.ih = ih
        self.ox = ox
        self.oy = oy
        self.size_line = size_line
        self.bpp_bytes = bpp_bytes
        self.endian = endian
        self._pac_b = self._pack(PAC_COLOR, endian)
        self._ready = True

    def render(self, session: GameSession) -> None:
        if not self._ready or self._template is None or self._mvb is None:
            return
        work = bytearray(self._template)

        cell = self.cell
        cx = session.pac_x * cell + cell // 2
        cy = session.pac_y * cell + cell // 2
        r = max(3, cell // 2 - 2)
        sl = self.size_line
        bb = self.bpp_bytes
        pac = self._pac_b
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
            work[base:base + (x1 - x0 + 1) * bb] = pac * (x1 - x0 + 1)

        n = min(len(self._mvb), len(work))
        self._mvb[:n] = work[:n]
        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr, self.win_ptr, self._img, self.ox, self.oy
        )
        self._flush()