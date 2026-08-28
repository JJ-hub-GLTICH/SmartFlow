from dataclasses import dataclass

GREEN = "GREEN"
YELLOW = "YELLOW"
RED = "RED"

@dataclass
class TrafficSignal:
    direction: str
    state: str = RED
    green_elapsed: float = 0.0

    def set_state(self, state: str) -> None:
        if self.state != state:
            self.green_elapsed = 0.0
        self.state = state

    def update(self, dt: float) -> None:
        if self.state == GREEN:
            self.green_elapsed += dt
