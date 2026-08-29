from dataclasses import dataclass, field

@dataclass
class Metrics:
    cleared: int = 0
    total_wait: float = 0.0
    max_wait: float = 0.0
    signal_changes: int = 0
    final_avg_wait: float | None = None
    final_max_wait: float | None = None

    def record_clear(self, wait: float) -> None:
        self.cleared += 1
        self.total_wait += wait
        self.max_wait = max(self.max_wait, wait)

    def finalize(self, active_waits: list[float]) -> None:
        # At a short live simulation, many vehicles are still on the road when
        # the clock ends. Include their accumulated waiting time so the expo
        # result does not misleadingly show 0.0s just because nothing left the
        # screen yet.
        waits = [self.total_wait] if self.cleared else []
        count = self.cleared
        waits.extend(active_waits)
        count += len(active_waits)
        self.final_avg_wait = sum(waits) / count if count else 0.0
        self.final_max_wait = max([self.max_wait, *active_waits], default=0.0)

    @property
    def avg_wait(self) -> float:
        if self.final_avg_wait is not None:
            return self.final_avg_wait
        return self.total_wait / self.cleared if self.cleared else 0.0

    @property
    def display_max_wait(self) -> float:
        return self.final_max_wait if self.final_max_wait is not None else self.max_wait

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
