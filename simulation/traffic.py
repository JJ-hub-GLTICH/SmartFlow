from dataclasses import dataclass, field

@dataclass
class Metrics:
    cleared: int = 0
    total_wait: float = 0.0
    max_wait: float = 0.0
    signal_changes: int = 0

    def record_clear(self, wait: float) -> None:
        self.cleared += 1
        self.total_wait += wait
        self.max_wait = max(self.max_wait, wait)

    @property
    def avg_wait(self) -> float:
        return self.total_wait / self.cleared if self.cleared else 0.0

@dataclass
class RoadStats:
    total: int = 0
    waiting: int = 0
    density: float = 0.0
    avg_wait: float = 0.0
    signal: str = "RED"
    green_time: float = 0.0

    def as_dict(self) -> dict:
        return self.__dict__.copy()
