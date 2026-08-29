from dataclasses import dataclass, field
import pygame

DIRECTION_VECTORS = {
    "NORTH": (0, 1), "SOUTH": (0, -1), "EAST": (-1, 0), "WEST": (1, 0)
}
COLORS = {
    "NORTH": (65, 176, 246), "SOUTH": (79, 209, 127),
    "EAST": (245, 176, 82), "WEST": (203, 120, 244),
    "EMERGENCY": (245, 248, 255),
}
# Faster visual traffic so vehicles reach the junction early in a 15-second
# expo test, while keeping different vehicle types visibly distinct.
VEHICLE_TYPES = {
    "car": (34, 17, 108.0),
    "truck": (48, 19, 92.0),
    "bus": (58, 20, 84.0),
    "emergency": (42, 18, 118.0),
}

@dataclass
class Vehicle:
    direction: str
    x: float
    y: float
    spawn_time: float
    vehicle_type: str = "car"
    target_speed: float | None = None
    speed: float = 0.0
    waiting_time: float = 0.0
    stopped: bool = False
    cleared: bool = False
    emergency: bool = False
    length: int = field(init=False)
    width: int = field(init=False)
    color: tuple = field(init=False)

    def __post_init__(self) -> None:
        if self.emergency:
            self.vehicle_type = "emergency"
        self.length, self.width, default_speed = VEHICLE_TYPES.get(self.vehicle_type, VEHICLE_TYPES["car"])
        self.target_speed = self.target_speed or default_speed
        self.speed = min(self.speed, self.target_speed)
        self.color = COLORS["EMERGENCY"] if self.emergency else COLORS[self.direction]

    @property
    def half_length(self) -> float:
        return self.length / 2

    def distance_to_stop(self, stop_line: dict[str, float]) -> float:
        if self.direction == "NORTH": return stop_line["NORTH"] - (self.y + self.half_length)
        if self.direction == "SOUTH": return (self.y - self.half_length) - stop_line["SOUTH"]
        if self.direction == "EAST": return (self.x - self.half_length) - stop_line["EAST"]
        return stop_line["WEST"] - (self.x + self.half_length)

    def progress(self) -> float:
        if self.direction == "NORTH": return self.y
        if self.direction == "SOUTH": return -self.y
        if self.direction == "EAST": return -self.x
        return self.x

    def move(self, dt: float, desired_speed: float | None = None) -> None:
        desired = max(0.0, min(self.target_speed or 100.0, desired_speed if desired_speed is not None else self.target_speed or 100.0))
        accel = 78.0 if desired > self.speed else 125.0
        self.speed = min(desired, self.speed + accel * dt) if self.speed < desired else max(desired, self.speed - accel * dt)
        vx, vy = DIRECTION_VECTORS[self.direction]
        self.x += vx * self.speed * dt
        self.y += vy * self.speed * dt

    def offscreen(self, rect: pygame.Rect) -> bool:
        margin = 95
        if self.direction == "NORTH": return self.y > rect.bottom + margin
        if self.direction == "SOUTH": return self.y < rect.y - margin
        if self.direction == "EAST": return self.x < rect.x - margin
        return self.x > rect.right + margin

    def _oriented_points(self, rect: pygame.Rect):
        if self.direction == "NORTH":
            return [(rect.centerx, rect.bottom), (rect.x, rect.bottom-7), (rect.x, rect.y+7), (rect.centerx, rect.y), (rect.right, rect.y+7), (rect.right, rect.bottom-7)]
        if self.direction == "SOUTH":
            return [(rect.centerx, rect.y), (rect.right, rect.y+7), (rect.right, rect.bottom-7), (rect.centerx, rect.bottom), (rect.x, rect.bottom-7), (rect.x, rect.y+7)]
        if self.direction == "EAST":
            return [(rect.right, rect.centery), (rect.right-7, rect.y), (rect.x+7, rect.y), (rect.x, rect.centery), (rect.x+7, rect.bottom), (rect.right-7, rect.bottom)]
        return [(rect.x, rect.centery), (rect.x+7, rect.bottom), (rect.right-7, rect.bottom), (rect.right, rect.centery), (rect.right-7, rect.y), (rect.x+7, rect.y)]

    def draw(self, surface: pygame.Surface) -> None:
        horizontal = self.direction in ("EAST", "WEST")
        rect = pygame.Rect(0, 0, self.length if horizontal else self.width, self.width if horizontal else self.length)
        rect.center = (int(self.x), int(self.y))
        shadow = rect.move(3, 4)
        pygame.draw.rect(surface, (4, 8, 14, 95), shadow, border_radius=7)
        pygame.draw.polygon(surface, tuple(max(0, c-34) for c in self.color), self._oriented_points(rect.inflate(4, 4)))
        pygame.draw.polygon(surface, self.color, self._oriented_points(rect))
        pygame.draw.rect(surface, (255,255,255,55), rect.inflate(-8, -8), 1, border_radius=5)
        if horizontal:
            cabin = pygame.Rect(0, 0, max(11, rect.w//3), rect.h-6); cabin.centery = rect.centery
            cabin.centerx = rect.centerx + (-5 if self.direction == "EAST" else 5)
            lights = [(rect.x+2, rect.y+4), (rect.x+2, rect.bottom-7)] if self.direction == "WEST" else [(rect.right-5, rect.y+4), (rect.right-5, rect.bottom-7)]
            wheel_rects = [(rect.x+7, rect.y-3, 7, 5), (rect.right-15, rect.y-3, 7, 5), (rect.x+7, rect.bottom-2, 7, 5), (rect.right-15, rect.bottom-2, 7, 5)]
        else:
            cabin = pygame.Rect(0, 0, rect.w-6, max(11, rect.h//3)); cabin.centerx = rect.centerx
            cabin.centery = rect.centery + (-5 if self.direction == "NORTH" else 5)
            lights = [(rect.x+4, rect.bottom-5), (rect.right-7, rect.bottom-5)] if self.direction == "NORTH" else [(rect.x+4, rect.y+2), (rect.right-7, rect.y+2)]
            wheel_rects = [(rect.x-3, rect.y+8, 5, 7), (rect.x-3, rect.bottom-16, 5, 7), (rect.right-2, rect.y+8, 5, 7), (rect.right-2, rect.bottom-16, 5, 7)]
        pygame.draw.rect(surface, (28, 45, 62), cabin, border_radius=4)
        for wr in wheel_rects: pygame.draw.rect(surface, (13, 17, 24), wr, border_radius=2)
        for lx, ly in lights: pygame.draw.rect(surface, (255, 236, 150), (lx, ly, 4, 3), border_radius=1)
        if self.emergency:
            bar = pygame.Rect(0,0, 14 if horizontal else rect.w-5, 5 if horizontal else 14); bar.center = rect.center
            pygame.draw.rect(surface, (255, 58, 58), bar, border_radius=2)
            pygame.draw.circle(surface, (72, 160, 255), rect.center, 3)
