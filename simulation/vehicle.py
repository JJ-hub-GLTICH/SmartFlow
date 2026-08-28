from dataclasses import dataclass, field
import pygame

DIRECTION_VECTORS = {
    "NORTH": (0, 1), "SOUTH": (0, -1), "EAST": (-1, 0), "WEST": (1, 0)
}
COLORS = {
    "NORTH": (71, 181, 255), "SOUTH": (78, 222, 128),
    "EAST": (255, 193, 94), "WEST": (231, 107, 255),
    "EMERGENCY": (255, 255, 255),
}
VEHICLE_TYPES = {
    "car": (30, 16, 78.0),
    "truck": (40, 18, 68.0),
    "bus": (50, 18, 62.0),
    "emergency": (38, 16, 86.0),
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
        desired = max(0.0, min(self.target_speed or 75.0, desired_speed if desired_speed is not None else self.target_speed or 75.0))
        accel = 48.0 if desired > self.speed else 92.0
        if self.speed < desired:
            self.speed = min(desired, self.speed + accel * dt)
        else:
            self.speed = max(desired, self.speed - accel * dt)
        vx, vy = DIRECTION_VECTORS[self.direction]
        self.x += vx * self.speed * dt
        self.y += vy * self.speed * dt

    def offscreen(self, w: int, h: int) -> bool:
        return self.x < -90 or self.x > w + 90 or self.y < -90 or self.y > h + 90

    def draw(self, surface: pygame.Surface) -> None:
        horizontal = self.direction in ("EAST", "WEST")
        rect = pygame.Rect(0, 0, self.length if horizontal else self.width, self.width if horizontal else self.length)
        rect.center = (int(self.x), int(self.y))
        pygame.draw.rect(surface, self.color, rect, border_radius=5)
        if self.emergency:
            pygame.draw.rect(surface, (255, 58, 58), rect.inflate(-8, -6), border_radius=3)
            pygame.draw.rect(surface, (55, 130, 255), (rect.centerx-3, rect.y+3, 6, rect.h-6), border_radius=2)
        else:
            shine = pygame.Rect(rect.x + 4, rect.y + 3, max(5, rect.w // 3), max(4, rect.h - 6))
            pygame.draw.rect(surface, (235, 248, 255), shine, border_radius=3)
        wheel = (28, 32, 40)
        if horizontal:
            for ox in (5, rect.w - 9):
                pygame.draw.rect(surface, wheel, (rect.x + ox, rect.y - 2, 5, 4), border_radius=2)
                pygame.draw.rect(surface, wheel, (rect.x + ox, rect.bottom - 2, 5, 4), border_radius=2)
        else:
            for oy in (5, rect.h - 9):
                pygame.draw.rect(surface, wheel, (rect.x - 2, rect.y + oy, 4, 5), border_radius=2)
                pygame.draw.rect(surface, wheel, (rect.right - 2, rect.y + oy, 4, 5), border_radius=2)
