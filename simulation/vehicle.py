from dataclasses import dataclass, field
import pygame

DIRECTION_VECTORS = {
    "NORTH": (0, 1), "SOUTH": (0, -1), "EAST": (-1, 0), "WEST": (1, 0)
}
COLORS = {
    "NORTH": (71, 181, 255), "SOUTH": (78, 222, 128),
    "EAST": (255, 193, 94), "WEST": (231, 107, 255)
}

@dataclass
class Vehicle:
    direction: str
    x: float
    y: float
    spawn_time: float
    speed: float = 92.0
    waiting_time: float = 0.0
    stopped: bool = False
    cleared: bool = False
    length: int = 28
    width: int = 16
    color: tuple = field(init=False)

    def __post_init__(self) -> None:
        self.color = COLORS[self.direction]

    def distance_to_stop(self, stop_line: dict[str, float]) -> float:
        if self.direction == "NORTH": return stop_line["NORTH"] - self.y
        if self.direction == "SOUTH": return self.y - stop_line["SOUTH"]
        if self.direction == "EAST": return self.x - stop_line["EAST"]
        return stop_line["WEST"] - self.x

    def move(self, dt: float) -> None:
        vx, vy = DIRECTION_VECTORS[self.direction]
        self.x += vx * self.speed * dt
        self.y += vy * self.speed * dt

    def offscreen(self, w: int, h: int) -> bool:
        return self.x < -80 or self.x > w + 80 or self.y < -80 or self.y > h + 80

    def draw(self, surface: pygame.Surface) -> None:
        horizontal = self.direction in ("EAST", "WEST")
        rect = pygame.Rect(0, 0, self.length if horizontal else self.width, self.width if horizontal else self.length)
        rect.center = (int(self.x), int(self.y))
        pygame.draw.rect(surface, self.color, rect, border_radius=5)
        shine = pygame.Rect(rect.x + 4, rect.y + 3, max(5, rect.w // 3), max(4, rect.h - 6))
        pygame.draw.rect(surface, (235, 248, 255), shine, border_radius=3)
        # Wheels make vehicles read as cars rather than plain blocks.
        wheel = (28, 32, 40)
        if horizontal:
            for ox in (5, rect.w - 9):
                pygame.draw.rect(surface, wheel, (rect.x + ox, rect.y - 2, 5, 4), border_radius=2)
                pygame.draw.rect(surface, wheel, (rect.x + ox, rect.bottom - 2, 5, 4), border_radius=2)
        else:
            for oy in (5, rect.h - 9):
                pygame.draw.rect(surface, wheel, (rect.x - 2, rect.y + oy, 4, 5), border_radius=2)
                pygame.draw.rect(surface, wheel, (rect.right - 2, rect.y + oy, 4, 5), border_radius=2)
