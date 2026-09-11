import math
import time

LIGHT_RADIUS_START: float = 3.5
LIGHT_RADIUS_MIN: float = 2.0
LIGHT_RADIUS_MAX: float = 8.0
PACGUM_LIGHT_GAIN: float = 0.5
DECAY_INTERVAL: float = 1.0
DECAY_STEP: float = 1.1
SHINE_DURATION: float = 8.0


class ShadowMode:
    def __init__(
        self,
        radius_start: float = LIGHT_RADIUS_START,
        radius_min: float = LIGHT_RADIUS_MIN,
        radius_max: float = LIGHT_RADIUS_MAX,
        pacgum_gain: float = PACGUM_LIGHT_GAIN,
        decay_interval: float = DECAY_INTERVAL,
        decay_step: float = DECAY_STEP,
        shine_duration: float = SHINE_DURATION,
    ) -> None:
        self.radius: float = radius_start
        self.radius_min = radius_min
        self.radius_max = radius_max
        self.pacgum_gain = pacgum_gain
        self.decay_interval = max(0.1, decay_interval)
        self.decay_step = decay_step
        self.shine_duration = shine_duration
        self._last_decay: float = time.time()
        self._shine_until: float = 0.0

    def update(self) -> None:
        now = time.time()
        while now - self._last_decay >= self.decay_interval:
            self._last_decay += self.decay_interval
            self.radius = max(self.radius_min, self.radius - self.decay_step)

    def on_pacgum(self) -> None:
        self.radius = min(self.radius_max, self.radius + self.pacgum_gain)

    def on_shine(self) -> None:
        self._shine_until = time.time() + self.shine_duration

    def shine_active(self) -> bool:
        return time.time() < self._shine_until

    def shine_time_left(self) -> int:
        if not self.shine_active():
            return 0
        return max(0, int(self._shine_until - time.time()))

    def is_visible(self, ex: int, ey: int, px: int, py: int) -> bool:
        if self.shine_active():
            return True
        return math.hypot(ex - px, ey - py) <= self.radius
