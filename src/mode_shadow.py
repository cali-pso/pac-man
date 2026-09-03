import math
import time

LIGHT_RADIUS_START: float = 3.5
LIGHT_RADIUS_MIN: float = 2.0
LIGHT_RADIUS_MAX: float = 8.0
PACGUM_LIGHT_GAIN: float = 0.5
DECAY_INTERVAL: float = 1
DECAY_STEP: float = 1.1
SHINE_DURATION: float = 8.0

class ShadowMode:
    def __init__(self) -> None:
        self.radius: float = LIGHT_RADIUS_START
        self._last_decay: float = time.time()
        self._shine_until: float = 0.0

    def update(self) -> None:
        now = time.time()
        while now - self._last_decay >= DECAY_INTERVAL:
            self._last_decay += DECAY_INTERVAL
            self.radius = max(LIGHT_RADIUS_MIN, self.radius - DECAY_STEP)

    def on_pacgum(self) -> None:
        self.radius = min(LIGHT_RADIUS_MAX, self.radius + PACGUM_LIGHT_GAIN)

    def on_shine(self) -> None:
        self._shine_until = time.time() + SHINE_DURATION

    def shine_active(self) -> bool:
        return time.time() < self._shine_until

    def shine_time_left(self) -> int:
        if not self.shine_activate():
            return 0
        return max(0, int(self._shine_until - time.time()))

    def is_visible(self, ex: int, ey: int, px: int, py: int) -> bool:
        if self.shine_active():
            return True
        return math.hypot(ex - px, ey - py) <= self.radius
