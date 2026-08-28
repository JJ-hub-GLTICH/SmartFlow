from dataclasses import dataclass
from simulation.signal import GREEN

DIRECTIONS = ("NORTH", "EAST", "SOUTH", "WEST")

@dataclass
class OptimizerConfig:
    waiting_weight: float = 3.0
    total_weight: float = 1.2
    wait_time_weight: float = 0.18
    density_weight: float = 18.0
    starvation_weight: float = 0.35
    min_green: float = 7.0
    max_green: float = 24.0
    yellow_time: float = 2.5
    starvation_seconds: float = 34.0

@dataclass
class Decision:
    direction: str
    green_time: float
    scores: dict[str, float]
    reason: str

class SmartFlowOptimizer:
    """Deterministic adaptive signal selector.

    Score = waiting cars, total cars, accumulated waiting time, lane density,
    and a fairness bonus based on time since the road last had green.
    """
    def __init__(self, config: OptimizerConfig | None = None):
        self.config = config or OptimizerConfig()

    def choose(self, road_stats: dict, time_since_green: dict[str, float], current_green: str | None) -> Decision:
        scores: dict[str, float] = {}
        for direction in DIRECTIONS:
            stats = road_stats[direction]
            starvation_bonus = min(time_since_green.get(direction, 0), 60) * self.config.starvation_weight
            if time_since_green.get(direction, 0) >= self.config.starvation_seconds:
                starvation_bonus += 18.0
            score = (
                stats["waiting"] * self.config.waiting_weight
                + stats["total"] * self.config.total_weight
                + stats["avg_wait"] * self.config.wait_time_weight
                + stats["density"] * self.config.density_weight
                + starvation_bonus
            )
            if direction == current_green:
                score *= 0.75
            scores[direction] = round(score, 2)

        direction = max(DIRECTIONS, key=lambda d: (scores[d], time_since_green.get(d, 0), road_stats[d]["waiting"]))
        stats = road_stats[direction]
        pressure = stats["waiting"] + stats["density"] * 9 + min(stats["avg_wait"] / 4, 8)
        green_time = max(self.config.min_green, min(self.config.max_green, self.config.min_green + pressure * 0.9))
        reason = "Highest priority score from queue length, density, wait time, and fairness bonus"
        return Decision(direction, round(green_time, 1), scores, reason)

class TraditionalScheduler:
    def __init__(self, fixed_green: float = 12.0):
        self.fixed_green = fixed_green
        self.index = -1

    def next(self) -> Decision:
        self.index = (self.index + 1) % len(DIRECTIONS)
        direction = DIRECTIONS[self.index]
        return Decision(direction, self.fixed_green, {}, "Fixed-time rotation ignores live density")
